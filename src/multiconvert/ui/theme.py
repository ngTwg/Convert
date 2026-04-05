"""
MultiConvert – Vibrant Modern Theme
Dynamic, professional design with vibrant accents, smooth hover effects, and premium feel.
"""

DARK_THEME_QSS = """
/* ═══════════════════════════════════════════════════════════
   GLOBAL - Modern Typography, No Borders
   ═══════════════════════════════════════════════════════════ */

* {
    font-family: "Inter", "Segoe UI Variable", "SF Pro Display", system-ui, sans-serif;
    font-size: 13px;
    color: #E2E8F0;
    selection-background-color: #3B82F6;
    selection-color: #FFFFFF;
}

QMainWindow, QWidget#centralWidget {
    background-color: #0F172A;
}

QWidget {
    background: transparent;
}

/* ═══════════════════════════════════════════════════════════
   LABELS & TEXT
   ═══════════════════════════════════════════════════════════ */
QLabel { color: #CBD5E1; font-weight: 500; }
QLabel#titleLabel { color: #FFFFFF; font-size: 24px; font-weight: 800; letter-spacing: 0.5px; }

/* ═══════════════════════════════════════════════════════════
   INPUTS & COMBOBOX - Soft Backgrounds, No Frames
   ═══════════════════════════════════════════════════════════ */
QLineEdit, QComboBox, QTextEdit {
    background-color: rgba(255, 255, 255, 0.04);
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 6px;
    padding: 10px 14px;
    color: #F8FAFC;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    background-color: rgba(255, 255, 255, 0.08);
    border-bottom: 2px solid #3B82F6;
    border-bottom-left-radius: 2px;
    border-bottom-right-radius: 2px;
}

QLineEdit:hover, QComboBox:hover {
    background-color: rgba(255, 255, 255, 0.06);
}

QComboBox::drop-down {
    border: none;
    width: 32px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #94A3B8;
    margin-right: 12px;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    border: none;
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #3B82F6;
    selection-color: #FFFFFF;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 10px;
    border-radius: 4px;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS - Soft Pill Shapes
   ═══════════════════════════════════════════════════════════ */
QPushButton {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    color: #F8FAFC;
    font-weight: 600;
}

QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
QPushButton:pressed { background-color: rgba(255, 255, 255, 0.02); }

QPushButton#primaryBtn, QPushButton:default {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #3B82F6);
    color: #FFFFFF;
    padding: 12px 28px;
}
QPushButton#primaryBtn:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #60A5FA); }
QPushButton#primaryBtn:disabled { background: rgba(255, 255, 255, 0.05); color: #64748B; }

/* ═══════════════════════════════════════════════════════════
   CHECKBOX - Modern Indicators
   ═══════════════════════════════════════════════════════════ */
QCheckBox { spacing: 10px; color: #CBD5E1; font-weight: 500; }
QCheckBox::indicator {
    width: 20px; height: 20px;
    border-radius: 6px;
    border: none;
    background-color: rgba(255, 255, 255, 0.08);
}
QCheckBox::indicator:hover { background-color: rgba(255, 255, 255, 0.15); }
QCheckBox::indicator:checked {
    background-color: #3B82F6;
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIzIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik01IDEybDUgNSAxMC0xMCIvPjwvc3ZnPg==);
}

/* ═══════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════ */
QProgressBar {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #FFFFFF;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #34D399);
    border-radius: 4px;
}

/* ═══════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 6px; margin: 2px; border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.2); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

/* ═══════════════════════════════════════════════════════════
   DROP ZONE
   ═══════════════════════════════════════════════════════════ */
QFrame#dropZone {
    background-color: rgba(255, 255, 255, 0.02);
    border: none;
    border-radius: 16px;
}
QFrame#dropZone:hover { background-color: rgba(255, 255, 255, 0.05); }
QFrame[dropActive="true"] { background-color: rgba(59, 130, 246, 0.15); }

/* ═══════════════════════════════════════════════════════════
   SPLITTER & OTHERS
   ═══════════════════════════════════════════════════════════ */
QSplitter::handle { background: transparent; }
QMenu {
    background-color: #1E293B;
    border: none;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item { padding: 8px 24px 8px 12px; border-radius: 4px; }
QMenu::item:selected { background-color: rgba(255, 255, 255, 0.1); }
QStatusBar { background: transparent; color: #94A3B8; border: none; }
QDialog, QMessageBox { background-color: #0F172A; }
"""

FORMAT_COLORS: dict[str, str] = {
    "pdf":  "#F43F5E",
    "docx": "#3B82F6",
    "doc":  "#3B82F6",
    "txt":  "#94A3B8",
    "md":   "#10B981",
    "html": "#F59E0B",
    "epub": "#8B5CF6",
    "odt":  "#06B6D4",
    "rtf":  "#64748B",
}

def format_badge_style(fmt: str) -> str:
    """Return inline style for a vibrant badge."""
    color = FORMAT_COLORS.get(fmt, "#64748B")
    return (
        f"background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15); "
        f"color: {color}; "
        f"border: 1px solid {color}; "
        f"border-radius: 4px; "
        f"padding: 2px 8px; "
        f"font-size: 10px; "
        f"font-weight: 700; "
        f"text-transform: uppercase; "
        f"letter-spacing: 0.5px;"
    )
