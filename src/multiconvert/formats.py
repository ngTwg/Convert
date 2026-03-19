from __future__ import annotations

from pathlib import Path

EXT_TO_FORMAT: dict[str, str] = {
    # Text formats
    ".md": "md",
    ".markdown": "md",
    ".txt": "txt",
    ".html": "html",
    ".htm": "html",
    ".rst": "rst",
    # Document formats
    ".docx": "docx",
    ".doc": "doc",
    ".odt": "odt",
    ".rtf": "rtf",
    ".epub": "epub",
    ".pdf": "pdf",
    ".pptx": "pptx",
    ".xlsx": "xlsx",
    ".csv": "csv",
    # LaTeX
    ".tex": "latex",
    ".latex": "latex",
    # Org-mode
    ".org": "org",
    # AsciiDoc
    ".adoc": "asciidoc",
    ".asciidoc": "asciidoc",
    # Wiki formats
    ".mediawiki": "mediawiki",
    ".wiki": "mediawiki",
    ".textile": "textile",
    # OPML (outlines)
    ".opml": "opml",
    # FictionBook
    ".fb2": "fb2",
    # Jupyter Notebook
    ".ipynb": "ipynb",
    # JSON
    ".json": "json",
    # Man pages
    ".man": "man",
    # txt2tags
    ".t2t": "t2t",
    # Jira/Confluence
    ".jira": "jira",
    # Image formats
    ".jpg": "jpg",
    ".jpeg": "jpg",
    ".png": "png",
    ".tif": "tif",
    ".tiff": "tif",
    ".bmp": "bmp",
    ".gif": "gif",
    ".webp": "webp",
    ".ico": "ico",
    ".svg": "svg",
    ".heic": "heic",
    ".heif": "heic",
}

FORMAT_ALIASES: dict[str, str] = {
    "markdown": "md",
    "htm": "html",
    "jpeg": "jpg",
    "tiff": "tif",
    "tex": "latex",
    "adoc": "asciidoc",
    "wiki": "mediawiki",
    "heif": "heic",
}

TEXT_EDITABLE_FORMATS: set[str] = {"md", "txt", "html", "rst", "latex", "org", "asciidoc", "textile", "json"}

DEFAULT_INTERMEDIATES: tuple[str, ...] = ("html", "odt", "docx", "md", "txt")


def normalize_format(fmt: str | None) -> str | None:
    if fmt is None:
        return None
    normalized = fmt.strip().lower().lstrip(".")
    return FORMAT_ALIASES.get(normalized, normalized)


def detect_format(path: str | Path) -> str | None:
    suffix = Path(path).suffix.lower()
    return EXT_TO_FORMAT.get(suffix)


def ensure_extension(path: str | Path, fmt: str) -> Path:
    target = Path(path)
    normalized = normalize_format(fmt) or fmt
    for ext, ext_fmt in EXT_TO_FORMAT.items():
        if ext_fmt == normalized:
            if target.suffix.lower() == ext:
                return target
            if target.suffix:
                return target.with_suffix(ext)
            return target.with_name(target.name + ext)
    return target
