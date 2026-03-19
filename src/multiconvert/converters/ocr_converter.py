from __future__ import annotations

import html
import importlib.util
from pathlib import Path

from multiconvert.converters.base import BaseConverter
from multiconvert.errors import ConversionError
from multiconvert.formats import normalize_format
from multiconvert.utils import locate_executable


class OcrConverter(BaseConverter):
    name = "ocr"
    priority = 20

    _input_formats = {"pdf", "jpg", "png", "tif", "bmp"}
    _output_formats = {"txt", "md", "html", "docx"}

    def __init__(self) -> None:
        self._tesseract = locate_executable("tesseract", env_var="TESSERACT_CMD")

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
                "OCR dependencies are missing. Install pytesseract/Pillow and Tesseract OCR."
            )

        import pytesseract  # type: ignore

        pytesseract.pytesseract.tesseract_cmd = self._tesseract or "tesseract"
        lang = options.get("ocr_lang", "eng")

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
                raise ConversionError("python-docx is required for OCR -> DOCX conversion.")
            from docx import Document  # type: ignore

            doc = Document()
            for paragraph in text_blob.split("\n\n"):
                if paragraph.strip():
                    doc.add_paragraph(paragraph.strip())
            doc.save(destination)
            return

        raise ConversionError(f"OCR cannot export to target format: {target_format}")

    @staticmethod
    def _has_module(module_name: str) -> bool:
        return importlib.util.find_spec(module_name) is not None

    @staticmethod
    def _load_pages(source: Path, source_format: str, options: dict):
        from PIL import Image  # type: ignore

        if source_format == "pdf":
            if importlib.util.find_spec("pdf2image") is None:
                raise ConversionError("pdf2image is required for PDF OCR input.")
            from pdf2image import convert_from_path  # type: ignore

            dpi = int(options.get("ocr_dpi", 300))
            return convert_from_path(str(source), dpi=dpi)

        return [Image.open(source)]
