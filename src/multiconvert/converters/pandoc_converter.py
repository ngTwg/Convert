from __future__ import annotations

from pathlib import Path

from multiconvert.converters.base import BaseConverter
from multiconvert.formats import normalize_format
from multiconvert.utils import locate_executable, run_command


class PandocConverter(BaseConverter):
    name = "pandoc"
    priority = 4

    _input_formats = {"md", "rst", "txt", "html", "docx", "odt", "rtf", "epub"}
    _output_formats = {"md", "txt", "html", "docx", "odt", "rtf", "epub", "pdf"}

    def __init__(self) -> None:
        self._pandoc = locate_executable(
            "pandoc",
            env_var="MULTICONVERT_PANDOC",
            portable_subpath="tools/pandoc/pandoc.exe",
        )

    def supported_pairs(self) -> set[tuple[str, str]]:
        pairs: set[tuple[str, str]] = set()
        for src in self._input_formats:
            for dst in self._output_formats:
                if src != dst:
                    pairs.add((src, dst))
        return pairs

    def available(self) -> bool:
        return self._pandoc is not None

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

        destination.parent.mkdir(parents=True, exist_ok=True)

        command = [
            self._pandoc or "pandoc",
            str(source),
            "-f",
            self._pandoc_format(source_format),
            "-t",
            self._pandoc_format(target_format),
            "-o",
            str(destination),
            "--resource-path",
            str(source.parent),
        ]

        if target_format == "pdf":
            pdf_engine = options.get("pdf_engine", "xelatex")
            command.append(f"--pdf-engine={pdf_engine}")
            template = options.get("pdf_template")
            if template:
                command.extend(["--template", str(template)])

        run_command(command)

    @staticmethod
    def _pandoc_format(fmt: str) -> str:
        if fmt == "md":
            return "markdown"
        return fmt
