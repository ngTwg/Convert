"""
MultiConvert – Premium Main Window
Dark slate + warm amber design language with drag & drop,
batch processing, progress bar, and inline status.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from multiconvert.formats import TEXT_EDITABLE_FORMATS, detect_format, ensure_extension
from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest, ConversionResult
from multiconvert.ui.worker import ConvertWorker


# ─── Unicode icons (no image files needed) ──────────────────────
ICON_FILE     = "📄"
ICON_FOLDER   = "📁"
ICON_CONVERT  = "⚡"
ICON_OPEN     = "🔓"
ICON_EDIT     = "✏️"
ICON_CHECK    = "✅"
ICON_WARN     = "⚠️"
ICON_ENGINE   = "⚙️"
ICON_DROP     = "📥"
ICON_BATCH    = "📚"
ICON_REMOVE   = "✕"


class DropZone(QFrame):
    """Drag-and-drop region that accepts file paths."""
    filesDropped = Signal(list)  # list[str]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel(ICON_DROP)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 36px; background: transparent; border: none; color: rgba(232,168,56,0.45);")
        layout.addWidget(icon)

        hint = QLabel("Drop files here  ·  or click Browse")
        hint.setObjectName("dropHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        sub = QLabel("Supports: DOCX  PDF  MD  HTML  EPUB  ODT  RTF  TXT  images …")
        sub.setObjectName("subtitleLabel")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dropActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event) -> None:
        self.setProperty("dropActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:
        self.setProperty("dropActive", False)
        self.style().unpolish(self)
        self.style().polish(self)
        paths = []
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local:
                paths.append(local)
        if paths:
            self.filesDropped.emit(paths)


class MainWindow(QMainWindow):
    """Premium dark-themed converter window."""

    def __init__(self, manager: ConverterManager) -> None:
        super().__init__()
        self._manager = manager
        self._thread: QThread | None = None
        self._worker: ConvertWorker | None = None
        self._last_result: ConversionResult | None = None
        self._batch_files: list[str] = []

        self.setWindowTitle("MultiConvert")
        self.resize(1100, 820)
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)

        self._build_ui()
        self._bind_events()
        self._detect_engines()

    # ═══════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 12)
        root.setSpacing(14)

        # ── Header ──
        header = QHBoxLayout()
        title = QLabel(f"{ICON_CONVERT}  MultiConvert")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        version_label = QLabel("v0.1.0")
        version_label.setObjectName("subtitleLabel")
        header.addWidget(version_label)
        root.addLayout(header)

        # ── Drop Zone ──
        self.drop_zone = DropZone()
        root.addWidget(self.drop_zone)

        # ── Input / Output Section ──
        io_group = QGroupBox(f"  {ICON_FILE}  Input / Output")
        io_layout = QVBoxLayout()
        io_layout.setSpacing(10)

        # Input row
        in_row = QHBoxLayout()
        lbl_in = QLabel("Source file")
        lbl_in.setMinimumWidth(80)
        in_row.addWidget(lbl_in)
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Select a file or drag-and-drop above…")
        in_row.addWidget(self.input_path)
        self.btn_input = QPushButton(f"{ICON_FOLDER}  Browse")
        self.btn_input.setMinimumWidth(100)
        in_row.addWidget(self.btn_input)
        io_layout.addLayout(in_row)

        # Format + Output row
        out_row = QHBoxLayout()
        lbl_fmt = QLabel("Convert to")
        lbl_fmt.setMinimumWidth(80)
        out_row.addWidget(lbl_fmt)
        self.target_combo = QComboBox()
        self.target_combo.addItems(sorted(self._manager.all_formats()))
        self.target_combo.setMinimumWidth(90)
        out_row.addWidget(self.target_combo)
        lbl_out = QLabel("Output")
        lbl_out.setMinimumWidth(50)
        out_row.addWidget(lbl_out)
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Auto-generated from input file name")
        out_row.addWidget(self.output_path)
        self.btn_output = QPushButton(f"{ICON_FOLDER}  Browse")
        self.btn_output.setMinimumWidth(100)
        out_row.addWidget(self.btn_output)
        io_layout.addLayout(out_row)

        io_group.setLayout(io_layout)
        root.addWidget(io_group)

        # ── Options Section ──
        opt_group = QGroupBox(f"  {ICON_ENGINE}  Options")
        opt_layout = QHBoxLayout()
        opt_layout.setSpacing(20)

        self.chk_open_after = QCheckBox("Open output after conversion")
        self.chk_open_after.setChecked(True)
        opt_layout.addWidget(self.chk_open_after)

        self.chk_ocr = QCheckBox("Force OCR (scanned PDF / images)")
        opt_layout.addWidget(self.chk_ocr)

        lbl_lang = QLabel("OCR lang")
        opt_layout.addWidget(lbl_lang)
        self.input_ocr_lang = QLineEdit("vie+eng")
        self.input_ocr_lang.setMaximumWidth(100)
        opt_layout.addWidget(self.input_ocr_lang)

        opt_layout.addStretch()
        opt_group.setLayout(opt_layout)
        root.addWidget(opt_group)

        # ── Batch list (hidden by default) ──
        self.batch_group = QGroupBox(f"  {ICON_BATCH}  Batch Queue")
        batch_layout = QVBoxLayout()
        self.batch_list = QListWidget()
        self.batch_list.setMaximumHeight(120)
        batch_layout.addWidget(self.batch_list)

        batch_btn_row = QHBoxLayout()
        self.btn_clear_batch = QPushButton(f"{ICON_REMOVE}  Clear list")
        self.btn_clear_batch.setObjectName("dangerBtn")
        batch_btn_row.addWidget(self.btn_clear_batch)
        batch_btn_row.addStretch()
        batch_layout.addLayout(batch_btn_row)

        self.batch_group.setLayout(batch_layout)
        self.batch_group.setVisible(False)
        root.addWidget(self.batch_group)

        # ── Action Buttons ──
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_convert = QPushButton(f"{ICON_CONVERT}  Convert")
        self.btn_convert.setObjectName("primaryBtn")
        self.btn_convert.setMinimumHeight(44)
        action_row.addWidget(self.btn_convert)

        self.btn_open = QPushButton(f"{ICON_OPEN}  Open Output")
        self.btn_open.setObjectName("successBtn")
        self.btn_open.setEnabled(False)
        action_row.addWidget(self.btn_open)

        self.btn_edit = QPushButton(f"{ICON_EDIT}  Edit in App")
        self.btn_edit.setEnabled(False)
        action_row.addWidget(self.btn_edit)

        root.addLayout(action_row)

        # ── Progress bar ──
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        # ── Log ──
        log_group = QGroupBox("  📋  Conversion Log")
        log_layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setObjectName("logBox")
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(160)
        log_layout.addWidget(self.log_box)
        log_group.setLayout(log_layout)
        root.addWidget(log_group)

        self.setCentralWidget(central)

        # ── Status bar ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.engine_status = QLabel()
        self.engine_status.setObjectName("statusLabel")
        self.status_bar.addPermanentWidget(self.engine_status)

    # ═══════════════════════════════════════════════════════
    #  EVENTS
    # ═══════════════════════════════════════════════════════

    def _bind_events(self) -> None:
        self.btn_input.clicked.connect(self._pick_input)
        self.btn_output.clicked.connect(self._pick_output)
        self.target_combo.currentTextChanged.connect(self._update_output_extension)
        self.btn_convert.clicked.connect(self._start_convert)
        self.btn_open.clicked.connect(self._open_output)
        self.btn_edit.clicked.connect(self._edit_output)
        self.drop_zone.filesDropped.connect(self._handle_dropped_files)
        self.btn_clear_batch.clicked.connect(self._clear_batch)

    # ═══════════════════════════════════════════════════════
    #  ENGINE DETECTION
    # ═══════════════════════════════════════════════════════

    def _detect_engines(self) -> None:
        active = self._manager.active_converters()
        names = [c.name for c in active]
        parts: list[str] = []
        for c in active:
            parts.append(f"{ICON_CHECK} {c.name}")
        missing = {"pandoc", "libreoffice", "ocr"} - set(names)
        for m in sorted(missing):
            parts.append(f"{ICON_WARN} {m} (not found)")

        self.engine_status.setText("  ·  ".join(parts))
        self.status_bar.showMessage(
            f"Ready — {len(active)} engine(s) active, "
            f"{len(self._manager.all_formats())} formats available"
        )

    # ═══════════════════════════════════════════════════════
    #  DRAG & DROP
    # ═══════════════════════════════════════════════════════

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self._handle_dropped_files(paths)

    def _handle_dropped_files(self, paths: list[str]) -> None:
        if len(paths) == 1:
            self.input_path.setText(paths[0])
            self._on_input_chosen(paths[0])
        else:
            # batch mode
            self._batch_files = paths
            self.batch_list.clear()
            for p in paths:
                item = QListWidgetItem(f"{ICON_FILE}  {Path(p).name}")
                item.setToolTip(p)
                self.batch_list.addItem(item)
            self.batch_group.setVisible(True)
            self.input_path.setText(f"{len(paths)} files selected (batch mode)")
            self._append_log(f"Batch: {len(paths)} files queued")

    def _clear_batch(self) -> None:
        self._batch_files.clear()
        self.batch_list.clear()
        self.batch_group.setVisible(False)
        self.input_path.clear()

    # ═══════════════════════════════════════════════════════
    #  FILE PICKERS
    # ═══════════════════════════════════════════════════════

    def _pick_input(self) -> None:
        selected, _ = QFileDialog.getOpenFileNames(self, "Choose source file(s)")
        if not selected:
            return
        if len(selected) == 1:
            self.input_path.setText(selected[0])
            self._on_input_chosen(selected[0])
        else:
            self._handle_dropped_files(selected)

    def _on_input_chosen(self, path: str) -> None:
        source_fmt = detect_format(path)
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
        if not src or "batch" in src.lower():
            return ""
        source = Path(src)
        target = self.target_combo.currentText().strip()
        return str(source.with_name(f"{source.stem}_converted.{target}"))

    def _update_output_extension(self) -> None:
        src = self.input_path.text().strip()
        target = self.target_combo.currentText().strip()
        if not src or not target or "batch" in src.lower():
            return
        source = Path(src)
        current = self.output_path.text().strip()
        if not current:
            self.output_path.setText(self._default_output_path())
            return
        updated = ensure_extension(current, target)
        self.output_path.setText(str(updated))

    # ═══════════════════════════════════════════════════════
    #  CONVERSION
    # ═══════════════════════════════════════════════════════

    def _start_convert(self) -> None:
        if self._batch_files:
            self._start_batch_convert()
            return

        src_text = self.input_path.text().strip()
        dst_text = self.output_path.text().strip()
        target_fmt = self.target_combo.currentText().strip()
        if not src_text or not target_fmt:
            QMessageBox.warning(self, "Missing input", "Please select source and target format.")
            return

        if not dst_text:
            dst_text = self._default_output_path()
            self.output_path.setText(dst_text)

        request = ConversionRequest(
            source=Path(src_text),
            destination=Path(dst_text),
            target_format=target_fmt,
            options=self._build_options(),
        )

        self._set_converting_state(True)
        self.log_box.clear()
        self._append_log(f"{ICON_CONVERT} Starting conversion…")
        self._append_log(f"   {Path(src_text).name}  →  .{target_fmt}")

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
        self._thread.finished.connect(lambda: self._set_converting_state(False))

        self._thread.start()

    def _start_batch_convert(self) -> None:
        target_fmt = self.target_combo.currentText().strip()
        if not target_fmt:
            QMessageBox.warning(self, "Missing format", "Select a target format.")
            return

        self._set_converting_state(True)
        self.log_box.clear()
        self._append_log(f"{ICON_BATCH} Batch converting {len(self._batch_files)} files to .{target_fmt}")

        total = len(self._batch_files)
        success = 0
        failed_list: list[str] = []

        for i, src_text in enumerate(self._batch_files, 1):
            src = Path(src_text)
            dst = src.with_name(f"{src.stem}_converted.{target_fmt}")
            self._append_log(f"\n[{i}/{total}] {src.name}")
            try:
                request = ConversionRequest(
                    source=src,
                    destination=dst,
                    target_format=target_fmt,
                    options=self._build_options(),
                )
                result = self._manager.convert(request, logger=self._append_log)
                self._append_log(f"   {ICON_CHECK} → {result.destination.name}")
                success += 1
            except Exception as exc:
                self._append_log(f"   {ICON_WARN} Failed: {exc}")
                failed_list.append(src.name)

        self._append_log(f"\n{'═'*50}")
        self._append_log(f"Batch complete: {success}/{total} succeeded")
        if failed_list:
            self._append_log(f"Failed: {', '.join(failed_list)}")

        self._set_converting_state(False)
        self.status_bar.showMessage(f"Batch done — {success}/{total} converted")

    def _build_options(self) -> dict:
        options: dict[str, object] = {}
        if self.chk_ocr.isChecked():
            options["force_ocr"] = True
            options["ocr_lang"] = self.input_ocr_lang.text().strip() or "eng"
        return options

    def _set_converting_state(self, converting: bool) -> None:
        self.btn_convert.setEnabled(not converting)
        self.btn_open.setEnabled(False)
        self.btn_edit.setEnabled(False)
        self.progress.setVisible(converting)
        if converting:
            self.status_bar.showMessage("Converting…")
        else:
            self.progress.setVisible(False)

    def _on_finished(self, result: ConversionResult) -> None:
        self._last_result = result
        self.output_path.setText(str(result.destination))
        self._append_log(f"\n{ICON_CHECK} Conversion completed!")
        if result.route:
            route_str = " → ".join(
                f"{step.source_format}→{step.target_format}" for step in result.route
            )
            self._append_log(f"   Route: {route_str}")

        self.btn_open.setEnabled(True)
        out_fmt = detect_format(result.destination)
        self.btn_edit.setEnabled(out_fmt in TEXT_EDITABLE_FORMATS)

        self.status_bar.showMessage(
            f"Done — Output: {result.destination.name} "
            f"({result.destination.stat().st_size / 1024:.1f} KB)"
        )

        if self.chk_open_after.isChecked():
            self._open_path(result.destination)

    def _on_failed(self, message: str) -> None:
        self._append_log(f"\n{ICON_WARN} Conversion failed!")
        self._append_log(f"   {message}")
        self.status_bar.showMessage("Conversion failed")
        QMessageBox.critical(self, "Conversion Failed", message)

    # ═══════════════════════════════════════════════════════
    #  POST-ACTIONS
    # ═══════════════════════════════════════════════════════

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

        from multiconvert.ui.editor_dialog import EditorDialog
        dialog = EditorDialog(self._manager, out_path, self)
        dialog.exec()

    def _append_log(self, text: str) -> None:
        self.log_box.append(text)
        # auto-scroll to bottom
        scrollbar = self.log_box.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    @staticmethod
    def _open_path(path: Path) -> None:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
            return
        subprocess.run(["xdg-open", str(path)], check=False)
