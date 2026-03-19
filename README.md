# MultiConvert 🔄

> **Premium desktop file converter & editor for Windows**
> Convert between 12+ document formats with high quality • Edit output in-app • Batch processing

---

## ✨ Features

### 🔄 Multi-Format Conversion
- **Input**: MD, RST, TXT, HTML, DOCX, DOC, ODT, RTF, EPUB, PDF, PNG, JPG, TIF, BMP
- **Output**: MD, TXT, HTML, DOCX, ODT, RTF, EPUB, PDF, CSV
- **Auto-routing**: If no direct converter exists (e.g., `md→pdf`), automatically chains through intermediates (`md→html→pdf`)

### ✏️ In-App WYSIWYG Editor
- Rich text editing with **Bold**, *Italic*, ~~Strikethrough~~
- Headings (H1-H3), bullet/numbered lists, blockquotes
- Insert links, undo/redo
- Import any file → edit as HTML → export to any format

### 📥 Drag & Drop
- Drop single or multiple files onto the app
- Automatic batch queue for multiple files

### ⚡ Batch Processing
- Convert entire folders of files at once
- Parallel processing with progress tracking

### 🔍 OCR Support
- Extract text from scanned PDFs and images
- Multi-language support (Vietnamese + English default)

### 🎨 Premium Dark UI
- JetBrains Fleet-inspired dark slate theme
- Warm amber accent colors
- Smooth animations and micro-interactions

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| GUI | PySide6 + QWebEngineView |
| Text Engine | Pandoc ≥ 3.1 |
| Office Engine | LibreOffice 7+ (headless) |
| OCR Engine | Tesseract + pytesseract + pdf2image |
| Packaging | PyInstaller |

---

## 🚀 Quick Start

### 1. Setup environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

### 2. Install external engines

| Engine | Required? | Install |
|--------|-----------|---------|
| **Pandoc** | ✅ Core | [pandoc.org/installing](https://pandoc.org/installing.html) |
| **LibreOffice** | ✅ Office files | [libreoffice.org](https://www.libreoffice.org/) |
| **Tesseract OCR** | 📷 For OCR | [github.com/tesseract-ocr](https://github.com/tesseract-ocr/tesseract) |
| **Poppler** | 📷 PDF→images | [poppler utils](https://github.com/oschwartz10612/poppler-windows/releases) |

> Make sure all engines are in your `PATH`, or configure via environment variables:
> - `MULTICONVERT_PANDOC` → path to `pandoc.exe`
> - `MULTICONVERT_SOFFICE` → path to `soffice.exe`
> - `TESSERACT_CMD` → path to `tesseract.exe`

### 3. Launch GUI

```powershell
python main.py --gui
```

### 4. CLI Usage

```powershell
# Single file conversion
python main.py --input report.docx --to pdf --output report.pdf --open

# With OCR
python main.py --input scan.pdf --to docx --ocr --ocr-lang vie+eng

# List available formats
python main.py --list-formats
```

---

## 📦 Build .exe

```powershell
pip install pyinstaller
.\build_exe.ps1           # folder build (recommended)
.\build_exe.ps1 -OneFile  # single .exe (slower startup)
```

Output: `dist/MultiConvert/`

---

## 🏗️ Architecture

```
MultiConvert
├── app.py                    # Entry point (CLI / GUI)
├── manager.py                # Route planner (weighted graph)
├── models.py                 # ConversionRequest / Result
├── formats.py                # Format registry & detection
├── errors.py                 # ConversionError
├── plugin_loader.py          # Load built-in + external plugins
├── converters/
│   ├── base.py               # BaseConverter ABC
│   ├── pandoc_converter.py   # Pandoc (md, html, docx, epub…)
│   ├── libreoffice_converter.py  # LibreOffice headless
│   └── ocr_converter.py      # Tesseract OCR
└── ui/
    ├── main_window.py        # Premium dark GUI
    ├── editor_dialog.py      # WYSIWYG editor (QWebEngineView)
    ├── worker.py             # Background thread worker
    └── theme.py              # Dark slate + amber QSS stylesheet
```

### Conversion Flow

```
Input File → Detect Format → Find Route (graph search)
  → Step 1: Converter A (md → html)
  → Step 2: Converter B (html → pdf)
  → Output File
```

### Plugin System

Drop a `.py` file in a plugins folder with:

```python
def get_converter():
    return YourConverterSubclass()
```

Then pass `--plugin-dir ./plugins` to load them.

---

## 📊 Format Compatibility Matrix

| From \ To | md | txt | html | docx | odt | rtf | epub | pdf |
|-----------|:--:|:---:|:----:|:----:|:---:|:---:|:----:|:---:|
| **md**    | -  | ✅  | ✅   | ✅   | ✅  | ✅  | ✅   | ✅  |
| **txt**   | ✅ | -   | ✅   | ✅   | ✅  | ✅  | ✅   | ✅  |
| **html**  | ✅ | ✅  | -    | ✅   | ✅  | ✅  | ✅   | ✅  |
| **docx**  | ✅ | ✅  | ✅   | -    | ✅  | ✅  | ✅   | ✅  |
| **odt**   | ✅ | ✅  | ✅   | ✅   | -   | ✅  | ✅   | ✅  |
| **rtf**   | ✅ | ✅  | ✅   | ✅   | ✅  | -   | ✅   | ✅  |
| **epub**  | ✅ | ✅  | ✅   | ✅   | ✅  | ✅  | -    | ✅  |
| **pdf***  | ✅ | ✅  | ✅   | ✅   | ✅  | ✅  | ✅   | -   |
| **images**| ✅ | ✅  | ✅   | ✅   |     |     |      |     |

> *PDF input requires text-layer or OCR for scanned documents

---

## ⚠️ Known Limitations

- **PDF → editable**: Layout fidelity ~80-90% for text PDFs, lower for complex layouts
- **Macro files** (`.docm`, `.xlsm`): Macros are not preserved
- **RTL languages**: May need additional LaTeX packages for PDF output
- **Multiple LibreOffice instances**: Queued (semaphore=1) to prevent crashes

---

## 📄 License

- Pandoc: GPL
- LibreOffice: LGPL
- Tesseract: Apache 2.0
- MultiConvert: MIT
