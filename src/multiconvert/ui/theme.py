"""
MultiConvert – Premium Dark Theme Stylesheet (QSS)
Inspired by: JetBrains Fleet / Figma desktop dark UI
Design language: Dark slate with warm amber accents, soft glows
"""

DARK_THEME_QSS = """
/* ═══════════════════════════════════════════════════════════
   GLOBAL PALETTE
   ═══════════════════════════════════════════════════════════ */

* {
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
    color: #D4D7DE;
    selection-background-color: #E8A838;
    selection-color: #1B1D23;
}

/* ═══════════════════════════════════════════════════════════
   MAIN WINDOW & CENTRAL WIDGET
   ═══════════════════════════════════════════════════════════ */

QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #13151A,
        stop:0.5 #1A1D25,
        stop:1 #111318
    );
}

QWidget#centralWidget {
    background: transparent;
}

QWidget {
    background: transparent;
}

/* ═══════════════════════════════════════════════════════════
   GROUP BOXES (Cards)
   ═══════════════════════════════════════════════════════════ */

QGroupBox {
    background: rgba(30, 33, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    margin-top: 18px;
    padding: 20px 16px 16px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #A0A5B2;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 14px;
    background: rgba(232, 168, 56, 0.12);
    border: 1px solid rgba(232, 168, 56, 0.25);
    border-radius: 8px;
    color: #E8A838;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════════════════════ */

QLabel {
    color: #8B90A0;
    font-size: 12px;
    font-weight: 500;
    padding: 0 2px;
}

QLabel#sectionLabel {
    color: #E8A838;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

QLabel#statusLabel {
    color: #6B7080;
    font-size: 11px;
    padding: 4px 8px;
}

QLabel#titleLabel {
    color: #F0F2F8;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.3px;
}

QLabel#subtitleLabel {
    color: #6B7080;
    font-size: 12px;
    font-weight: 400;
}

QLabel#dropHint {
    color: rgba(232, 168, 56, 0.7);
    font-size: 15px;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════
   LINE EDIT (Text Input)
   ═══════════════════════════════════════════════════════════ */

QLineEdit {
    background: rgba(10, 12, 16, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 14px;
    color: #E0E3EA;
    font-size: 13px;
    min-height: 20px;
}

QLineEdit:focus {
    border-color: rgba(232, 168, 56, 0.5);
    background: rgba(10, 12, 16, 0.8);
}

QLineEdit:hover {
    border-color: rgba(255, 255, 255, 0.15);
}

QLineEdit[readOnly="true"] {
    background: rgba(10, 12, 16, 0.3);
    color: #6B7080;
}

/* ═══════════════════════════════════════════════════════════
   COMBO BOX (Dropdown)
   ═══════════════════════════════════════════════════════════ */

QComboBox {
    background: rgba(10, 12, 16, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 14px;
    color: #E0E3EA;
    font-size: 13px;
    min-height: 20px;
    min-width: 90px;
}

QComboBox:hover {
    border-color: rgba(232, 168, 56, 0.4);
}

QComboBox::drop-down {
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8B90A0;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background: #1E212A;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 4px;
    selection-background-color: rgba(232, 168, 56, 0.2);
    selection-color: #E8A838;
    outline: 0;
}

QComboBox QAbstractItemView::item {
    padding: 6px 12px;
    border-radius: 4px;
    min-height: 24px;
}

QComboBox QAbstractItemView::item:hover {
    background: rgba(232, 168, 56, 0.1);
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════ */

QPushButton {
    background: rgba(40, 44, 56, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 9px 20px;
    color: #C8CBD4;
    font-size: 13px;
    font-weight: 600;
    min-height: 18px;
}

QPushButton:hover {
    background: rgba(55, 60, 75, 0.9);
    border-color: rgba(255, 255, 255, 0.15);
    color: #F0F2F8;
}

QPushButton:pressed {
    background: rgba(35, 38, 48, 0.95);
    border-color: rgba(232, 168, 56, 0.3);
}

QPushButton:disabled {
    background: rgba(30, 33, 42, 0.4);
    color: rgba(139, 144, 160, 0.4);
    border-color: rgba(255, 255, 255, 0.03);
}

/* Primary / accent button */
QPushButton#primaryBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #D4952E,
        stop:1 #E8A838
    );
    border: none;
    color: #1B1D23;
    font-weight: 700;
    padding: 10px 28px;
    font-size: 14px;
}

QPushButton#primaryBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #E8A838,
        stop:1 #F0BD5C
    );
    color: #1B1D23;
}

QPushButton#primaryBtn:pressed {
    background: #C98A28;
}

QPushButton#primaryBtn:disabled {
    background: rgba(232, 168, 56, 0.25);
    color: rgba(27, 29, 35, 0.5);
}

/* Success (green) */
QPushButton#successBtn {
    background: rgba(56, 189, 108, 0.15);
    border: 1px solid rgba(56, 189, 108, 0.3);
    color: #38BD6C;
}

QPushButton#successBtn:hover {
    background: rgba(56, 189, 108, 0.25);
    color: #4DD882;
}

/* Danger (red) */
QPushButton#dangerBtn {
    background: rgba(232, 72, 85, 0.12);
    border: 1px solid rgba(232, 72, 85, 0.25);
    color: #E84855;
}

QPushButton#dangerBtn:hover {
    background: rgba(232, 72, 85, 0.22);
}

/* Icon-like small button */
QPushButton#iconBtn {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 28px;
    max-width: 36px;
    min-height: 28px;
}

QPushButton#iconBtn:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.08);
}

/* ═══════════════════════════════════════════════════════════
   CHECK BOX
   ═══════════════════════════════════════════════════════════ */

QCheckBox {
    spacing: 8px;
    color: #A0A5B2;
    font-size: 12px;
    padding: 4px 0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1.5px solid rgba(255, 255, 255, 0.15);
    background: rgba(10, 12, 16, 0.5);
}

QCheckBox::indicator:hover {
    border-color: rgba(232, 168, 56, 0.5);
}

QCheckBox::indicator:checked {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #D4952E,
        stop:1 #E8A838
    );
    border-color: transparent;
    image: none;
}

QCheckBox::indicator:checked:hover {
    background: #E8A838;
}

/* ═══════════════════════════════════════════════════════════
   TEXT EDIT (Log box / Editor)
   ═══════════════════════════════════════════════════════════ */

QTextEdit {
    background: rgba(8, 10, 14, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 12px 14px;
    color: #B0B5C4;
    font-family: "Cascadia Code", "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 12px;
    line-height: 1.5;
}

QTextEdit:focus {
    border-color: rgba(232, 168, 56, 0.3);
}

QTextEdit#logBox {
    background: rgba(6, 8, 12, 0.8);
    color: #7A8098;
    font-size: 11px;
}

/* ═══════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════ */

QProgressBar {
    background: rgba(10, 12, 16, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    text-align: center;
    color: #8B90A0;
    font-size: 11px;
    font-weight: 600;
    min-height: 14px;
    max-height: 14px;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #D4952E,
        stop:0.5 #E8A838,
        stop:1 #F0BD5C
    );
    border-radius: 5px;
}

/* ═══════════════════════════════════════════════════════════
   STATUS BAR
   ═══════════════════════════════════════════════════════════ */

QStatusBar {
    background: rgba(15, 17, 22, 0.9);
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    color: #5A5F70;
    font-size: 11px;
    padding: 2px 10px;
    min-height: 24px;
}

QStatusBar::item {
    border: none;
}

/* ═══════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════ */

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.15);
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
    height: 10px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(255, 255, 255, 0.15);
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    width: 0;
}

/* ═══════════════════════════════════════════════════════════
   TAB WIDGET
   ═══════════════════════════════════════════════════════════ */

QTabWidget::pane {
    background: transparent;
    border: none;
}

QTabBar::tab {
    background: rgba(30, 33, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 18px;
    margin-right: 2px;
    color: #6B7080;
    font-weight: 600;
    font-size: 12px;
}

QTabBar::tab:selected {
    background: rgba(232, 168, 56, 0.1);
    color: #E8A838;
    border-color: rgba(232, 168, 56, 0.2);
}

QTabBar::tab:hover:!selected {
    background: rgba(40, 44, 56, 0.8);
    color: #A0A5B2;
}

/* ═══════════════════════════════════════════════════════════
   SPLITTER
   ═══════════════════════════════════════════════════════════ */

QSplitter::handle {
    background: rgba(255, 255, 255, 0.04);
    margin: 2px;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

QSplitter::handle:hover {
    background: rgba(232, 168, 56, 0.3);
}

/* ═══════════════════════════════════════════════════════════
   TOOL TIP
   ═══════════════════════════════════════════════════════════ */

QToolTip {
    background: #262A36;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    padding: 6px 10px;
    color: #D4D7DE;
    font-size: 12px;
}

/* ═══════════════════════════════════════════════════════════
   DIALOG
   ═══════════════════════════════════════════════════════════ */

QDialog {
    background: #1A1D25;
}

QMessageBox {
    background: #1A1D25;
}

QMessageBox QLabel {
    color: #D4D7DE;
    font-size: 13px;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ═══════════════════════════════════════════════════════════
   LIST WIDGET (batch file list)
   ═══════════════════════════════════════════════════════════ */

QListWidget {
    background: rgba(8, 10, 14, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 6px;
    outline: 0;
}

QListWidget::item {
    background: rgba(30, 33, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 2px 0;
    color: #C8CBD4;
    font-size: 12px;
}

QListWidget::item:selected {
    background: rgba(232, 168, 56, 0.12);
    border-color: rgba(232, 168, 56, 0.3);
    color: #E8A838;
}

QListWidget::item:hover {
    background: rgba(40, 44, 56, 0.7);
}

/* ═══════════════════════════════════════════════════════════
   FRAME (drop zone)
   ═══════════════════════════════════════════════════════════ */

QFrame#dropZone {
    background: rgba(20, 22, 28, 0.6);
    border: 2px dashed rgba(232, 168, 56, 0.25);
    border-radius: 14px;
    min-height: 100px;
}

QFrame#dropZone:hover {
    border-color: rgba(232, 168, 56, 0.5);
    background: rgba(232, 168, 56, 0.04);
}

/* drop-active state via property */
QFrame[dropActive="true"] {
    border-color: #E8A838;
    background: rgba(232, 168, 56, 0.08);
}

/* ═══════════════════════════════════════════════════════════
   MENU BAR
   ═══════════════════════════════════════════════════════════ */

QMenuBar {
    background: rgba(15, 17, 22, 0.95);
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    padding: 2px 6px;
    color: #8B90A0;
    font-size: 12px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background: rgba(232, 168, 56, 0.12);
    color: #E8A838;
}

QMenu {
    background: #1E212A;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 14px;
    border-radius: 4px;
    color: #C8CBD4;
}

QMenu::item:selected {
    background: rgba(232, 168, 56, 0.15);
    color: #E8A838;
}

QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.06);
    margin: 4px 8px;
}

/* ═══════════════════════════════════════════════════════════
   WEB ENGINE (Editor)
   ═══════════════════════════════════════════════════════════ */

QWebEngineView {
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    background: #0A0C10;
}
"""

# Compact format-type indicator pills for the UI
FORMAT_COLORS: dict[str, str] = {
    "md":   "#61AFEF",
    "txt":  "#8B90A0",
    "html": "#E06C75",
    "rst":  "#C678DD",
    "docx": "#2B7CD3",
    "doc":  "#2B7CD3",
    "odt":  "#56B6C2",
    "rtf":  "#98C379",
    "epub": "#E5C07B",
    "pdf":  "#E84855",
    "pptx": "#D19A66",
    "xlsx": "#1FA553",
    "csv":  "#56B6C2",
    "jpg":  "#E06C75",
    "png":  "#61AFEF",
    "tif":  "#C678DD",
    "bmp":  "#98C379",
}


def format_badge_style(fmt: str) -> str:
    """Return inline style for a small format badge."""
    color = FORMAT_COLORS.get(fmt, "#8B90A0")
    return (
        f"background: {color}20; "
        f"color: {color}; "
        f"border: 1px solid {color}40; "
        f"border-radius: 4px; "
        f"padding: 2px 8px; "
        f"font-size: 11px; "
        f"font-weight: 700; "
        f"text-transform: uppercase;"
    )
