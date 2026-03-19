# MultiConvert 🔄

> **Premium desktop file converter & editor for Windows**
> Convert between 19 input formats and 9 output formats with high quality • Edit output in-app • Batch processing

---

## ✨ Features

### 🔄 Multi-Format Conversion
- **Input (19)**: MD, RST, TXT, HTML, DOCX, DOC, ODT, RTF, EPUB, PDF, PPTX, XLSX, CSV, JPG, PNG, TIF, BMP, GIF, WEBP
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

## 🎁 Hướng dẫn Đóng gói và Phát hành (Release Guide)

### Phương pháp 1: Tạo Windows Installer (KHUYẾN NGHỊ) ⭐

**Tạo file cài đặt chuyên nghiệp như các ứng dụng Windows khác:**

```powershell
powershell -ExecutionPolicy Bypass -File build_installer.ps1 -UseVenv
```

**Yêu cầu tiên quyết:**
- Cài đặt [Inno Setup](https://jrsoftware.org/isdl.php) (miễn phí)

**Quá trình thực hiện:**
1. Tự động build file `MultiConvert.exe` từ source code
2. Tạo Windows Installer (file `.exe`) với giao diện cài đặt chuyên nghiệp
3. Hỗ trợ English + tiếng Việt (nếu máy build có Vietnamese.isl của Inno Setup)
4. Tự động kiểm tra và thông báo về LibreOffice & Tesseract OCR
5. Tạo shortcut trên Desktop và Start Menu
6. Cài đặt uninstaller tự động
7. Tự động lấy version từ `pyproject.toml` (không cần sửa tay trong installer script)

**Kết quả:**
- File installer: `installer_output/MultiConvert_Setup_v<version>.exe` (ví dụ: `installer_output/MultiConvert_Setup_v0.1.0.exe`)
- Người dùng chỉ cần **tải file .exe và chạy** → cài đặt như app bình thường!
- Nhấp đúp 2 lần → hiện giao diện cài đặt → Next → Install → Done!

### Hướng dẫn sử dụng nhanh (đúng quy trình phân phối)

1. Build setup:

```powershell
powershell -ExecutionPolicy Bypass -File build_installer.ps1 -UseVenv
```

2. Lấy file phát hành trong thư mục `installer_output` với tên `MultiConvert_Setup_v<version>.exe`.
3. Gửi file setup này cho người dùng.
4. Người dùng nhấp đúp file setup để cài đặt theo wizard.
5. Ở màn hình cuối, tick tùy chọn Launch để mở app ngay sau khi cài.

---

### Phương pháp 2: Portable ZIP (Không cần cài đặt)

Nếu muốn phân phối dạng ZIP portable (giải nén và chạy):

```powershell
powershell -ExecutionPolicy Bypass -File build_exe.ps1 -UseVenv
```

**Quá trình này sẽ thực hiện:**
1. Tạo một môi trường ảo (`build_venv`) sạch sẽ, giảm dung lượng (từ 1.3GB → ~900MB)
2. Tự động gom các thư viện cần thiết như Pandoc, bộ giao diện PySide6 WebEngine
3. Tạo file `MultiConvert.exe` (đã giấu console window) có kèm icon logo
4. Xuất file hướng dẫn `README.txt` để hỗ trợ người dùng cuối

**Output:**
- Toàn bộ phần mềm trong thư mục `dist\MultiConvert\`
- Nén thành ZIP và gửi cho người dùng
- Người dùng giải nén và nhấp đúp `MultiConvert.exe`

>**Lưu ý:** Thư mục `_internal/` chứa thư viện bắt buộc, phải nằm cùng thư mục với file `.exe`

---

## 🛠️ Trình quản lý chuyển đổi mở rộng (Dành cho người phân phối)

Tool tự động kèm theo Pandoc. Tuy nhiên, một số định dạng sau cần cài thêm Engine:

1. **PDF dạng Scan / Hình ảnh (JPG, PNG, GIF, WEBP) ra Chữ:**
   - Yêu cầu người dùng cài **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki
   - Cài đặt ở thư mục mặc định `C:\Program Files\Tesseract-OCR`
   - MultiConvert sẽ tự động nhận diện và sử dụng
   - **Windows Installer tự động kiểm tra và thông báo** nếu chưa cài

2. **Word (DOC, DOCX), Excel (XLSX, CSV) ra PDF:**
   - MultiConvert dùng **LibreOffice** để xử lý chuyển đổi Office formats
   - Tải tại: https://www.libreoffice.org/
   - **Windows Installer tự động kiểm tra và thông báo** nếu chưa cài

---

## 📦 Build Commands Quick Reference

```powershell
# Build Windows Installer (recommended for distribution)
.\build_installer.ps1 -UseVenv

# Build portable EXE only
.\build_exe.ps1 -UseVenv

# Build installer without rebuilding EXE (if already built)
.\build_installer.ps1 -SkipBuild
```

**Output Locations:**
- EXE: `dist/MultiConvert/MultiConvert.exe`
- Installer: `installer_output/MultiConvert_Setup_v<version>.exe`

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
- Copyright holder: Lê Ngọc Tường, Đại học Khoa học Tự nhiên (HCMUS)
