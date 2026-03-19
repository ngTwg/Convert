from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from multiconvert.converters.base import BaseConverter
from multiconvert.errors import ConversionError
from multiconvert.formats import normalize_format
from multiconvert.utils import locate_executable, run_command


class LibreOfficeConverter(BaseConverter):
    name = "libreoffice"
    priority = 6

    _office_formats = {
        "doc",
        "docx",
        "odt",
        "rtf",
        "pptx",
        "xlsx",
        "html",
        "txt",
        "csv",
        "pdf",
    }
    _output_formats = {"pdf", "docx", "odt", "rtf", "html", "txt", "csv", "epub"}

    def __init__(self) -> None:
        self._soffice = (
            locate_executable(
                "soffice",
                env_var="MULTICONVERT_SOFFICE",
                portable_subpath="tools/libreoffice/program/soffice.exe",
            )
            or locate_executable("soffice.exe", env_var="MULTICONVERT_SOFFICE")
        )

    def supported_pairs(self) -> set[tuple[str, str]]:
        pairs: set[tuple[str, str]] = set()
        for src in self._office_formats:
            for dst in self._output_formats:
                if src != dst:
                    pairs.add((src, dst))
        return pairs

    def available(self) -> bool:
        return self._soffice is not None

    def convert(
        self,
        source: Path,
        destination: Path,
        source_format: str,
        target_format: str,
        options: dict,
    ) -> None:
        target_format = normalize_format(target_format) or target_format

        with tempfile.TemporaryDirectory(prefix="lo_convert_") as outdir_text:
            outdir = Path(outdir_text)
            command = [
                self._soffice or "soffice",
                "--headless",
                "--convert-to",
                self._filter_for(target_format),
                "--outdir",
                str(outdir),
                str(source),
            ]
            run_command(command)

            produced = self._find_output(outdir, source.stem, target_format)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(produced), str(destination))

    @staticmethod
    def _filter_for(target_format: str) -> str:
        mapping = {
            "txt": "txt:Text",
            "html": "html",
            "pdf": "pdf",
            "docx": "docx",
            "odt": "odt",
            "rtf": "rtf",
            "csv": "csv",
            "epub": "epub",
        }
        return mapping.get(target_format, target_format)

    @staticmethod
    def _find_output(outdir: Path, stem: str, target_format: str) -> Path:
        expected = normalize_format(target_format) or target_format
        candidates = sorted(outdir.glob(f"{stem}.*"))
        if not candidates:
            raise ConversionError("LibreOffice did not create any output file.")

        for candidate in candidates:
            if (normalize_format(candidate.suffix.lstrip(".")) or "") == expected:
                return candidate

        return candidates[0]
