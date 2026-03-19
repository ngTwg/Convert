from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .formats import normalize_format


@dataclass(frozen=True)
class RouteStep:
    converter: str
    source_format: str
    target_format: str


@dataclass
class ConversionRequest:
    source: Path | str
    destination: Path | str
    source_format: str | None = None
    target_format: str | None = None
    options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.source = Path(self.source)
        self.destination = Path(self.destination)
        self.source_format = normalize_format(self.source_format)
        self.target_format = normalize_format(self.target_format)


@dataclass
class ConversionResult:
    destination: Path
    route: list[RouteStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
