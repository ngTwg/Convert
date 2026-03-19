from __future__ import annotations

from pathlib import Path

EXT_TO_FORMAT: dict[str, str] = {
    ".md": "md",
    ".markdown": "md",
    ".txt": "txt",
    ".html": "html",
    ".htm": "html",
    ".rst": "rst",
    ".docx": "docx",
    ".doc": "doc",
    ".odt": "odt",
    ".rtf": "rtf",
    ".epub": "epub",
    ".pdf": "pdf",
    ".pptx": "pptx",
    ".xlsx": "xlsx",
    ".csv": "csv",
    ".jpg": "jpg",
    ".jpeg": "jpg",
    ".png": "png",
    ".tif": "tif",
    ".tiff": "tif",
    ".bmp": "bmp",
    ".gif": "gif",
    ".webp": "webp",
}

FORMAT_ALIASES: dict[str, str] = {
    "markdown": "md",
    "htm": "html",
    "jpeg": "jpg",
    "tiff": "tif",
}

TEXT_EDITABLE_FORMATS: set[str] = {"md", "txt", "html", "rst"}

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
