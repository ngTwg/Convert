"""
MultiConvert – Clean Minimalist Theme
Simple, professional design without distracting colors
"""

DARK_THEME_QSS = """
/* ═══════════════════════════════════════════════════════════
   GLOBAL - Clean Sans-Serif Typography
   ═══════════════════════════════════════════════════════════ */

* {
    font-family: "Segoe UI", "SF Pro Display", system-ui, sans-serif;
    font-size: 13px;
    color: #E0E0E0;
    selection-background-color: #4A9EFF;
    selection-color: #FFFFFF;
}

/* ═══════════════════════════════════════════════════════════
   MAIN WINDOW - Simple Dark Background
   ═══════════════════════════════════════════════════════════ */

QMainWindow {
    background: #1A1A1A;
}

QWidget#centralWidget {
    background: #1A1A1A;
}

QWidget {
    background: transparent;
}

/* ═══════════════════════════════════════════════════════════
   GROUP BOXES (Cards) - Clean Flat Design
   ═══════════════════════════════════════════════════════════ */

QGroupBox {
    background: #242424;
    border: 1px solid #333333;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px 12px 12px 12px;
    font-size: 12px;
    font-weight: 600;
    color: #888888;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background: #2A2A2A;
    border: 1px solid #333333;
    border-radius: 6px;
    color: #AAAAAA;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════════════════
   LABELS - Clean Typography
   ═══════════════════════════════════════════════════════════ */

QLabel {
    color: #AAAAAA;
    font-size: 12px;
    font-weight: 500;
    padding: 0 2px;
    background: transparent;
    border: none;
}

QLabel#titleLabel {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
}

QLabel#subtitleLabel {
    color: #666666;
    font-size: 11px;
    font-weight: 400;
}

QLabel#dropHint {
    color: #888888;
    font-size: 14px;
    font-weight: 500;
}

QLabel#statusLabel {
    color: #666666;
    font-size: 11px;
    padding: 4px 8px;
}

QLabel#successLabel {
    color: #4CAF50;
    font-weight: 600;
}

QLabel#warningLabel {
    color: #FF9800;
    font-weight: 600;
}

QLabel#errorLabel {
    color: #F44336;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════
   LINE EDIT - Clean Input Fields
   ═══════════════════════════════════════════════════════════ */

QLineEdit {
    background: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 10px 14px;
    color: #E0E0E0;
    font-size: 13px;
    min-height: 20px;
}

QLineEdit:focus {
    border-color: #4A9EFF;
    background: #222222;
}

QLineEdit:hover {
    border-color: #444444;
}

QLineEdit:disabled {
    background: #1A1A1A;
    color: #555555;
    border-color: #2A2A2A;
}

QLineEdit::placeholder {
    color: #555555;
}

/* ═══════════════════════════════════════════════════════════
   COMBO BOX - Clean Dropdown
   ═══════════════════════════════════════════════════════════ */

QComboBox {
    background: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 10px 14px;
    color: #E0E0E0;
    font-size: 13px;
    min-height: 20px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #444444;
}

QComboBox:focus {
    border-color: #4A9EFF;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
    subcontrol-position: center right;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #888888;
    margin-right: 10px;
}

QComboBox::down-arrow:hover {
    border-top-color: #4A9EFF;
}

QComboBox QAbstractItemView {
    background: #242424;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 4px;
    selection-background-color: #4A9EFF;
    selection-color: #FFFFFF;
    outline: 0;
}

QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 4px;
    min-height: 24px;
}

QComboBox QAbstractItemView::item:hover {
    background: #333333;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS - Clean Flat Design
   ═══════════════════════════════════════════════════════════ */

QPushButton {
    background: #2A2A2A;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 10px 20px;
    color: #E0E0E0;
    font-size: 13px;
    font-weight: 500;
    min-height: 18px;
}

QPushButton:hover {
    background: #333333;
    border-color: #444444;
}

QPushButton:pressed {
    background: #252525;
}

QPushButton:disabled {
    background: #222222;
    color: #444444;
    border-color: #2A2A2A;
}

/* Primary Button - Blue Accent */
QPushButton#primaryBtn {
    background: #4A9EFF;
    border: none;
    color: #FFFFFF;
    font-weight: 600;
    padding: 12px 28px;
    font-size: 14px;
}

QPushButton#primaryBtn:hover {
    background: #5AABFF;
}

QPushButton#primaryBtn:pressed {
    background: #3A8EEF;
}

QPushButton#primaryBtn:disabled {
    background: #333333;
    color: #555555;
}

/* Success Button - Green */
QPushButton#successBtn {
    background: transparent;
    border: 1px solid #4CAF50;
    color: #4CAF50;
}

QPushButton#successBtn:hover {
    background: rgba(76, 175, 80, 0.1);
    border-color: #66BB6A;
    color: #66BB6A;
}

QPushButton#successBtn:disabled {
    border-color: #333333;
    color: #444444;
}

/* Danger Button - Red */
QPushButton#dangerBtn {
    background: transparent;
    border: 1px solid #F44336;
    color: #F44336;
}

QPushButton#dangerBtn:hover {
    background: rgba(244, 67, 54, 0.1);
}

/* Secondary Button */
QPushButton#secondaryBtn {
    background: transparent;
    border: 1px solid #444444;
    color: #AAAAAA;
}

QPushButton#secondaryBtn:hover {
    background: #2A2A2A;
    color: #E0E0E0;
}

/* ═══════════════════════════════════════════════════════════
   CHECK BOX - Clean Toggle
   ═══════════════════════════════════════════════════════════ */

QCheckBox {
    spacing: 8px;
    color: #AAAAAA;
    font-size: 12px;
    padding: 4px 0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #444444;
    background: #1E1E1E;
}

QCheckBox::indicator:hover {
    border-color: #4A9EFF;
}

QCheckBox::indicator:checked {
    background: #4A9EFF;
    border-color: #4A9EFF;
}

QCheckBox:hover {
    color: #E0E0E0;
}

/* ═══════════════════════════════════════════════════════════
   TEXT EDIT - Clean Text Area
   ═══════════════════════════════════════════════════════════ */

QTextEdit {
    background: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 12px;
    color: #AAAAAA;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 11px;
}

QTextEdit:focus {
    border-color: #4A9EFF;
}

QTextEdit#logBox {
    background: #1A1A1A;
    color: #888888;
    font-size: 11px;
    border-color: #2A2A2A;
}

/* ═══════════════════════════════════════════════════════════
   PROGRESS BAR - Clean Horizontal Progress
   ═══════════════════════════════════════════════════════════ */

QProgressBar {
    background: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 4px;
    text-align: center;
    color: #AAAAAA;
    font-size: 11px;
    font-weight: 500;
    min-height: 8px;
    max-height: 8px;
}

QProgressBar::chunk {
    background: #4A9EFF;
    border-radius: 3px;
}

/* Thin progress bar for file items */
QProgressBar#fileProgress {
    min-height: 4px;
    max-height: 4px;
    border: none;
    background: #2A2A2A;
}

QProgressBar#fileProgress::chunk {
    background: #4CAF50;
    border-radius: 2px;
}

/* ═══════════════════════════════════════════════════════════
   STATUS BAR - Clean Bottom Bar
   ═══════════════════════════════════════════════════════════ */

QStatusBar {
    background: #1A1A1A;
    border-top: 1px solid #2A2A2A;
    color: #666666;
    font-size: 11px;
    padding: 4px 12px;
    min-height: 24px;
}

QStatusBar::item {
    border: none;
}

/* ═══════════════════════════════════════════════════════════
   SCROLLBAR - Minimal Thin Scrollbar
   ═══════════════════════════════════════════════════════════ */

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #444444;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #555555;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: #444444;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #555555;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    width: 0;
}

/* ═══════════════════════════════════════════════════════════
   LIST WIDGET - Clean File List
   ═══════════════════════════════════════════════════════════ */

QListWidget {
    background: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 4px;
    outline: 0;
}

QListWidget::item {
    background: #242424;
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 2px 0;
    color: #E0E0E0;
    font-size: 12px;
}

QListWidget::item:selected {
    background: #333333;
    color: #FFFFFF;
}

QListWidget::item:hover {
    background: #2A2A2A;
}

/* ═══════════════════════════════════════════════════════════
   DROP ZONE - Simple Dashed Border
   ═══════════════════════════════════════════════════════════ */

QFrame#dropZone {
    background: #1E1E1E;
    border: 2px dashed #333333;
    border-radius: 8px;
    min-height: 100px;
}

QFrame#dropZone:hover {
    border-color: #4A9EFF;
    background: #222222;
}

QFrame[dropActive="true"] {
    border: 2px solid #4A9EFF;
    background: rgba(74, 158, 255, 0.05);
}

/* ═══════════════════════════════════════════════════════════
   MENU BAR - Clean Menu
   ═══════════════════════════════════════════════════════════ */

QMenuBar {
    background: #1A1A1A;
    border-bottom: 1px solid #2A2A2A;
    padding: 4px 8px;
    color: #AAAAAA;
    font-size: 12px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
    background: transparent;
}

QMenuBar::item:selected {
    background: #2A2A2A;
    color: #FFFFFF;
}

QMenu {
    background: #242424;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    color: #E0E0E0;
}

QMenu::item:selected {
    background: #333333;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background: #333333;
    margin: 4px 8px;
}

/* ═══════════════════════════════════════════════════════════
   TOOLTIP - Clean Tooltip
   ═══════════════════════════════════════════════════════════ */

QToolTip {
    background: #2A2A2A;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 6px 10px;
    color: #E0E0E0;
    font-size: 11px;
}

/* ═══════════════════════════════════════════════════════════
   DIALOG - Clean Dialog Windows
   ═══════════════════════════════════════════════════════════ */

QDialog {
    background: #1A1A1A;
}

QMessageBox {
    background: #1A1A1A;
}

QMessageBox QLabel {
    color: #E0E0E0;
    font-size: 13px;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 8px 16px;
}

/* ═══════════════════════════════════════════════════════════
   TAB WIDGET
   ═══════════════════════════════════════════════════════════ */

QTabWidget::pane {
    background: transparent;
    border: none;
}

QTabBar::tab {
    background: #242424;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
    color: #888888;
    font-weight: 500;
    font-size: 12px;
}

QTabBar::tab:selected {
    background: #2A2A2A;
    color: #FFFFFF;
    border-color: #444444;
}

QTabBar::tab:hover:!selected {
    background: #2A2A2A;
    color: #AAAAAA;
}

/* ═══════════════════════════════════════════════════════════
   SPLITTER
   ═══════════════════════════════════════════════════════════ */

QSplitter::handle {
    background: #333333;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background: #4A9EFF;
}

/* ═══════════════════════════════════════════════════════════
   FILE ITEM WIDGET - Custom Widget for File Progress
   ═══════════════════════════════════════════════════════════ */

QWidget#fileItemWidget {
    background: #242424;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 8px;
}

QWidget#fileItemWidget:hover {
    background: #2A2A2A;
    border-color: #444444;
}

QWidget#fileItemComplete {
    background: #242424;
    border: 1px solid #4CAF50;
    border-radius: 6px;
}

QWidget#fileItemError {
    background: #242424;
    border: 1px solid #F44336;
    border-radius: 6px;
}
"""


# Simple format colors for badges (minimal palette)
FORMAT_COLORS: dict[str, str] = {
    "pdf":  "#E57373",
    "docx": "#64B5F6",
    "doc":  "#64B5F6",
    "txt":  "#AAAAAA",
    "md":   "#81C784",
    "html": "#FFB74D",
    "epub": "#BA68C8",
    "odt":  "#4DD0E1",
    "rtf":  "#90A4AE",
}


def format_badge_style(fmt: str) -> str:
    """Return inline style for a small format badge."""
    color = FORMAT_COLORS.get(fmt, "#888888")
    return (
        f"background: transparent; "
        f"color: {color}; "
        f"border: 1px solid {color}; "
        f"border-radius: 3px; "
        f"padding: 2px 6px; "
        f"font-size: 10px; "
        f"font-weight: 600; "
        f"text-transform: uppercase;"
    )
