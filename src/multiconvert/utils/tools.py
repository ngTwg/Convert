from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from multiconvert.errors import ConversionError

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Well-known system install locations (checked in order before $PATH)
_SOFFICE_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    r"/usr/bin/soffice",
    r"/usr/lib/libreoffice/program/soffice",
    r"/Applications/LibreOffice.app/Contents/MacOS/soffice",
]

_TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"/usr/bin/tesseract",
    r"/usr/local/bin/tesseract",
]

_PANDOC_CANDIDATES: list[str] = []   # pandoc usually on PATH or via pypandoc_binary


def locate_executable(
    name: str,
    *,
    env_var: str | None = None,
    portable_subpath: str | None = None,
    extra_candidates: list[str] | None = None,
) -> str | None:
    """Locate an external executable using multiple strategies."""

    # 1. Environment variable override
    if env_var:
        configured = os.environ.get(env_var)
        if configured and Path(configured).exists():
            return str(Path(configured))

    # 2. System PATH
    found = shutil.which(name)
    if found:
        return found

    # 3. Portable path bundled next to the .exe/project
    if portable_subpath:
        portable = PROJECT_ROOT / portable_subpath
        if portable.exists():
            return str(portable)

    # 4. Extra well-known paths (system installs outside PATH)
    for candidate in (extra_candidates or []):
        if Path(candidate).exists():
            return candidate

    return None


def locate_soffice() -> str | None:
    return locate_executable(
        "soffice",
        env_var="MULTICONVERT_SOFFICE",
        portable_subpath="tools/libreoffice/program/soffice.exe",
        extra_candidates=_SOFFICE_CANDIDATES,
    ) or locate_executable(
        "soffice.exe",
        env_var="MULTICONVERT_SOFFICE",
    )


def locate_tesseract() -> str | None:
    return locate_executable(
        "tesseract",
        env_var="TESSERACT_CMD",
        portable_subpath="tools/tesseract/tesseract.exe",
        extra_candidates=_TESSERACT_CANDIDATES,
    )


def locate_poppler_bindir() -> str | None:
    """Return the directory containing pdftoppm (Poppler bin/)."""
    # 1. Env var pointing to the bin dir
    env = os.environ.get("MULTICONVERT_POPPLER_PATH")
    if env and Path(env, "pdftoppm.exe").exists():
        return env
    if env and Path(env, "pdftoppm").exists():
        return env

    # 2. Bundled tools/poppler/bin
    portable = PROJECT_ROOT / "tools" / "poppler" / "bin"
    if (portable / "pdftoppm.exe").exists() or (portable / "pdftoppm").exists():
        return str(portable)

    # 3. On PATH
    found = shutil.which("pdftoppm")
    if found:
        return str(Path(found).parent)

    return None


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 1800,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        detail = stderr or stdout or "Unknown converter error."
        raise ConversionError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n{detail}"
        )
    return completed
