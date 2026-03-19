from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from multiconvert.errors import ConversionError

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def locate_executable(
    name: str,
    *,
    env_var: str | None = None,
    portable_subpath: str | None = None,
) -> str | None:
    if env_var:
        configured = os.environ.get(env_var)
        if configured and Path(configured).exists():
            return str(Path(configured))

    found = shutil.which(name)
    if found:
        return found

    if portable_subpath:
        portable = PROJECT_ROOT / portable_subpath
        if portable.exists():
            return str(portable)

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
