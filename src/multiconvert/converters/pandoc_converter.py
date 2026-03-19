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

        temp_source = None
        temp_lua = None
        current_source = source

        # Fix encoding issues for text formats (Pandoc requires UTF-8)
        if source_format in {"md", "txt", "markdown", "csv", "html", "json"}:
            try:
                source.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = source.read_text(encoding="cp1258", errors="replace")
                import tempfile
                import os
                fd, path = tempfile.mkstemp(suffix=f".{source_format}")
                os.close(fd)
                temp_source = Path(path)
                temp_source.write_text(text, encoding="utf-8")
                current_source = temp_source

        command = [
            self._pandoc or "pandoc",
            str(current_source),
            "-f", self._pandoc_format(source_format, is_input=True),
            "-t", self._pandoc_format(target_format, is_input=False),
            "-o", str(destination),
            "--resource-path", str(source.parent),
        ]

        # Only use standalone for formats that need a complete document
        standalone_formats = {"html", "epub", "pdf", "latex", "docx", "odt", "rtf", "pptx"}
        if target_format in standalone_formats:
            command.append("--standalone")

        # Fix for abnormal bold/heading: use more restrictive markdown
        if source_format in {"md", "txt", "markdown"}:
            # Use gfm (GitHub Flavored Markdown) to integrate better Markdown logic like the requested VS Code extension
            command[command.index("-f") + 1] = "gfm"
            
            # Strip bold, italic, and heading sizes to make the text plain as requested
            lua_code = """
function Header(el)
    return pandoc.Para(el.content)
end
function Strong(el)
    return el.content
end
function Emph(el)
    return el.content
end
"""
            import tempfile
            import os
            fd, lua_path = tempfile.mkstemp(suffix=".lua")
            os.close(fd)
            Path(lua_path).write_text(lua_code, encoding="utf-8")
            temp_lua = Path(lua_path)
            command.append(f"--lua-filter={temp_lua}")

        # DOCX-specific: use reference doc style if available
        if target_format == "docx":
            command.extend(["--wrap", "preserve"])

        # HTML-specific: minimal output
        if target_format == "html":
            command.extend(["--wrap", "preserve"])

        # TXT output: use plain text
        if target_format == "txt":
            command[command.index("-t") + 1] = "plain"
            command.extend(["--wrap", "none"])

        if target_format == "pdf":
            # Pick available PDF engine - prefer xelatex for UTF-8/Vietnamese support
            for engine in ("xelatex", "lualatex", "pdflatex", "wkhtmltopdf"):
                if shutil.which(engine):
                    command.append(f"--pdf-engine={engine}")
                    # xelatex/lualatex handle UTF-8 natively with proper fonts
                    if engine in ("xelatex", "lualatex"):
                        # Use fonts with good Vietnamese character support
                        command.extend([
                            "-V", "mainfont=Times New Roman",
                            "-V", "sansfont=Arial",
                            "-V", "monofont=Consolas",
                            "-V", "mathfont=Cambria Math",
                            "-V", "CJKmainfont=Arial Unicode MS",
                        ])
                    break
            else:
                # Fallback to user-specified
                pdf_engine = options.get("pdf_engine", "xelatex")
                command.append(f"--pdf-engine={pdf_engine}")

            template = options.get("pdf_template")
            if template:
                command.extend(["--template", str(template)])

        try:
            run_command(command)
        finally:
            import os
            if temp_source and temp_source.exists():
                try:
                    os.unlink(temp_source)
                except OSError:
                    pass
            if temp_lua and temp_lua.exists():
                try:
                    os.unlink(temp_lua)
                except OSError:
                    pass

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
