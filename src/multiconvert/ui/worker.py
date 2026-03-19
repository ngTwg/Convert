from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest


class ConvertWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)
    log = Signal(str)
    done = Signal()

    def __init__(self, manager: ConverterManager, request: ConversionRequest) -> None:
        super().__init__()
        self._manager = manager
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            result = self._manager.convert(self._request, logger=self.log.emit)
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001 - show all in UI log
            self.failed.emit(str(exc))
        finally:
            self.done.emit()
