from __future__ import annotations

import importlib.util
from pathlib import Path

from multiconvert.converters import BaseConverter, LibreOfficeConverter, OcrConverter, PandocConverter


def default_converters() -> list[BaseConverter]:
    return [PandocConverter(), LibreOfficeConverter(), OcrConverter()]


def load_external_plugins(plugin_dir: Path) -> list[BaseConverter]:
    converters: list[BaseConverter] = []
    if not plugin_dir.exists():
        return converters

    for plugin_file in sorted(plugin_dir.glob("*.py")):
        if plugin_file.name.startswith("_"):
            continue
        module_name = f"multiconvert_plugin_{plugin_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        if not spec or not spec.loader:
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        factory = getattr(module, "get_converter", None)
        if not callable(factory):
            continue

        instance = factory()
        if isinstance(instance, BaseConverter):
            converters.append(instance)

    return converters
