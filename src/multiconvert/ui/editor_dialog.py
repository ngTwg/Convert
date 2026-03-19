from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from multiconvert.formats import detect_format
from multiconvert.manager import ConverterManager
from multiconvert.models import ConversionRequest


class EditorDialog(QDialog):
    def __init__(self, manager: ConverterManager, file_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Edit: {file_path.name}")
        self.resize(980, 720)
        self._manager = manager
        self._file_path = file_path
        self._format = detect_format(file_path) or "txt"

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)

        self.target_combo = QComboBox()
        self.target_combo.addItems(
            sorted(["md", "txt", "html", "docx", "odt", "rtf", "pdf", "epub"])
        )
        self.target_combo.setCurrentText("pdf")

        self.export_path = QLineEdit(str(file_path.with_name(file_path.stem + "_edited.pdf")))
        self.btn_pick_export = QPushButton("Browse")
        self.btn_save = QPushButton("Save")
        self.btn_export = QPushButton("Save + Export")
        self.btn_close = QPushButton("Close")

        layout = QVBoxLayout()
        layout.addWidget(self.editor)

        export_row = QHBoxLayout()
        export_row.addWidget(QLabel("Export to"))
        export_row.addWidget(self.target_combo)
        export_row.addWidget(self.export_path)
        export_row.addWidget(self.btn_pick_export)
        layout.addLayout(export_row)

        action_row = QHBoxLayout()
        action_row.addWidget(self.btn_save)
        action_row.addWidget(self.btn_export)
        action_row.addWidget(self.btn_close)
        layout.addLayout(action_row)
        self.setLayout(layout)

        self.btn_pick_export.clicked.connect(self._pick_export_file)
        self.btn_save.clicked.connect(self._save_only)
        self.btn_export.clicked.connect(self._save_and_export)
        self.btn_close.clicked.connect(self.close)

        self._load_file()

    def _load_file(self) -> None:
        content = self._file_path.read_text(encoding="utf-8", errors="replace")
        if self._format == "html":
            self.editor.setHtml(content)
            self.editor.setAcceptRichText(True)
            return
        if self._format == "md" and hasattr(self.editor, "setMarkdown"):
            self.editor.setMarkdown(content)
            return
        self.editor.setPlainText(content)

    def _pick_export_file(self) -> None:
        target = self.target_combo.currentText()
        selected, _ = QFileDialog.getSaveFileName(
            self,
            "Export destination",
            self.export_path.text(),
            f"*.{target}",
        )
        if selected:
            self.export_path.setText(selected)

    def _save_only(self) -> None:
        try:
            self._save_editor_content()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Save failed", str(exc))
            return
        QMessageBox.information(self, "Saved", "Edited content has been saved.")

    def _save_and_export(self) -> None:
        try:
            self._save_editor_content()
            target_path = Path(self.export_path.text())
            target_format = self.target_combo.currentText()
            request = ConversionRequest(
                source=self._file_path,
                destination=target_path,
                source_format=self._format,
                target_format=target_format,
            )
            result = self._manager.convert(request)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Export failed", str(exc))
            return
        QMessageBox.information(self, "Done", f"Exported to:\n{result.destination}")

    def _save_editor_content(self) -> None:
        if self._format == "html":
            text = self.editor.toHtml()
        elif self._format == "md" and hasattr(self.editor, "toMarkdown"):
            text = self.editor.toMarkdown()
        else:
            text = self.editor.toPlainText()
        self._file_path.write_text(text, encoding="utf-8")
