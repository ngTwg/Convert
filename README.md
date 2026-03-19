# MultiConvert (.exe-ready desktop converter)

MultiConvert is a Python desktop app for Windows that converts between common text/office/ebook formats and supports in-app editing for text-like outputs.

## What this starter already includes

- Plugin-based conversion engine (`Pandoc`, `LibreOffice`, `OCR` adapter).
- Route planner (auto multi-hop conversion when no direct pair exists).
- Desktop GUI (PySide6):
  - choose input/output
  - run conversion
  - open output directly
  - edit output in-app for `md/txt/html/rst`, then export again
- CLI mode for scripting and batch workflows.
- Build script for `pyinstaller`.

## Supported formats (practical baseline)

- Input candidates: `md, rst, txt, html, docx, doc, odt, rtf, epub, pdf, png, jpg, tif, bmp`
- Output candidates: `md, txt, html, docx, odt, rtf, epub, pdf, csv`
- Real availability depends on installed engines:
  - `pandoc` for text/ebook conversions
  - `soffice` (LibreOffice headless) for office-heavy conversion paths
  - `tesseract + pytesseract (+ pdf2image)` for OCR flows

## Quick start

1. Create venv and install deps:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

2. Install external engines and put them in `PATH`:

- `pandoc`
- `LibreOffice` (must expose `soffice`)
- Optional OCR:
  - `tesseract-ocr`
  - `poppler` (for `pdf2image` on Windows)

3. Launch GUI:

```powershell
python main.py --gui
```

4. Or use CLI:

```powershell
python main.py --input sample.docx --to pdf --output sample.pdf --open
python main.py --list-formats
```

## Build .exe

```powershell
pip install pyinstaller
.\build_exe.ps1
```

- Default output: `dist/MultiConvert/`
- One-file build:

```powershell
.\build_exe.ps1 -OneFile
```

## Architecture summary

- `ConverterManager` builds a format graph from active converters and finds best route by weighted shortest path.
- Each converter implements:
  - `supported_pairs()`
  - `available()`
  - `convert(...)`
- Flow:
  - Detect source/target format
  - Plan route (example: `md -> html -> pdf`)
  - Execute each step in isolated process command
  - Return final file and route log

## External plugin example

Drop a `.py` file in your plugin folder and pass `--plugin-dir`.
The module must expose:

```python
def get_converter():
    return YourConverterSubclass()
```

## Quality caveats

- `docx/html/md` roundtrip can be high quality with proper templates/styles.
- `pdf -> editable` will always lose some layout fidelity, especially scanned PDFs.
- Macro-enabled files (`docm/xlsm`) are not preserved in conversion output.
- For production quality:
  - add golden-file tests
  - add template presets
  - add queue control to avoid running multiple `soffice` instances at once.
