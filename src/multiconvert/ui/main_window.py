from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from multiconvert.formats import TEXT_EDITABLE_FORMATS, detect_format, ensure_extension
from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest, ConversionResult
from multiconvert.ui.editor_dialog import EditorDialog
from multiconvert.ui.worker import ConvertWorker


class MainWindow(QMainWindow):
    def __init__(self, manager: ConverterManager) -> None:
        super().__init__()
        self._manager = manager
        self._thread: QThread | None = None
        self._worker: ConvertWorker | None = None
        self._last_result: ConversionResult | None = None

        self.setWindowTitle("MultiConvert - converter + editor")
        self.resize(1024, 760)

        self.input_path = QLineEdit()
        self.btn_input = QPushButton("Browse")

        self.target_combo = QComboBox()
        self.target_combo.addItems(sorted(self._manager.all_formats()))

        self.output_path = QLineEdit()
        self.btn_output = QPushButton("Browse")

        self.chk_open_after = QCheckBox("Open output file after conversion")
        self.chk_open_after.setChecked(True)

        self.chk_ocr = QCheckBox("Force OCR (for scanned PDF/images)")
        self.input_ocr_lang = QLineEdit("vie+eng")

        self.btn_convert = QPushButton("Convert")
        self.btn_open = QPushButton("Open output")
        self.btn_edit = QPushButton("Edit output in app")
        self.btn_open.setEnabled(False)
        self.btn_edit.setEnabled(False)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self._build_layout()
        self._bind_events()

    def _build_layout(self) -> None:
        root = QWidget()
        main = QVBoxLayout()

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Input"))
        input_row.addWidget(self.input_path)
        input_row.addWidget(self.btn_input)
        main.addLayout(input_row)

        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("To format"))
        output_row.addWidget(self.target_combo)
        output_row.addWidget(QLabel("Output"))
        output_row.addWidget(self.output_path)
        output_row.addWidget(self.btn_output)
        main.addLayout(output_row)

        ocr_row = QHBoxLayout()
        ocr_row.addWidget(self.chk_open_after)
        ocr_row.addWidget(self.chk_ocr)
        ocr_row.addWidget(QLabel("OCR lang"))
        ocr_row.addWidget(self.input_ocr_lang)
        main.addLayout(ocr_row)

        action_row = QHBoxLayout()
        action_row.addWidget(self.btn_convert)
        action_row.addWidget(self.btn_open)
        action_row.addWidget(self.btn_edit)
        main.addLayout(action_row)

        main.addWidget(QLabel("Logs"))
        main.addWidget(self.log_box)

        root.setLayout(main)
        self.setCentralWidget(root)

    def _bind_events(self) -> None:
        self.btn_input.clicked.connect(self._pick_input)
        self.btn_output.clicked.connect(self._pick_output)
        self.target_combo.currentTextChanged.connect(self._update_output_extension)
        self.btn_convert.clicked.connect(self._start_convert)
        self.btn_open.clicked.connect(self._open_output)
        self.btn_edit.clicked.connect(self._edit_output)

    def _pick_input(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Choose source file")
        if not selected:
            return
        self.input_path.setText(selected)
        source_fmt = detect_format(selected)
        if source_fmt:
            output_candidates = sorted(self._manager.output_formats_for(source_fmt))
            if output_candidates:
                self.target_combo.clear()
                self.target_combo.addItems(output_candidates)
                if "pdf" in output_candidates:
                    self.target_combo.setCurrentText("pdf")
        self._update_output_extension()

    def _pick_output(self) -> None:
        current = self.output_path.text().strip() or self._default_output_path()
        selected, _ = QFileDialog.getSaveFileName(self, "Output file", current)
        if selected:
            self.output_path.setText(selected)

    def _default_output_path(self) -> str:
        src = self.input_path.text().strip()
        if not src:
            return ""
        source = Path(src)
        target = self.target_combo.currentText().strip()
        return str(source.with_name(f"{source.stem}_converted.{target}"))

    def _update_output_extension(self) -> None:
        src = self.input_path.text().strip()
        target = self.target_combo.currentText().strip()
        if not src or not target:
            return
        source = Path(src)
        current = self.output_path.text().strip()
        if not current:
            self.output_path.setText(self._default_output_path())
            return
        updated = ensure_extension(current, target)
        self.output_path.setText(str(updated))

    def _start_convert(self) -> None:
        src_text = self.input_path.text().strip()
        dst_text = self.output_path.text().strip()
        target_fmt = self.target_combo.currentText().strip()
        if not src_text or not dst_text or not target_fmt:
            QMessageBox.warning(self, "Missing input", "Please select source and output.")
            return

        request = ConversionRequest(
            source=Path(src_text),
            destination=Path(dst_text),
            target_format=target_fmt,
            options=self._build_options(),
        )

        self.btn_convert.setEnabled(False)
        self.btn_open.setEnabled(False)
        self.btn_edit.setEnabled(False)
        self.log_box.clear()
        self._append_log("Starting conversion...")

        self._thread = QThread(self)
        self._worker = ConvertWorker(self._manager, request)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._append_log)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.done.connect(self._thread.quit)
        self._worker.done.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(lambda: self.btn_convert.setEnabled(True))

        self._thread.start()

    def _build_options(self) -> dict:
        options: dict[str, object] = {}
        if self.chk_ocr.isChecked():
            options["force_ocr"] = True
            options["ocr_lang"] = self.input_ocr_lang.text().strip() or "eng"
        return options

    def _on_finished(self, result: ConversionResult) -> None:
        self._last_result = result
        self.output_path.setText(str(result.destination))
        self._append_log("Conversion completed.")
        if result.route:
            for step in result.route:
                self._append_log(
                    f"  - {step.converter}: {step.source_format} -> {step.target_format}"
                )
        self.btn_open.setEnabled(True)

        out_fmt = detect_format(result.destination)
        self.btn_edit.setEnabled(out_fmt in TEXT_EDITABLE_FORMATS)

        if self.chk_open_after.isChecked():
            self._open_path(result.destination)

    def _on_failed(self, message: str) -> None:
        self._append_log("Conversion failed.")
        self._append_log(message)
        QMessageBox.critical(self, "Conversion failed", message)

    def _open_output(self) -> None:
        if not self._last_result:
            return
        self._open_path(self._last_result.destination)

    def _edit_output(self) -> None:
        if not self._last_result:
            return
        out_path = self._last_result.destination
        out_fmt = detect_format(out_path)
        if out_fmt not in TEXT_EDITABLE_FORMATS:
            QMessageBox.information(
                self,
                "Unsupported in-app edit",
                "In-app editor currently supports: md, txt, html, rst.",
            )
            return

        dialog = EditorDialog(self._manager, out_path, self)
        dialog.exec()

    def _append_log(self, text: str) -> None:
        self.log_box.append(text)

    @staticmethod
    def _open_path(path: Path) -> None:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
            return
        subprocess.run(["xdg-open", str(path)], check=False)
