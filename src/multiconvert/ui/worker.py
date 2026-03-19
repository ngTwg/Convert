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


class BatchConvertWorker(QObject):
    batch_finished = Signal(int, int, list)  # success_count, total_count, failed_files
    log = Signal(str)
    done = Signal()
    progress = Signal(int, int)  # current, total

    def __init__(self, manager: ConverterManager, requests: list[ConversionRequest]) -> None:
        super().__init__()
        self._manager = manager
        self._requests = requests

    @Slot()
    def run(self) -> None:
        total = len(self._requests)
        success = 0
        failed_list = []

        for i, request in enumerate(self._requests, 1):
            self.log.emit(f"\n[{i}/{total}] {request.source.name}")
            try:
                result = self._manager.convert(request, logger=self.log.emit)
                self.log.emit(f"   ✅ → {result.destination.name}")
                success += 1
            except Exception as exc:
                self.log.emit(f"   ⚠️ Lỗi: {exc}")
                failed_list.append(request.source.name)
            self.progress.emit(i, total)

        self.batch_finished.emit(success, total, failed_list)
        self.done.emit()

