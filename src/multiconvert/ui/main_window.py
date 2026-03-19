"""
MultiConvert – Clean Main Window
Minimalist design with file progress bars, dependency checks, and onboarding.
"""
from __future__ import annotations

import importlib.metadata
import os
import subprocess
from pathlib import Path

from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QThread, Signal, QTimer,
    QSettings, QSize
)
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QSpacerItem,
)

from multiconvert.formats import TEXT_EDITABLE_FORMATS, detect_format, ensure_extension
from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest, ConversionResult
from multiconvert.ui.worker import ConvertWorker

APP_COPYRIGHT = "Le Ngoc Tuong - HCMUS"


def app_version() -> str:
    try:
        return importlib.metadata.version("multiconvert")
    except importlib.metadata.PackageNotFoundError:
        return "0.2.0"


# ═══════════════════════════════════════════════════════════
#  FILE ITEM WIDGET - Individual progress per file
# ═══════════════════════════════════════════════════════════

class FileItemWidget(QWidget):
    """Widget showing a single file with its conversion progress."""
    removeClicked = Signal(str)

    def __init__(self, file_path: str, parent=None) -> None:
        super().__init__(parent)
        self.file_path = file_path
        self.setObjectName("fileItemWidget")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Top row: filename + remove button
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.name_label = QLabel(Path(self.file_path).name)
        self.name_label.setStyleSheet("color: #E0E0E0; font-size: 12px; font-weight: 500;")
        top_row.addWidget(self.name_label)

        # Format badge
        fmt = detect_format(self.file_path) or "?"
        self.format_label = QLabel(fmt.upper())
        self.format_label.setStyleSheet(
            "color: #888888; font-size: 10px; padding: 2px 6px; "
            "border: 1px solid #444444; border-radius: 3px;"
        )
        top_row.addWidget(self.format_label)

        top_row.addStretch()

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666666; font-size: 11px;")
        top_row.addWidget(self.status_label)

        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(20, 20)
        self.remove_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #666666; font-size: 16px; }"
            "QPushButton:hover { color: #F44336; }"
        )
        self.remove_btn.clicked.connect(lambda: self.removeClicked.emit(self.file_path))
        top_row.addWidget(self.remove_btn)

        layout.addLayout(top_row)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setObjectName("fileProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

    def set_progress(self, value: int) -> None:
        """Update progress (0-100)."""
        self.progress.setVisible(True)
        self.progress.setValue(value)
        self.status_label.setText(f"{value}%")
        self.status_label.setStyleSheet("color: #4A9EFF; font-size: 11px;")

    def set_converting(self) -> None:
        """Mark as currently converting."""
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Converting...")
        self.status_label.setStyleSheet("color: #4A9EFF; font-size: 11px;")
        self.remove_btn.setEnabled(False)

    def set_complete(self) -> None:
        """Mark as completed successfully."""
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.status_label.setText("Done")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: 600;")
        self.setObjectName("fileItemComplete")
        self.setStyleSheet("QWidget#fileItemComplete { border: 1px solid #4CAF50; }")

    def set_error(self, message: str = "Failed") -> None:
        """Mark as failed."""
        self.progress.setVisible(False)
        self.status_label.setText("Error")
        self.status_label.setStyleSheet("color: #F44336; font-size: 11px; font-weight: 600;")
        self.status_label.setToolTip(message)
        self.setObjectName("fileItemError")
        self.setStyleSheet("QWidget#fileItemError { border: 1px solid #F44336; }")


# ═══════════════════════════════════════════════════════════
#  DROP ZONE
# ═══════════════════════════════════════════════════════════

class DropZone(QFrame):
    """Clean drag-and-drop region."""
    filesDropped = Signal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        # Simple icon (text-based)
        icon = QLabel("+")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "font-size: 32px; font-weight: 300; color: #444444; background: transparent; border: none;"
        )
        layout.addWidget(icon)

        hint = QLabel("Drop files here or click Browse")
        hint.setObjectName("dropHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        sub = QLabel("Supports: PDF, DOCX, MD, HTML, EPUB, Images, and 30+ more formats")
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
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self.filesDropped.emit(paths)


# ═══════════════════════════════════════════════════════════
#  WELCOME DIALOG - Onboarding & Help
# ═══════════════════════════════════════════════════════════

class WelcomeDialog(QDialog):
    """Onboarding dialog shown on first run."""

    def __init__(self, manager: ConverterManager, parent=None) -> None:
        super().__init__(parent)
        self._manager = manager
        self.setWindowTitle("Welcome to MultiConvert")
        self.setFixedSize(500, 450)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(20)

        # Title
        title = QLabel("MultiConvert")
        title.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: 700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(f"Version {app_version()} - 35+ formats supported")
        subtitle.setStyleSheet("color: #666666; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Quick Start Guide
        guide_title = QLabel("Quick Start")
        guide_title.setStyleSheet("color: #4A9EFF; font-size: 14px; font-weight: 600;")
        layout.addWidget(guide_title)

        steps = [
            "1. Drop files or click Browse to select files",
            "2. Choose output format from the dropdown",
            "3. Click Convert to start",
            "4. Files are saved in the same folder with new extension",
        ]
        for step in steps:
            lbl = QLabel(step)
            lbl.setStyleSheet("color: #AAAAAA; font-size: 12px; padding-left: 8px;")
            layout.addWidget(lbl)

        layout.addSpacing(10)

        # System Status
        status_title = QLabel("System Status")
        status_title.setStyleSheet("color: #4A9EFF; font-size: 14px; font-weight: 600;")
        layout.addWidget(status_title)

        active = self._manager.active_converters()
        names = {c.name for c in active}

        status_grid = QHBoxLayout()
        status_grid.setSpacing(16)

        # Pandoc status
        pandoc_ok = "pandoc" in names
        pandoc_lbl = QLabel(f"{'OK' if pandoc_ok else 'Not Found'}  Pandoc")
        pandoc_lbl.setStyleSheet(
            f"color: {'#4CAF50' if pandoc_ok else '#FF9800'}; font-size: 12px;"
        )
        status_grid.addWidget(pandoc_lbl)

        # LibreOffice status
        lo_ok = "libreoffice" in names
        lo_lbl = QLabel(f"{'OK' if lo_ok else 'Not Found'}  LibreOffice")
        lo_lbl.setStyleSheet(
            f"color: {'#4CAF50' if lo_ok else '#FF9800'}; font-size: 12px;"
        )
        status_grid.addWidget(lo_lbl)

        # Tesseract OCR status
        ocr_ok = "ocr" in names
        ocr_lbl = QLabel(f"{'OK' if ocr_ok else 'Not Found'}  Tesseract OCR")
        ocr_lbl.setStyleSheet(
            f"color: {'#4CAF50' if ocr_ok else '#FF9800'}; font-size: 12px;"
        )
        status_grid.addWidget(ocr_lbl)

        status_grid.addStretch()
        layout.addLayout(status_grid)

        # Warning if missing
        if not lo_ok or not ocr_ok:
            warn = QLabel(
                "Some converters are not available. "
                "Install LibreOffice for Office files, Tesseract for OCR."
            )
            warn.setStyleSheet("color: #FF9800; font-size: 11px;")
            warn.setWordWrap(True)
            layout.addWidget(warn)

        layout.addStretch()

        # Don't show again checkbox
        self.dont_show_chk = QCheckBox("Don't show this again")
        self.dont_show_chk.setStyleSheet("color: #666666;")
        layout.addWidget(self.dont_show_chk)

        # Get Started button
        start_btn = QPushButton("Get Started")
        start_btn.setObjectName("primaryBtn")
        start_btn.setMinimumHeight(40)
        start_btn.clicked.connect(self.accept)
        layout.addWidget(start_btn)


# ═══════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    """Clean minimalist converter window."""

    def __init__(self, manager: ConverterManager) -> None:
        super().__init__()
        self._manager = manager
        self._thread: QThread | None = None
        self._worker: ConvertWorker | None = None
        self._last_result: ConversionResult | None = None
        self._batch_files: list[str] = []
        self._file_widgets: dict[str, FileItemWidget] = {}
        self._settings = QSettings("MultiConvert", "MultiConvert")

        self.setWindowTitle("MultiConvert")
        self.resize(900, 700)
        self.setMinimumSize(700, 500)
        self.setAcceptDrops(True)

        self._build_ui()
        self._build_menu()
        self._bind_events()
        self._update_status()

        # Show welcome dialog on first run
        QTimer.singleShot(100, self._maybe_show_welcome)

    def _maybe_show_welcome(self) -> None:
        """Show welcome dialog if first run."""
        if not self._settings.value("hide_welcome", False, type=bool):
            dialog = WelcomeDialog(self._manager, self)
            dialog.exec()
            if dialog.dont_show_chk.isChecked():
                self._settings.setValue("hide_welcome", True)

    # ═══════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 12)
        root.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("MultiConvert")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()

        # Help button
        help_btn = QPushButton("?")
        help_btn.setFixedSize(28, 28)
        help_btn.setObjectName("secondaryBtn")
        help_btn.setToolTip("Help & About")
        help_btn.clicked.connect(self._show_help)
        header.addWidget(help_btn)

        root.addLayout(header)

        # Drop Zone
        self.drop_zone = DropZone()
        root.addWidget(self.drop_zone)

        # File List (scrollable)
        self.file_list_container = QWidget()
        self.file_list_layout = QVBoxLayout(self.file_list_container)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_layout.setSpacing(8)
        self.file_list_layout.addStretch()

        self.file_scroll = QScrollArea()
        self.file_scroll.setWidget(self.file_list_container)
        self.file_scroll.setWidgetResizable(True)
        self.file_scroll.setMaximumHeight(200)
        self.file_scroll.setVisible(False)
        self.file_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        root.addWidget(self.file_scroll)

        # Output Settings Row
        settings_row = QHBoxLayout()
        settings_row.setSpacing(12)

        lbl_fmt = QLabel("Convert to:")
        settings_row.addWidget(lbl_fmt)

        self.target_combo = QComboBox()
        self.target_combo.addItems(sorted(self._manager.all_formats()))
        self.target_combo.setMinimumWidth(100)
        if "pdf" in [self.target_combo.itemText(i) for i in range(self.target_combo.count())]:
            self.target_combo.setCurrentText("pdf")
        settings_row.addWidget(self.target_combo)

        settings_row.addStretch()

        self.chk_open_after = QCheckBox("Open after conversion")
        self.chk_open_after.setChecked(True)
        settings_row.addWidget(self.chk_open_after)

        self.chk_ocr = QCheckBox("Use OCR")
        self.chk_ocr.setToolTip("Enable OCR for scanned PDFs and images")
        settings_row.addWidget(self.chk_ocr)

        root.addLayout(settings_row)

        # Action Buttons
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.btn_browse = QPushButton("Browse Files")
        self.btn_browse.setObjectName("secondaryBtn")
        self.btn_browse.setMinimumHeight(40)
        action_row.addWidget(self.btn_browse)

        self.btn_convert = QPushButton("Convert")
        self.btn_convert.setObjectName("primaryBtn")
        self.btn_convert.setMinimumHeight(40)
        self.btn_convert.setMinimumWidth(140)
        action_row.addWidget(self.btn_convert)

        self.btn_open = QPushButton("Open Result")
        self.btn_open.setObjectName("successBtn")
        self.btn_open.setEnabled(False)
        self.btn_open.setMinimumHeight(40)
        action_row.addWidget(self.btn_open)

        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.setObjectName("secondaryBtn")
        self.btn_clear.setVisible(False)
        action_row.addWidget(self.btn_clear)

        root.addLayout(action_row)

        # Overall Progress
        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setFormat("%p%")
        self.overall_progress.setVisible(False)
        self.overall_progress.setFixedHeight(20)
        root.addWidget(self.overall_progress)

        root.addStretch()

        self.setCentralWidget(central)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(QLabel(f"v{app_version()}"))

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open Files...", self)
        open_action.triggered.connect(self._pick_input)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        guide_action = QAction("Quick Start Guide", self)
        guide_action.triggered.connect(lambda: self._show_welcome_forced())
        help_menu.addAction(guide_action)

        help_menu.addSeparator()

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_help(self) -> None:
        """Show quick help popup."""
        self._show_welcome_forced()

    def _show_welcome_forced(self) -> None:
        """Show welcome dialog regardless of settings."""
        dialog = WelcomeDialog(self._manager, self)
        dialog.exec()

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About MultiConvert",
            f"MultiConvert v{app_version()}\n\n"
            f"35+ input formats, 25+ output formats\n"
            f"Powered by Pandoc, LibreOffice, and Tesseract OCR\n\n"
            f"© {APP_COPYRIGHT}\n"
            f"https://github.com/ngTwg/Convert"
        )

    # ═══════════════════════════════════════════════════════
    #  EVENTS
    # ═══════════════════════════════════════════════════════

    def _bind_events(self) -> None:
        self.btn_browse.clicked.connect(self._pick_input)
        self.btn_convert.clicked.connect(self._start_convert)
        self.btn_open.clicked.connect(self._open_output)
        self.btn_clear.clicked.connect(self._clear_files)
        self.drop_zone.filesDropped.connect(self._handle_dropped_files)

    def _update_status(self) -> None:
        """Update status bar with system info."""
        active = self._manager.active_converters()
        count = len(self._manager.all_formats())
        self.status_label.setText(f"Ready - {len(active)} converters, {count} formats supported")

    # ═══════════════════════════════════════════════════════
    #  FILE HANDLING
    # ═══════════════════════════════════════════════════════

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self._handle_dropped_files(paths)

    def _handle_dropped_files(self, paths: list[str]) -> None:
        """Add files to the list."""
        for path in paths:
            if path not in self._batch_files:
                self._batch_files.append(path)
                self._add_file_widget(path)

        self._update_file_list_visibility()

        # Auto-select output format based on first file
        if paths:
            source_fmt = detect_format(paths[0])
            if source_fmt:
                outputs = sorted(self._manager.output_formats_for(source_fmt))
                if outputs:
                    self.target_combo.clear()
                    self.target_combo.addItems(outputs)
                    if "pdf" in outputs:
                        self.target_combo.setCurrentText("pdf")

    def _add_file_widget(self, file_path: str) -> None:
        """Add a file item widget."""
        widget = FileItemWidget(file_path)
        widget.removeClicked.connect(self._remove_file)
        self._file_widgets[file_path] = widget

        # Insert before the stretch
        self.file_list_layout.insertWidget(self.file_list_layout.count() - 1, widget)

    def _remove_file(self, file_path: str) -> None:
        """Remove a file from the list."""
        if file_path in self._batch_files:
            self._batch_files.remove(file_path)
        if file_path in self._file_widgets:
            widget = self._file_widgets.pop(file_path)
            widget.deleteLater()
        self._update_file_list_visibility()

    def _clear_files(self) -> None:
        """Clear all files."""
        self._batch_files.clear()
        for widget in self._file_widgets.values():
            widget.deleteLater()
        self._file_widgets.clear()
        self._update_file_list_visibility()
        self._last_result = None
        self.btn_open.setEnabled(False)

    def _update_file_list_visibility(self) -> None:
        """Show/hide file list based on file count."""
        has_files = len(self._batch_files) > 0
        self.file_scroll.setVisible(has_files)
        self.btn_clear.setVisible(has_files)
        self.status_label.setText(
            f"{len(self._batch_files)} file(s) selected" if has_files else "Ready"
        )

    def _pick_input(self) -> None:
        """Open file picker."""
        selected, _ = QFileDialog.getOpenFileNames(self, "Select files to convert")
        if selected:
            self._handle_dropped_files(selected)

    # ═══════════════════════════════════════════════════════
    #  CONVERSION
    # ═══════════════════════════════════════════════════════

    def _start_convert(self) -> None:
        """Start conversion process."""
        if not self._batch_files:
            QMessageBox.warning(self, "No Files", "Please select files to convert first.")
            return

        target_fmt = self.target_combo.currentText().strip()
        if not target_fmt:
            QMessageBox.warning(self, "No Format", "Please select an output format.")
            return

        self._set_converting_state(True)
        self.overall_progress.setVisible(True)
        self.overall_progress.setValue(0)

        # Prepare requests
        requests = []
        for src_text in self._batch_files:
            src = Path(src_text)
            dst = src.with_name(f"{src.stem}_converted.{target_fmt}")
            requests.append(ConversionRequest(
                source=src,
                destination=dst,
                target_format=target_fmt,
                options=self._build_options(),
            ))
            # Reset file widget state
            if src_text in self._file_widgets:
                self._file_widgets[src_text].set_converting()

        from multiconvert.ui.worker import BatchConvertWorker
        self._thread = QThread(self)
        self._batch_worker = BatchConvertWorker(self._manager, requests)
        self._batch_worker.moveToThread(self._thread)

        self._thread.started.connect(self._batch_worker.run)
        self._batch_worker.file_progress.connect(self._on_file_progress)
        self._batch_worker.file_complete.connect(self._on_file_complete)
        self._batch_worker.file_error.connect(self._on_file_error)
        self._batch_worker.progress.connect(self._on_overall_progress)
        self._batch_worker.batch_finished.connect(self._on_batch_finished)

        self._batch_worker.done.connect(self._thread.quit)
        self._batch_worker.done.connect(self._batch_worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(lambda: self._set_converting_state(False))

        self._thread.start()

    def _build_options(self) -> dict:
        options: dict[str, object] = {}
        if self.chk_ocr.isChecked():
            options["force_ocr"] = True
            options["ocr_lang"] = "vie+eng"
        return options

    def _set_converting_state(self, converting: bool) -> None:
        self.btn_convert.setEnabled(not converting)
        self.btn_browse.setEnabled(not converting)
        self.btn_clear.setEnabled(not converting)
        self.target_combo.setEnabled(not converting)

        if converting:
            self.btn_convert.setText("Converting...")
            self.status_label.setText("Converting files...")
        else:
            self.btn_convert.setText("Convert")
            self.overall_progress.setVisible(False)

    def _on_file_progress(self, file_path: str, progress: int) -> None:
        """Update individual file progress."""
        if file_path in self._file_widgets:
            self._file_widgets[file_path].set_progress(progress)

    def _on_file_complete(self, file_path: str, output_path: str) -> None:
        """Mark file as complete."""
        if file_path in self._file_widgets:
            self._file_widgets[file_path].set_complete()
        self._last_result = ConversionResult(destination=Path(output_path), route=[])

    def _on_file_error(self, file_path: str, error: str) -> None:
        """Mark file as failed."""
        if file_path in self._file_widgets:
            self._file_widgets[file_path].set_error(error)

    def _on_overall_progress(self, current: int, total: int) -> None:
        """Update overall progress bar."""
        percent = int((current / total) * 100) if total > 0 else 0
        self.overall_progress.setValue(percent)
        self.status_label.setText(f"Converting {current}/{total}...")

    def _on_batch_finished(self, success: int, total: int, failed_list: list) -> None:
        """Handle batch completion."""
        if success == total:
            self.status_label.setText(f"Done! {success} file(s) converted successfully")
            self.btn_open.setEnabled(True)
            if self.chk_open_after.isChecked() and self._last_result:
                self._open_path(self._last_result.destination)
        else:
            self.status_label.setText(f"Completed: {success}/{total} successful, {len(failed_list)} failed")
            if success > 0:
                self.btn_open.setEnabled(True)

    # ═══════════════════════════════════════════════════════
    #  POST-ACTIONS
    # ═══════════════════════════════════════════════════════

    def _open_output(self) -> None:
        """Open the last converted file."""
        if self._last_result and self._last_result.destination.exists():
            self._open_path(self._last_result.destination)
        else:
            QMessageBox.warning(self, "File Not Found", "The converted file was not found.")

    @staticmethod
    def _open_path(path: Path) -> None:
        """Open file with default system application."""
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except Exception as e:
            pass  # Silently fail
