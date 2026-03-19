"""
MultiConvert – Clean Main Window v2
Fixed bugs, added history, output folder selection, click-to-browse drop zone.
"""
from __future__ import annotations

import importlib.metadata
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QSettings, QSize
)
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
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
    QSplitter,
)

from multiconvert.formats import TEXT_EDITABLE_FORMATS, detect_format, ensure_extension
from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest, ConversionResult
from multiconvert.ui.worker import ConvertWorker

APP_COPYRIGHT = "Bản quyền đầy đủ thuộc Lê Ngọc Tường Github/ngTwg. HCMUS."


def app_version() -> str:
    try:
        return importlib.metadata.version("multiconvert")
    except importlib.metadata.PackageNotFoundError:
        return "0.2.0"


def get_app_icon() -> QIcon:
    """Get application icon from tools folder or use default."""
    import sys
    # Check various locations for icon
    search_paths = [
        Path(__file__).parent.parent.parent.parent / "tools" / "logo.ico",
        Path(sys.executable).parent / "tools" / "logo.ico",
        Path.cwd() / "tools" / "logo.ico",
    ]
    for path in search_paths:
        if path.exists():
            return QIcon(str(path))
    return QIcon()


# ═══════════════════════════════════════════════════════════
#  FILE ITEM WIDGET
# ═══════════════════════════════════════════════════════════

class FileItemWidget(QWidget):
    """Widget showing a single file with its conversion progress."""
    removeClicked = Signal(str)
    renameClicked = Signal(str)

    def __init__(self, file_path: str, parent=None) -> None:
        super().__init__(parent)
        self.file_path = file_path
        self.output_path = ""
        self.setFixedHeight(50)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(4)

        # Top row: filename + controls
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        # File icon (simple text)
        icon_lbl = QLabel("□")
        icon_lbl.setFixedWidth(16)
        icon_lbl.setStyleSheet("color: #666666; font-size: 12px;")
        top_row.addWidget(icon_lbl)

        self.name_label = QLabel(Path(self.file_path).name)
        self.name_label.setStyleSheet("color: #E0E0E0; font-size: 12px;")
        
        self.rename_btn = QPushButton("✎ Đổi")
        self.rename_btn.setFixedSize(45, 20)
        self.rename_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #4A9EFF; border-radius: 3px; color: #4A9EFF; font-size: 11px; }"
            "QPushButton:hover { background: rgba(74, 158, 255, 0.1); color: #5AABFF; }"
        )
        self.rename_btn.clicked.connect(self._rename_output)
        self.rename_btn.setVisible(False)
        self.rename_btn.setToolTip("Ghi đè file / Đổi tên")

        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(4)
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.rename_btn)
        name_layout.addStretch()
        top_row.addLayout(name_layout, 1)

        # Format badge
        fmt = detect_format(self.file_path) or "?"
        self.format_label = QLabel(fmt.upper())
        self.format_label.setFixedWidth(45)
        self.format_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.format_label.setStyleSheet(
            "color: #888888; font-size: 9px; padding: 2px 4px; "
            "border: 1px solid #444444; border-radius: 2px;"
        )
        top_row.addWidget(self.format_label)

        # Status
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setFixedWidth(70)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setStyleSheet("color: #666666; font-size: 11px;")
        top_row.addWidget(self.status_label)

        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(18, 18)
        self.remove_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #555555; font-size: 14px; }"
            "QPushButton:hover { color: #F44336; }"
        )
        self.remove_btn.clicked.connect(lambda: self.removeClicked.emit(self.file_path))
        top_row.addWidget(self.remove_btn)

        layout.addLayout(top_row)

        # Progress bar (thin)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar { background: #2A2A2A; border: none; border-radius: 1px; }"
            "QProgressBar::chunk { background: #4A9EFF; border-radius: 1px; }"
        )
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Style container
        self.setStyleSheet(
            "FileItemWidget { background: #242424; border: 1px solid #333333; border-radius: 4px; }"
        )

    def set_converting(self) -> None:
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.status_label.setText("Đang chuyển đổi...")
        self.status_label.setStyleSheet("color: #4A9EFF; font-size: 11px;")
        self.remove_btn.setEnabled(False)

    def set_progress(self, value: int) -> None:
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(value)
        self.status_label.setText(f"{value}%")

    def set_complete(self, output_path: str = "") -> None:
        self.output_path = output_path
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setStyleSheet(
            "QProgressBar { background: #2A2A2A; border: none; border-radius: 1px; }"
            "QProgressBar::chunk { background: #4CAF50; border-radius: 1px; }"
        )
        self.status_label.setText("Hoàn tất")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: 600;")
        self.setStyleSheet(
            "FileItemWidget { background: #242424; border: 1px solid #4CAF50; border-radius: 4px; }"
        )
        self.rename_btn.setVisible(True)
        self.remove_btn.setEnabled(True)

    def _rename_output(self) -> None:
        if not self.output_path or not Path(self.output_path).exists():
            return
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        
        old_path = Path(self.output_path)
        new_name, ok = QInputDialog.getText(
            self, "Đổi tên file", "Tên file mới:", text=old_path.name
        )
        if ok and new_name and new_name != old_path.name:
            new_path = old_path.parent / new_name
            if new_path.exists():
                QMessageBox.warning(self, "Lỗi", "File đã tồn tại!")
                return
            try:
                old_path.rename(new_path)
                self.output_path = str(new_path)
                self.name_label.setText(new_path.name)
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể đổi tên file:\n{e}")

    def set_error(self, message: str = "Lỗi") -> None:
        self.progress.setVisible(False)
        self.status_label.setText("Lỗi")
        self.status_label.setStyleSheet("color: #F44336; font-size: 11px;")
        self.status_label.setToolTip(message)
        self.setStyleSheet(
            "FileItemWidget { background: #242424; border: 1px solid #F44336; border-radius: 4px; }"
        )
        self.remove_btn.setEnabled(True)


# ═══════════════════════════════════════════════════════════
#  DROP ZONE (Clickable)
# ═══════════════════════════════════════════════════════════

class DropZone(QFrame):
    """Clickable drag-and-drop region."""
    filesDropped = Signal(list)
    clicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        icon = QLabel("+")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            "font-size: 28px; font-weight: 300; color: #444444; background: transparent;"
        )
        layout.addWidget(icon)

        hint = QLabel("Kéo thả file vào đây hoặc bấm để chọn")
        hint.setStyleSheet("color: #888888; font-size: 13px; background: transparent;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        sub = QLabel("Hỗ trợ PDF, DOCX, MD, HTML, EPUB, Ảnh...")
        sub.setStyleSheet("color: #555555; font-size: 11px; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

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
#  HISTORY ITEM
# ═══════════════════════════════════════════════════════════

class HistoryItem(QWidget):
    """Single history entry."""
    def __init__(self, data: dict, parent=None) -> None:
        super().__init__(parent)
        self.data = data
        self.setFixedHeight(38)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)

        # Time
        time_str = self.data.get("time", "")
        time_lbl = QLabel(time_str)
        time_lbl.setFixedWidth(40)
        time_lbl.setStyleSheet("color: #555555; font-size: 10px;")
        layout.addWidget(time_lbl)

        # Filename and Path
        center_vbox = QVBoxLayout()
        center_vbox.setSpacing(0)
        center_vbox.setContentsMargins(0, 0, 0, 0)

        name = Path(self.data.get("output", "")).name
        self.name_lbl = QLabel(name)
        self.name_lbl.setStyleSheet("color: #AAAAAA; font-size: 11px;")

        self.rename_btn = QPushButton("✎ Sửa")
        self.rename_btn.setFixedSize(40, 20)
        self.rename_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #333333; color: #888888; font-size: 10px; border-radius: 2px; }"
            "QPushButton:hover { border-color: #4A9EFF; color: #4A9EFF; }"
        )
        self.rename_btn.setToolTip("Ghi đè file / Đổi tên")
        self.rename_btn.clicked.connect(self._rename_output)

        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(4)
        name_row.addWidget(self.name_lbl)
        name_row.addWidget(self.rename_btn)
        name_row.addStretch()
        
        center_vbox.addLayout(name_row)

        path_str = str(Path(self.data.get("output", "")).parent)
        path_lbl = QLabel(path_str)
        path_lbl.setStyleSheet("color: #555555; font-size: 9px;")
        # Fix long paths stretching layout too much
        # We can let layout stretch apply to the vbox.
        center_vbox.addWidget(path_lbl)
        layout.addLayout(center_vbox, 1)

        # Size
        size_kb = self.data.get("size_kb", 0)
        size_lbl = QLabel(f"{size_kb:.1f} KB")
        size_lbl.setFixedWidth(55)
        size_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        size_lbl.setStyleSheet("color: #555555; font-size: 10px;")
        layout.addWidget(size_lbl)

        # Open button
        open_btn = QPushButton("Mở")
        open_btn.setFixedSize(36, 20)
        open_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #333333; "
            "color: #666666; font-size: 9px; border-radius: 2px; }"
            "QPushButton:hover { border-color: #4A9EFF; color: #4A9EFF; }"
        )
        open_btn.clicked.connect(self._open_file)
        layout.addWidget(open_btn)

    def _open_file(self) -> None:
        path = Path(self.data.get("output", ""))
        if path.exists():
            if os.name == "nt":
                import os
                os.startfile(path)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)

    def _rename_output(self) -> None:
        path = Path(self.data.get("output", ""))
        if not path.exists():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Lỗi", "File không còn tồn tại ở vị trí này!")
            return
            
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        
        new_name, ok = QInputDialog.getText(
            self, "Đổi tên file", "Tên file mới:", text=path.name
        )
        if ok and new_name and new_name != path.name:
            new_path = path.parent / new_name
            if new_path.exists():
                QMessageBox.warning(self, "Lỗi", "File đã tồn tại ở đích đến!")
                return
            try:
                path.rename(new_path)
                self.data["output"] = str(new_path)
                self.name_lbl.setText(new_name)
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể đổi tên file:\n{e}")


# ═══════════════════════════════════════════════════════════
#  WELCOME DIALOG
# ═══════════════════════════════════════════════════════════

class WelcomeDialog(QDialog):
    def __init__(self, manager: ConverterManager, parent=None) -> None:
        super().__init__(parent)
        self._manager = manager
        self.setWindowTitle("Chào Mừng")
        self.setWindowIcon(get_app_icon())
        self.setFixedSize(450, 380)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        title = QLabel("MultiConvert")
        title.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: 700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(f"v{app_version()} - 35+ formats")
        subtitle.setStyleSheet("color: #666666; font-size: 11px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Quick guide
        guide = QLabel("Bắt Đầu Nhanh")
        guide.setStyleSheet("color: #4A9EFF; font-size: 13px; font-weight: 600;")
        layout.addWidget(guide)

        steps = [
            "1. Kéo thả file hoặc bấm để chọn",
            "2. Chọn định dạng đích",
            "3. Chọn thư mục lưu (tuỳ chọn)",
            "4. Nhấn Chuyển đổi",
        ]
        for step in steps:
            lbl = QLabel(step)
            lbl.setStyleSheet("color: #AAAAAA; font-size: 11px; padding-left: 6px;")
            layout.addWidget(lbl)

        layout.addSpacing(8)

        # System status
        status = QLabel("Trạng thái Hệ thống")
        status.setStyleSheet("color: #4A9EFF; font-size: 13px; font-weight: 600;")
        layout.addWidget(status)

        active = self._manager.active_converters()
        names = {c.name for c in active}

        status_row = QHBoxLayout()
        for name, label in [("pandoc", "Pandoc"), ("libreoffice", "LibreOffice"), ("ocr", "Tesseract")]:
            ok = name in names
            lbl = QLabel(f"{'✓' if ok else '○'} {label}")
            lbl.setStyleSheet(f"color: {'#4CAF50' if ok else '#666666'}; font-size: 11px;")
            status_row.addWidget(lbl)
        status_row.addStretch()
        layout.addLayout(status_row)

        layout.addStretch()

        self.dont_show = QCheckBox("Không hiện lại")
        self.dont_show.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self.dont_show)

        btn = QPushButton("Bắt Đầu")
        btn.setObjectName("primaryBtn")
        btn.setMinimumHeight(36)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


# ═══════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self, manager: ConverterManager) -> None:
        super().__init__()
        self._manager = manager
        self._thread: QThread | None = None
        self._batch_files: list[str] = []
        self._file_widgets: dict[str, FileItemWidget] = {}
        self._output_folder: str = ""
        self._history: list[dict] = []
        self._settings = QSettings("MultiConvert", "MultiConvert")
        self._converting = False
        self._completed_count = 0
        self._total_count = 0

        self.setWindowTitle("MultiConvert")
        self.setWindowIcon(get_app_icon())
        self.resize(800, 650)
        self.setMinimumSize(600, 450)
        self.setAcceptDrops(True)

        self._load_history()
        self._build_ui()
        self._build_menu()
        self._bind_events()
        self._update_status()

        QTimer.singleShot(100, self._maybe_show_welcome)

    def _maybe_show_welcome(self) -> None:
        if not self._settings.value("hide_welcome", False, type=bool):
            dialog = WelcomeDialog(self._manager, self)
            dialog.exec()
            if dialog.dont_show.isChecked():
                self._settings.setValue("hide_welcome", True)

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 8)
        root.setSpacing(10)

        # Header
        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel("MultiConvert")
        title.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 600;")
        header.addWidget(title)

        header.addStretch()

        # App logo in header
        logo_label = QPushButton()
        logo_label.setFixedSize(28, 28)
        logo_label.setStyleSheet("QPushButton { border: none; background: transparent; }")
        icon = get_app_icon()
        if not icon.isNull():
            logo_label.setIcon(icon)
            logo_label.setIconSize(QSize(24, 24))
        else:
            logo_label.setText("◎")
            logo_label.setStyleSheet("color: #4A9EFF; font-size: 18px; border: none; background: transparent;")
        logo_label.setToolTip(f"MultiConvert v{app_version()} - Chào mừng")
        logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        logo_label.clicked.connect(lambda: WelcomeDialog(self._manager, self).exec())
        header.addWidget(logo_label)

        root.addLayout(header)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: #333333; }")

        # Top section
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        # Drop zone
        self.drop_zone = DropZone()
        top_layout.addWidget(self.drop_zone)

        # File list
        self.file_list_widget = QWidget()
        self.file_list_layout = QVBoxLayout(self.file_list_widget)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_layout.setSpacing(4)

        self.file_scroll = QScrollArea()
        self.file_scroll.setWidget(self.file_list_widget)
        self.file_scroll.setWidgetResizable(True)
        self.file_scroll.setMaximumHeight(150)
        self.file_scroll.setVisible(False)
        self.file_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        top_layout.addWidget(self.file_scroll)

        # Settings row
        settings = QHBoxLayout()
        settings.setSpacing(10)

        settings.addWidget(QLabel("Định dạng:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(sorted(self._manager.all_formats()))
        self.target_combo.setMinimumWidth(80)
        self.target_combo.setCurrentText("pdf")
        settings.addWidget(self.target_combo)

        settings.addWidget(QLabel("Lưu tại:"))
        self.folder_input = QLineEdit()
        # Set default to user's Documents folder
        default_folder = str(Path.home() / "Documents")
        self.folder_input.setText(default_folder)
        self.folder_input.setReadOnly(True)
        self.folder_input.setStyleSheet(
            "QLineEdit { color: #AAAAAA; background: #2A2A2A; border: 1px solid #333333; "
            "border-radius: 3px; padding: 4px 8px; }"
        )
        self._output_folder = default_folder
        self.folder_input.setMinimumWidth(150)
        settings.addWidget(self.folder_input, 1)

        self.browse_folder_btn = QPushButton("Duyệt")
        self.browse_folder_btn.setFixedWidth(60)
        self.browse_folder_btn.setStyleSheet(
            "QPushButton { background: #2A2A2A; border: 1px solid #333333; "
            "border-radius: 3px; color: #AAAAAA; font-size: 11px; padding: 4px 8px; }"
            "QPushButton:hover { border-color: #4A9EFF; }"
        )
        settings.addWidget(self.browse_folder_btn)

        top_layout.addLayout(settings)

        # Options row
        opts = QHBoxLayout()
        opts.setSpacing(16)

        self.chk_open = QCheckBox("Mở file sau khi xong")
        self.chk_open.setChecked(True)
        self.chk_open.setStyleSheet("color: #888888; font-size: 11px;")
        opts.addWidget(self.chk_open)

        self.chk_ocr = QCheckBox("Dùng OCR")
        self.chk_ocr.setStyleSheet("color: #888888; font-size: 11px;")
        opts.addWidget(self.chk_ocr)

        opts.addStretch()

        self.btn_clear = QPushButton("Xóa tất cả")
        self.btn_clear.setVisible(False)
        self.btn_clear.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #444444; "
            "border-radius: 3px; color: #888888; font-size: 11px; padding: 4px 12px; }"
            "QPushButton:hover { border-color: #F44336; color: #F44336; }"
        )
        opts.addWidget(self.btn_clear)

        top_layout.addLayout(opts)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.btn_convert = QPushButton("Chuyển đổi")
        self.btn_convert.setMinimumHeight(38)
        self.btn_convert.setStyleSheet(
            "QPushButton { background: #4A9EFF; border: none; border-radius: 4px; "
            "color: #FFFFFF; font-size: 13px; font-weight: 600; padding: 8px 24px; }"
            "QPushButton:hover { background: #5AABFF; }"
            "QPushButton:disabled { background: #333333; color: #555555; }"
        )
        actions.addWidget(self.btn_convert)

        self.btn_open = QPushButton("Mở Kết Quả")
        self.btn_open.setEnabled(False)
        self.btn_open.setMinimumHeight(38)
        self.btn_open.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #4CAF50; "
            "border-radius: 4px; color: #4CAF50; font-size: 12px; padding: 8px 16px; }"
            "QPushButton:hover { background: rgba(76, 175, 80, 0.1); }"
            "QPushButton:disabled { border-color: #333333; color: #444444; }"
        )
        actions.addWidget(self.btn_open)

        top_layout.addLayout(actions)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar { background: #2A2A2A; border: none; border-radius: 2px; }"
            "QProgressBar::chunk { background: #4A9EFF; border-radius: 2px; }"
        )
        top_layout.addWidget(self.progress)

        splitter.addWidget(top_widget)

        # History section
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 8, 0, 0)
        history_layout.setSpacing(4)

        history_header = QHBoxLayout()
        history_lbl = QLabel("Nhật ký chuyển đổi")
        history_lbl.setStyleSheet("color: #666666; font-size: 11px; font-weight: 600;")
        history_header.addWidget(history_lbl)
        history_header.addStretch()

        clear_history_btn = QPushButton("Xóa")
        clear_history_btn.setFixedSize(40, 18)
        clear_history_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #555555; font-size: 10px; }"
            "QPushButton:hover { color: #F44336; }"
        )
        clear_history_btn.clicked.connect(self._clear_history)
        history_header.addWidget(clear_history_btn)
        history_layout.addLayout(history_header)

        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(2)

        history_scroll = QScrollArea()
        history_scroll.setWidget(self.history_container)
        history_scroll.setWidgetResizable(True)
        history_scroll.setStyleSheet("QScrollArea { border: none; background: #1E1E1E; border-radius: 4px; }")
        history_layout.addWidget(history_scroll)

        splitter.addWidget(history_widget)
        splitter.setSizes([400, 150])

        root.addWidget(splitter)

        self.setCentralWidget(central)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { background: #1A1A1A; border-top: 1px solid #2A2A2A; }")
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666666; font-size: 11px;")
        self.status_bar.addWidget(self.status_label)

        # Load history items
        self._refresh_history_ui()

    def _build_menu(self) -> None:
        menu = self.menuBar()

        file_menu = menu.addMenu("Tập Tin")
        open_act = QAction("Mở File...", self)
        open_act.triggered.connect(self._pick_files)
        file_menu.addAction(open_act)
        file_menu.addSeparator()
        exit_act = QAction("Thoát", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        help_menu = menu.addMenu("Trợ Giúp")
        guide_act = QAction("Bắt Đầu Nhanh", self)
        guide_act.triggered.connect(lambda: WelcomeDialog(self._manager, self).exec())
        help_menu.addAction(guide_act)
        about_act = QAction("Thông Tin", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _show_about(self) -> None:
        QMessageBox.about(self, "Thông Tin", f"MultiConvert v{app_version()}\n\n{APP_COPYRIGHT}")

    def _bind_events(self) -> None:
        self.drop_zone.filesDropped.connect(self._add_files)
        self.drop_zone.clicked.connect(self._pick_files)
        self.browse_folder_btn.clicked.connect(self._pick_output_folder)
        self.btn_convert.clicked.connect(self._start_convert)
        self.btn_open.clicked.connect(self._open_last_result)
        self.btn_clear.clicked.connect(self._clear_files)

    def _update_status(self) -> None:
        active = self._manager.active_converters()
        self.status_label.setText(f"Sẵn sàng - {len(active)} bộ chuyển đổi")

    # ─── File handling ───────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if paths:
            self._add_files(paths)

    def _pick_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Chọn files")
        if files:
            self._add_files(files)

    def _pick_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu", self._output_folder)
        if folder:
            self._output_folder = folder
            self.folder_input.setText(folder)

    def _add_files(self, paths: list[str]) -> None:
        for p in paths:
            path = str(Path(p).resolve())
            if path not in self._batch_files:
                self._batch_files.append(path)
                widget = FileItemWidget(path)
                widget.removeClicked.connect(self._remove_file)
                self._file_widgets[path] = widget
                self.file_list_layout.addWidget(widget)

        self._update_ui_state()

        if paths:
            # Update default save folder if we just picked the first batch of files
            if len(self._batch_files) == len(paths):
                first_path = Path(paths[0]).resolve()
                self._output_folder = str(first_path.parent)
                self.folder_input.setText(self._output_folder)

            fmt = detect_format(paths[0])
            if fmt:
                outputs = sorted(self._manager.output_formats_for(fmt))
                if outputs:
                    self.target_combo.clear()
                    self.target_combo.addItems(outputs)
                    if "pdf" in outputs:
                        self.target_combo.setCurrentText("pdf")

    def _remove_file(self, raw_path: str) -> None:
        path = str(Path(raw_path).resolve())
        if path in self._batch_files:
            self._batch_files.remove(path)
        if path in self._file_widgets:
            self._file_widgets[path].deleteLater()
            del self._file_widgets[path]
        self._update_ui_state()

    def _clear_files(self) -> None:
        self._batch_files.clear()
        for w in self._file_widgets.values():
            w.deleteLater()
        self._file_widgets.clear()
        self._update_ui_state()
        self.btn_open.setEnabled(False)

    def _update_ui_state(self) -> None:
        has_files = len(self._batch_files) > 0
        self.file_scroll.setVisible(has_files)
        self.btn_clear.setVisible(has_files)
        if has_files:
            self.status_label.setText(f"Đã chọn {len(self._batch_files)} file")
        else:
            self._update_status()

    # ─── Conversion ──────────────────────────────────────────

    def _start_convert(self) -> None:
        if not self._batch_files:
            QMessageBox.warning(self, "Chưa có File", "Vui lòng thêm file trước.")
            return

        target = self.target_combo.currentText()
        if not target:
            return

        self._converting = True
        self._completed_count = 0
        self._total_count = len(self._batch_files)

        self.btn_convert.setEnabled(False)
        self.btn_convert.setText("Đang chuyển đổi...")
        self.progress.setVisible(True)
        self.progress.setValue(0)

        # Build requests
        requests = []
        output_folder = self._output_folder or None

        for path in self._batch_files:
            src = Path(path)
            if output_folder:
                dst = Path(output_folder) / f"{src.stem}_converted.{target}"
            else:
                dst = src.with_name(f"{src.stem}_converted.{target}")

            requests.append(ConversionRequest(
                source=src,
                destination=dst,
                target_format=target,
                options={"force_ocr": self.chk_ocr.isChecked(), "ocr_lang": "vie+eng"} if self.chk_ocr.isChecked() else {},
            ))

            if path in self._file_widgets:
                self._file_widgets[path].set_converting()

        # Start worker
        from multiconvert.ui.worker import BatchConvertWorker
        self._thread = QThread(self)
        self._worker = BatchConvertWorker(self._manager, requests)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.file_progress.connect(self._on_file_progress)
        self._worker.file_complete.connect(self._on_file_complete)
        self._worker.file_error.connect(self._on_file_error)
        self._worker.progress.connect(self._on_progress)
        self._worker.batch_finished.connect(self._on_batch_done)
        self._worker.done.connect(self._thread.quit)
        self._worker.done.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._on_thread_done)

        self._thread.start()

    def _on_file_progress(self, path: str, value: int) -> None:
        path = str(Path(path).resolve())
        if path in self._file_widgets:
            self._file_widgets[path].set_progress(value)

    def _on_file_complete(self, source: str, output: str) -> None:
        source = str(Path(source).resolve())
        if source in self._file_widgets:
            self._file_widgets[source].set_complete(output)

        self._completed_count += 1
        self._last_output = output

        # Add to history
        try:
            size_kb = Path(output).stat().st_size / 1024
        except Exception:
            size_kb = 0

        self._history.insert(0, {
            "time": datetime.now().strftime("%H:%M"),
            "source": source,
            "output": output,
            "size_kb": size_kb,
        })
        self._history = self._history[:50]  # Keep last 50
        self._save_history()
        self._refresh_history_ui()

    def _on_file_error(self, path: str, error: str) -> None:
        path = str(Path(path).resolve())
        if path in self._file_widgets:
            self._file_widgets[path].set_error(error)

    def _on_progress(self, current: int, total: int) -> None:
        percent = int((current / total) * 100) if total > 0 else 0
        self.progress.setValue(percent)
        self.status_label.setText(f"Đang chuyển đổi {current}/{total}...")

    def _on_batch_done(self, success: int, total: int, failed: list) -> None:
        self.status_label.setText(f"Hoàn tất: {success}/{total} file")
        # Reset button state immediately when batch is done
        self._converting = False
        self.btn_convert.setEnabled(True)
        self.btn_convert.setText("Chuyển đổi")
        self.progress.setVisible(False)

        if success > 0:
            self.btn_open.setEnabled(True)
            if self.chk_open.isChecked() and hasattr(self, "_last_output"):
                self._open_file(self._last_output)

    def _on_thread_done(self) -> None:
        self._converting = False
        self.btn_convert.setEnabled(True)
        self.btn_convert.setText("Chuyển đổi")
        self.progress.setVisible(False)

    def _open_last_result(self) -> None:
        if hasattr(self, "_last_output"):
            self._open_file(self._last_output)

    def _open_file(self, path: str) -> None:
        p = Path(path)
        if p.exists():
            if os.name == "nt":
                os.startfile(p)
            else:
                subprocess.run(["xdg-open", str(p)], check=False)

    # ─── History ─────────────────────────────────────────────

    def _load_history(self) -> None:
        try:
            data = self._settings.value("history", "[]")
            self._history = json.loads(data) if data else []
        except Exception:
            self._history = []

    def _save_history(self) -> None:
        self._settings.setValue("history", json.dumps(self._history))

    def _clear_history(self) -> None:
        self._history.clear()
        self._save_history()
        self._refresh_history_ui()

    def _refresh_history_ui(self) -> None:
        # Clear old
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                pass # Already removed from layout by takeAt

        # Add new
        for entry in self._history[:20]:
            widget = HistoryItem(entry)
            self.history_layout.addWidget(widget)

        if not self._history:
            lbl = QLabel("Chưa có nhật ký")
            lbl.setStyleSheet("color: #444444; font-size: 11px; padding: 16px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_layout.addWidget(lbl)

        self.history_layout.addStretch()
