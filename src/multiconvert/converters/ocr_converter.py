from __future__ import annotations

import html
import importlib.util
import os
import sys
from pathlib import Path

from multiconvert.converters.base import BaseConverter
from multiconvert.errors import ConversionError
from multiconvert.formats import normalize_format
from multiconvert.utils import locate_tesseract, locate_poppler_bindir


def _get_tessdata_dir() -> str | None:
    """Find tessdata directory: bundled (PyInstaller) or system install."""
    # PyInstaller bundle
    if hasattr(sys, "_MEIPASS"):
        bundled = Path(sys._MEIPASS) / "tessdata"  # type: ignore[attr-defined]
        if bundled.exists():
            return str(bundled)
    # Next to exe (onedir mode)
    exe_dir = Path(sys.executable).parent
    candidate = exe_dir / "_internal" / "tessdata"
    if candidate.exists():
        return str(candidate)
    # System Tesseract
    for p in [
        r"C:\Program Files\Tesseract-OCR\tessdata",
        r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
        "/usr/share/tesseract-ocr/4.00/tessdata",
        "/usr/share/tessdata",
    ]:
        if Path(p).exists():
            return p
    return None


class OcrConverter(BaseConverter):
    """Extract text from scanned PDFs and images using Tesseract OCR.

    Input: pdf (scanned), jpg, jpeg, png, tif, tiff, bmp, gif, webp, ico, heic
    Output: txt, md, html, docx
    """

    name = "ocr"
    priority = 20

    _input_formats = {"pdf", "jpg", "png", "tif", "bmp", "gif", "webp", "ico", "heic"}
    _output_formats = {"txt", "md", "html", "docx"}

    def __init__(self) -> None:
        self._tesseract = locate_tesseract()
        self._poppler_path = locate_poppler_bindir()

    def supported_pairs(self) -> set[tuple[str, str]]:
        pairs: set[tuple[str, str]] = set()
        for src in self._input_formats:
            for dst in self._output_formats:
                if src != dst:
                    pairs.add((src, dst))
        return pairs

    def available(self) -> bool:
        modules_ok = self._has_module("pytesseract") and self._has_module("PIL")
        return bool(self._tesseract and modules_ok)

    def convert(
        self,
        source: Path,
        destination: Path,
        source_format: str,
        target_format: str,
        options: dict,
    ) -> None:
        source_format = normalize_format(source_format) or source_format
        target_format = normalize_format(target_format) or target_format

        if not self.available():
            raise ConversionError(
                "OCR dependencies missing. Tesseract must be installed."
            )

        import pytesseract  # type: ignore

        pytesseract.pytesseract.tesseract_cmd = self._tesseract or "tesseract"
        lang = str(options.get("ocr_lang", "eng"))

        # Set tessdata directory for bundled exe
        tessdata_dir = _get_tessdata_dir()
        if tessdata_dir:
            os.environ["TESSDATA_PREFIX"] = tessdata_dir

        # Validate lang codes (tesseract will error on unknown langs)
        available_langs = self._available_langs()
        requested = [l.strip() for l in lang.split("+")]
        valid = [l for l in requested if l in available_langs or l == "osd"]
        if not valid:
            valid = ["eng"]
        lang = "+".join(valid)

        pages = self._load_pages(source, source_format, options)
        text_parts: list[str] = []
        for page in pages:
            text = pytesseract.image_to_string(page, lang=lang)
            text_parts.append(text.strip())

        text_blob = "\n\n".join([chunk for chunk in text_parts if chunk]).strip()
        destination.parent.mkdir(parents=True, exist_ok=True)

        if target_format in {"txt", "md"}:
            destination.write_text(text_blob, encoding="utf-8")
            return

        if target_format == "html":
            paragraphs = "</p><p>".join(
                html.escape(paragraph) for paragraph in text_blob.split("\n\n") if paragraph.strip()
            )
            document = f"<html><body><p>{paragraphs}</p></body></html>"
            destination.write_text(document, encoding="utf-8")
            return

        if target_format == "docx":
            if not self._has_module("docx"):
                raise ConversionError("python-docx is required for OCR → DOCX conversion.")
            from docx import Document  # type: ignore

            doc = Document()
            for paragraph in text_blob.split("\n\n"):
                if paragraph.strip():
                    doc.add_paragraph(paragraph.strip())
            doc.save(destination)
            return

        raise ConversionError(f"OCR cannot export to target format: {target_format}")

    def _available_langs(self) -> set[str]:
        """Get languages available in the tessdata directory."""
        try:
            import pytesseract  # type: ignore
            pytesseract.pytesseract.tesseract_cmd = self._tesseract or "tesseract"
            langs_str = pytesseract.get_languages()
            return set(langs_str) if isinstance(langs_str, list) else set()
        except Exception:
            return {"eng"}

    @staticmethod
    def _has_module(module_name: str) -> bool:
        return importlib.util.find_spec(module_name) is not None

    def _load_pages(self, source: Path, source_format: str, options: dict):
        from PIL import Image  # type: ignore

        if source_format == "pdf":
            if importlib.util.find_spec("pdf2image") is None:
                raise ConversionError("pdf2image is required for PDF OCR input.")
            from pdf2image import convert_from_path  # type: ignore

            dpi = int(options.get("ocr_dpi", 300))
            kwargs: dict = {"dpi": dpi}
            # Supply poppler_path if we found it
            if self._poppler_path:
                kwargs["poppler_path"] = self._poppler_path
            return convert_from_path(str(source), **kwargs)

        return [Image.open(source)]
