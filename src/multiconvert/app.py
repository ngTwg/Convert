from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest
from multiconvert.plugin_loader import default_converters, load_external_plugins


def build_manager(plugin_dir: Path | None = None) -> ConverterManager:
    converters = default_converters()
    if plugin_dir:
        converters.extend(load_external_plugins(plugin_dir))
    return ConverterManager(converters)


def _open_file(path: Path) -> None:
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    subprocess.run(["xdg-open", str(path)], check=False)


def run_cli(args: argparse.Namespace) -> int:
    manager = build_manager(Path(args.plugin_dir) if args.plugin_dir else None)

    if args.list_formats:
        formats = sorted(manager.all_formats())
        print("Available formats:", ", ".join(formats))
        active = [converter.name for converter in manager.active_converters()]
        print("Active converters:", ", ".join(active) if active else "(none)")
        return 0

    if not args.input or not args.to:
        print("Missing required CLI arguments. Use --gui or provide --input + --to.")
        return 2

    source = Path(args.input).expanduser().resolve()
    if not source.exists():
        print(f"Input file not found: {source}")
        return 2

    destination = (
        Path(args.output).expanduser().resolve()
        if args.output
        else source.with_name(f"{source.stem}_converted.{args.to}")
    )

    options: dict[str, object] = {}
    if args.ocr:
        options["force_ocr"] = True
        options["ocr_lang"] = args.ocr_lang

    request = ConversionRequest(
        source=source,
        destination=destination,
        target_format=args.to,
        options=options,
    )

    def _log(message: str) -> None:
        print(message)

    try:
        result = manager.convert(request, logger=_log)
    except Exception as exc:  # noqa: BLE001
        print(f"Conversion failed: {exc}")
        return 1

    print(f"Success: {result.destination}")
    if args.open:
        _open_file(result.destination)
    return 0


def run_gui(plugin_dir: Path | None = None) -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:  # pragma: no cover - depends on local env
        print("PySide6 is required for GUI mode. Install with: pip install PySide6")
        print(exc)
        return 2

    from multiconvert.ui.main_window import MainWindow
    from multiconvert.ui.theme import DARK_THEME_QSS

    app = QApplication(sys.argv)

    # apply premium dark theme
    app.setStyleSheet(DARK_THEME_QSS)

    manager = build_manager(plugin_dir)
    window = MainWindow(manager)
    window.show()
    return app.exec()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="multiconvert",
        description="Multi-format converter with plugin routing and optional GUI editor.",
    )
    parser.add_argument("--gui", action="store_true", help="Launch desktop GUI.")
    parser.add_argument("--input", help="Input file path.")
    parser.add_argument("--to", help="Target format (example: pdf, docx, md).")
    parser.add_argument("--output", help="Output file path.")
    parser.add_argument("--open", action="store_true", help="Open output after conversion.")
    parser.add_argument("--ocr", action="store_true", help="Enable OCR options.")
    parser.add_argument("--ocr-lang", default="eng", help="OCR language pack, ex: vie+eng.")
    parser.add_argument(
        "--plugin-dir",
        help="Directory containing external converter plugins (*.py).",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="Print available formats from active converters.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    plugin_dir = Path(args.plugin_dir) if args.plugin_dir else None

    if args.gui or (not args.input and not args.list_formats):
        return run_gui(plugin_dir)
    return run_cli(args)
