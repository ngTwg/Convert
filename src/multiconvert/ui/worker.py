from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest


class ConvertWorker(QObject):
    """Worker for single file conversion."""
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
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.done.emit()


class BatchConvertWorker(QObject):
    """Worker for batch file conversion with per-file progress."""
    batch_finished = Signal(int, int, list)  # success_count, total_count, failed_files
    log = Signal(str)
    done = Signal()
    progress = Signal(int, int)  # current, total

    # Per-file signals
    file_progress = Signal(str, int)  # file_path, progress (0-100)
    file_complete = Signal(str, str)  # source_path, output_path
    file_error = Signal(str, str)     # file_path, error_message

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
            source_path = str(request.source)

            try:
                # Emit start
                self.file_progress.emit(source_path, 10)

                # Convert
                result = self._manager.convert(request, logger=self.log.emit)

                # Emit complete - MUST use str for output path
                output_path = str(result.destination)
                self.file_progress.emit(source_path, 100)
                self.file_complete.emit(source_path, output_path)
                success += 1

            except Exception as exc:
                error_msg = str(exc)
                self.file_error.emit(source_path, error_msg)
                failed_list.append(request.source.name)

            # Emit overall progress
            self.progress.emit(i, total)

        # IMPORTANT: Emit batch_finished BEFORE done
        self.batch_finished.emit(success, total, failed_list)
        self.done.emit()
