from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from multiconvert.formats import normalize_format


class BaseConverter(ABC):
    name: str = "base"
    priority: int = 10

    @abstractmethod
    def supported_pairs(self) -> set[tuple[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def convert(
        self,
        source: Path,
        destination: Path,
        source_format: str,
        target_format: str,
        options: dict,
    ) -> None:
        raise NotImplementedError

    def can_convert(self, source_format: str, target_format: str) -> bool:
        src = normalize_format(source_format)
        dst = normalize_format(target_format)
        if not src or not dst:
            return False
        return (src, dst) in self.supported_pairs()
