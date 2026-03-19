from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

from multiconvert.converters.base import BaseConverter
from multiconvert.formats import normalize_format
from multiconvert.utils import locate_executable, run_command


def _has_latex() -> bool:
    """Check if xelatex/pdflatex is available for Pandoc PDF output."""
    return bool(shutil.which("xelatex") or shutil.which("pdflatex") or shutil.which("lualatex"))


class PandocConverter(BaseConverter):
    """Text/ebook conversion using Pandoc.

    Input formats:  md, rst, txt, html, docx, odt, rtf, epub, latex, org,
                    asciidoc, mediawiki, textile, opml, fb2, ipynb, json,
                    man, t2t, twiki, tikiwiki, jira, csv
    Output formats: md, txt, html, docx, odt, rtf, epub, latex, org,
                    asciidoc, mediawiki, textile, opml, fb2, ipynb, json,
                    man, pptx, revealjs, dzslides, slideous, slidy, s5
    + pdf  (only when xelatex/pdflatex is installed)

    NOTE: For DOCX→PDF without LaTeX, LibreOffice is preferred.
    """

    name = "pandoc"
    priority = 4   # lower = preferred; LibreOffice=6 so Pandoc is tried first for text formats

    _input_formats = {
        # Text formats
        "md", "rst", "txt", "html",
        # Document formats
        "docx", "odt", "rtf", "epub",
        # Markup formats
        "latex", "tex", "org", "asciidoc", "adoc",
        "mediawiki", "textile", "opml", "fb2",
        # Data/Code formats
        "ipynb", "json",
        # Other wiki/markup formats
        "man", "t2t", "twiki", "tikiwiki", "jira", "csv",
    }
    # pdf excluded by default; added dynamically only when LaTeX is present
    _output_formats_base = {
        # Text formats
        "md", "txt", "html",
        # Document formats
        "docx", "odt", "rtf", "epub",
        # Markup formats
        "latex", "org", "asciidoc", "mediawiki", "textile", "opml", "fb2",
        # Data/Code formats
        "ipynb", "json",
        # Presentation formats
        "pptx", "revealjs", "dzslides", "slideous", "slidy", "s5",
        # Other
        "man",
    }

    def __init__(self) -> None:
        self._pandoc = locate_executable(
            "pandoc",
            env_var="MULTICONVERT_PANDOC",
            portable_subpath="tools/pandoc/pandoc.exe",
        )
        # Fallback: use pypandoc_binary bundled pandoc
        if not self._pandoc:
            try:
                import pypandoc
                bundled = pypandoc.get_pandoc_path()
                if bundled:
                    self._pandoc = str(bundled)
            except Exception:
                pass

        self._has_latex = _has_latex()

    def _output_formats(self) -> set[str]:
        fmts = set(self._output_formats_base)
        if self._has_latex:
            fmts.add("pdf")
        return fmts

    def supported_pairs(self) -> set[tuple[str, str]]:
        pairs: set[tuple[str, str]] = set()
        for src in self._input_formats:
            for dst in self._output_formats():
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
            "-f", self._pandoc_format(source_format, is_input=True),
            "-t", self._pandoc_format(target_format, is_input=False),
            "-o", str(destination),
            "--resource-path", str(source.parent),
        ]

        # Only use standalone for formats that need a complete document
        standalone_formats = {"html", "epub", "pdf", "latex", "docx", "odt", "rtf", "pptx"}
        if target_format in standalone_formats:
            command.append("--standalone")

        # Fix for abnormal bold text: use proper markdown extensions
        if source_format in {"md", "txt", "markdown"}:
            # Disable extensions that might cause unexpected bold
            command[command.index("-f") + 1] = "markdown-smart-auto_identifiers"

        # DOCX-specific: wrap text properly
        if target_format == "docx":
            command.extend(["--wrap", "auto"])

        # HTML-specific: use clean output
        if target_format == "html":
            command.extend(["--wrap", "none"])

        if target_format == "pdf":
            # Pick available PDF engine
            for engine in ("xelatex", "pdflatex", "lualatex", "wkhtmltopdf"):
                if shutil.which(engine):
                    command.append(f"--pdf-engine={engine}")
                    break
            else:
                # Fallback to user-specified
                pdf_engine = options.get("pdf_engine", "xelatex")
                command.append(f"--pdf-engine={pdf_engine}")

            template = options.get("pdf_template")
            if template:
                command.extend(["--template", str(template)])

        run_command(command)

    @staticmethod
    def _pandoc_format(fmt: str, is_input: bool = False) -> str:
        if fmt == "txt":
            return "markdown" if is_input else "plain"
        mapping = {
            "md": "markdown",
            "tex": "latex",
            "adoc": "asciidoc",
        }
        return mapping.get(fmt, fmt)
