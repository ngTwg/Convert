"""
MultiConvert – Rich In-App Editor Dialog
Uses QWebEngineView with a contenteditable HTML editor,
plus a toolbar for basic formatting.
Import: Any supported format → HTML → edit → Export to any format.
"""
from __future__ import annotations

import html as html_module
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from multiconvert.formats import detect_format
from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest

# Try to import QWebEngineView; fall back to QTextEdit if unavailable
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebChannel import QWebChannel
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False


# ─── Embedded WYSIWYG HTML ─────────────────────────────────────
EDITOR_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  :root {
    --bg: #0F1116;
    --fg: #D4D7DE;
    --accent: #E8A838;
    --border: rgba(255,255,255,0.06);
    --toolbar-bg: #1A1D25;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--fg);
    font-family: "Segoe UI", "SF Pro Text", sans-serif;
    font-size: 15px;
    line-height: 1.7;
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  /* ─── Toolbar ─── */
  .toolbar {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 8px 14px;
    background: var(--toolbar-bg);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    flex-wrap: wrap;
  }

  .toolbar button {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 6px;
    color: #A0A5B2;
    font-size: 13px;
    padding: 5px 10px;
    cursor: pointer;
    transition: all 0.15s ease;
    font-family: inherit;
  }

  .toolbar button:hover {
    background: rgba(232,168,56,0.12);
    color: var(--accent);
    border-color: rgba(232,168,56,0.3);
  }

  .toolbar button:active {
    background: rgba(232,168,56,0.2);
  }

  .toolbar .sep {
    width: 1px;
    height: 22px;
    background: var(--border);
    margin: 0 6px;
  }

  /* ─── Editor Area ─── */
  #editor {
    flex: 1;
    padding: 28px 36px;
    overflow-y: auto;
    outline: none;
    cursor: text;
  }

  #editor:focus {
    outline: none;
  }

  /* Rich text styling */
  #editor h1 { font-size: 1.8em; font-weight: 800; color: #F0F2F8; margin: 0.6em 0 0.3em; }
  #editor h2 { font-size: 1.4em; font-weight: 700; color: #E0E3EA; margin: 0.5em 0 0.25em; }
  #editor h3 { font-size: 1.15em; font-weight: 600; color: #C8CBD4; margin: 0.4em 0 0.2em; }
  #editor p { margin: 0.5em 0; }
  #editor ul, #editor ol { margin: 0.5em 0 0.5em 1.5em; }
  #editor li { margin: 0.2em 0; }
  #editor blockquote {
    border-left: 3px solid var(--accent);
    padding: 8px 16px;
    margin: 0.8em 0;
    background: rgba(232,168,56,0.05);
    color: #B0B5C4;
  }
  #editor pre {
    background: rgba(0,0,0,0.3);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
    font-family: "Cascadia Code", "JetBrains Mono", monospace;
    font-size: 13px;
    overflow-x: auto;
    margin: 0.8em 0;
  }
  #editor code {
    background: rgba(232,168,56,0.1);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: "Cascadia Code", "JetBrains Mono", monospace;
    font-size: 0.9em;
    color: var(--accent);
  }
  #editor a { color: #61AFEF; text-decoration: underline; }
  #editor img { max-width: 100%%; border-radius: 8px; margin: 0.5em 0; }
  #editor table {
    border-collapse: collapse;
    margin: 0.8em 0;
    width: 100%%;
  }
  #editor th, #editor td {
    border: 1px solid var(--border);
    padding: 8px 12px;
    text-align: left;
  }
  #editor th { background: rgba(255,255,255,0.04); font-weight: 600; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
</style>
</head>
<body>

<div class="toolbar">
  <button onclick="fmt('bold')" title="Bold (Ctrl+B)"><b>B</b></button>
  <button onclick="fmt('italic')" title="Italic (Ctrl+I)"><i>I</i></button>
  <button onclick="fmt('underline')" title="Underline (Ctrl+U)"><u>U</u></button>
  <button onclick="fmt('strikeThrough')" title="Strikethrough"><s>S</s></button>
  <div class="sep"></div>
  <button onclick="fmt('formatBlock','<h1>')" title="Heading 1">H1</button>
  <button onclick="fmt('formatBlock','<h2>')" title="Heading 2">H2</button>
  <button onclick="fmt('formatBlock','<h3>')" title="Heading 3">H3</button>
  <button onclick="fmt('formatBlock','<p>')" title="Paragraph">¶</button>
  <div class="sep"></div>
  <button onclick="fmt('insertUnorderedList')" title="Bullet list">• List</button>
  <button onclick="fmt('insertOrderedList')" title="Numbered list">1. List</button>
  <button onclick="fmt('formatBlock','<blockquote>')" title="Blockquote">❝ Quote</button>
  <div class="sep"></div>
  <button onclick="insertLink()" title="Insert link">🔗 Link</button>
  <button onclick="fmt('removeFormat')" title="Clear formatting">✕ Clear</button>
  <div class="sep"></div>
  <button onclick="fmt('undo')" title="Undo (Ctrl+Z)">↩ Undo</button>
  <button onclick="fmt('redo')" title="Redo (Ctrl+Y)">↪ Redo</button>
</div>

<div id="editor" contenteditable="true">
%s
</div>

<script>
function fmt(cmd, val) {
  document.execCommand(cmd, false, val || null);
  document.getElementById('editor').focus();
}

function insertLink() {
  var url = prompt('Nhập link (URL):');
  if (url) {
    document.execCommand('createLink', false, url);
  }
}

function getContent() {
  return document.getElementById('editor').innerHTML;
}

function setContent(html) {
  document.getElementById('editor').innerHTML = html;
}
</script>
</body>
</html>"""


class EditorDialog(QDialog):
    """Rich in-app editor with WYSIWYG toolbar and export."""

    def __init__(self, manager: ConverterManager, file_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"✏️  Sửa file: {file_path.name}")
        self.resize(1060, 780)
        self._manager = manager
        self._file_path = file_path
        self._format = detect_format(file_path) or "txt"
        self._html_content = ""

        self._build_ui()
        self._load_file()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # ── Web editor or fallback text editor ──
        if HAS_WEBENGINE:
            self.web_editor = QWebEngineView()
            layout.addWidget(self.web_editor)
            self._use_web = True
        else:
            from PySide6.QtWidgets import QTextEdit
            self.text_editor = QTextEdit()
            self.text_editor.setAcceptRichText(True)
            layout.addWidget(self.text_editor)
            self._use_web = False

        # ── Export controls ──
        export_row = QHBoxLayout()
        export_row.addWidget(QLabel("Xuất file sang dạng"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(
            sorted(["md", "txt", "html", "docx", "odt", "rtf", "pdf", "epub"])
        )
        self.target_combo.setCurrentText("pdf")
        export_row.addWidget(self.target_combo)

        self.export_path = QLineEdit(
            str(self._file_path.with_name(self._file_path.stem + "_edited.pdf"))
        )
        export_row.addWidget(self.export_path)

        self.btn_pick_export = QPushButton("📁 Chọn Thư Mục")
        export_row.addWidget(self.btn_pick_export)
        layout.addLayout(export_row)

        # ── Action buttons ──
        action_row = QHBoxLayout()
        self.btn_save = QPushButton("💾  Lưu")
        action_row.addWidget(self.btn_save)

        self.btn_export = QPushButton("⚡  Lưu và Xuất file")
        self.btn_export.setObjectName("primaryBtn")
        action_row.addWidget(self.btn_export)

        self.btn_close = QPushButton("Đóng")
        action_row.addWidget(self.btn_close)
        layout.addLayout(action_row)

        # ── Bind ──
        self.btn_pick_export.clicked.connect(self._pick_export_file)
        self.btn_save.clicked.connect(self._save_only)
        self.btn_export.clicked.connect(self._save_and_export)
        self.btn_close.clicked.connect(self.close)
        self.target_combo.currentTextChanged.connect(self._update_export_ext)

    def _load_file(self) -> None:
        """Load the file and convert to HTML for editing."""
        content = self._file_path.read_text(encoding="utf-8", errors="replace")

        if self._format == "html":
            self._html_content = content
        elif self._format == "md":
            # Convert markdown to HTML for the WYSIWYG editor
            try:
                import pypandoc
                self._html_content = pypandoc.convert_text(content, "html", format="markdown")
            except Exception:
                # Simple fallback: wrap in paragraphs
                paragraphs = content.split("\n\n")
                self._html_content = "".join(
                    f"<p>{html_module.escape(p)}</p>" for p in paragraphs if p.strip()
                )
        elif self._format in ("rst",):
            try:
                import pypandoc
                self._html_content = pypandoc.convert_text(content, "html", format="rst")
            except Exception:
                self._html_content = f"<pre>{html_module.escape(content)}</pre>"
        else:
            # txt or any other: wrap in pre
            self._html_content = f"<pre>{html_module.escape(content)}</pre>"

        if self._use_web:
            full_html = EDITOR_HTML_TEMPLATE % self._html_content
            self.web_editor.setHtml(full_html, QUrl("about:blank"))
        else:
            self.text_editor.setHtml(self._html_content)

    def _update_export_ext(self) -> None:
        target = self.target_combo.currentText()
        current = Path(self.export_path.text())
        self.export_path.setText(str(current.with_suffix(f".{target}")))

    def _pick_export_file(self) -> None:
        target = self.target_combo.currentText()
        selected, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file xuất ra tại",
            self.export_path.text(),
            f"*.{target}",
        )
        if selected:
            self.export_path.setText(selected)

    def _save_only(self) -> None:
        try:
            self._do_save()
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi khi lưu file", str(exc))
            return
        QMessageBox.information(self, "Đã lưu", "Đã lưu nội dung chỉnh sửa thành công.")

    def _save_and_export(self) -> None:
        try:
            self._do_save()
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi khi lưu file", str(exc))
            return

        target_path = Path(self.export_path.text())
        target_format = self.target_combo.currentText()

        try:
            # Export from the saved (HTML) file to target format
            request = ConversionRequest(
                source=self._file_path,
                destination=target_path,
                source_format=self._format,
                target_format=target_format,
            )
            result = self._manager.convert(request)
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi khi xuất file", str(exc))
            return

        QMessageBox.information(
            self, "Hoàn tất", f"Đã xuất file ra:\n{result.destination}"
        )

    def _do_save(self) -> None:
        """Extract content from editor and write back to file."""
        if self._use_web:
            # Use JavaScript to get the edited HTML
            self.web_editor.page().runJavaScript(
                "getContent()", self._save_content_callback
            )
        else:
            if self._format == "html":
                text = self.text_editor.toHtml()
            elif self._format == "md" and hasattr(self.text_editor, "toMarkdown"):
                text = self.text_editor.toMarkdown()
            else:
                text = self.text_editor.toPlainText()
            self._file_path.write_text(text, encoding="utf-8")

    @Slot(str)
    def _save_content_callback(self, content: str) -> None:
        """Callback after JS returns the editor content."""
        if self._format == "html":
            # Save as full HTML
            full = f"<html><body>{content}</body></html>"
            self._file_path.write_text(full, encoding="utf-8")
        elif self._format == "md":
            # Convert HTML back to Markdown
            try:
                import pypandoc
                md_text = pypandoc.convert_text(content, "markdown", format="html")
                self._file_path.write_text(md_text, encoding="utf-8")
            except Exception:
                self._file_path.write_text(content, encoding="utf-8")
        else:
            # For txt/rst, save the HTML (will be converted on export)
            self._file_path.write_text(content, encoding="utf-8")
