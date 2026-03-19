param(
    [switch]$OneFile,
    [switch]$Clean,
    [switch]$UseVenv
)

$entry    = "main.py"
$name     = "MultiConvert"
$distDir  = "dist\$name"
$toolsDir = "tools"
$venvPyinstaller = ".\build_venv\Scripts\pyinstaller.exe"

# ─── Read version from pyproject.toml (single source of truth) ──
$projectVersion = "0.1.0"
if (Test-Path "pyproject.toml") {
    $versionLine = Get-Content "pyproject.toml" | Select-String -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
    if ($versionLine -and $versionLine.Matches.Count -gt 0) {
        $projectVersion = $versionLine.Matches[0].Groups[1].Value
    }
}

# ─── Determine pyinstaller binary ────────────────────────────
if ($UseVenv -and (Test-Path $venvPyinstaller)) {
    $pyinstallerCmd = $venvPyinstaller
    Write-Host "[i] Using clean venv pyinstaller: $pyinstallerCmd" -ForegroundColor Cyan
} else {
    $pyinstallerCmd = "pyinstaller"
}

# ─── Clean previous build ────────────────────────────────────
if ($Clean -or $UseVenv) {
    Write-Host "Cleaning old build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "build","dist","$name.spec" -ErrorAction SilentlyContinue
}

# ─── Locate LibreOffice ──────────────────────────────────────
$sofficePaths = @(
    "C:\Program Files\LibreOffice\program",
    "C:\Program Files (x86)\LibreOffice\program"
)
$loDir = $null
foreach ($p in $sofficePaths) {
    if (Test-Path "$p\soffice.exe") { $loDir = $p; break }
}

# ─── Locate Tesseract ────────────────────────────────────────
$tessDir = $null
$tessPaths = @("C:\Program Files\Tesseract-OCR", "C:\Program Files (x86)\Tesseract-OCR")
foreach ($p in $tessPaths) {
    if (Test-Path "$p\tesseract.exe") { $tessDir = $p; break }
}

# ─── Base PyInstaller arguments ─────────────────────────────
$pyArgs = @(
    "--noconfirm",
    "--clean",
    "--name", $name,
    "--paths", "src",
    "--hidden-import", "PySide6.QtWebEngineWidgets",
    "--hidden-import", "PySide6.QtWebEngineCore",
    "--hidden-import", "PySide6.QtWebChannel",
    "--hidden-import", "PySide6.QtNetwork",
    "--hidden-import", "pypandoc",
    "--hidden-import", "pytesseract",
    "--hidden-import", "pdf2image",
    "--hidden-import", "PIL",
    "--hidden-import", "docx",
    "--collect-all", "pypandoc",
    "--collect-all", "PySide6",
    "--exclude-module", "PyQt5",
    "--exclude-module", "PyQt6",
    "--exclude-module", "tkinter",
    "--exclude-module", "matplotlib",
    "--exclude-module", "scipy",
    "--exclude-module", "numpy"
)

if ($OneFile) {
    $pyArgs += "--onefile"
} else {
    $pyArgs += "--onedir"
}

# ─── Hide Console & Set Icon ─────────────────────────────────
$pyArgs += "--windowed"
if (Test-Path "tools\logo.ico") {
    $pyArgs += "--icon=tools\logo.ico"
}

# ─── Bundle Poppler ──────────────────────────────────────────
$popplerBin = "tools\poppler\bin"
if (Test-Path $popplerBin) {
    Write-Host "[+] Bundling Poppler: $popplerBin" -ForegroundColor Cyan
    $pyArgs += "--add-data"; $pyArgs += "$popplerBin;tools/poppler/bin"
} else {
    Write-Host "[!] Poppler not found at $popplerBin - PDF OCR may be limited" -ForegroundColor Yellow
}

# ─── Bundle Tesseract tessdata ───────────────────────────────
if ($tessDir) {
    $tessdata = "$tessDir\tessdata"
    if (Test-Path $tessdata) {
        Write-Host "[+] Bundling Tesseract tessdata from: $tessdata" -ForegroundColor Cyan
        $pyArgs += "--add-data"; $pyArgs += "$tessdata;tessdata"
    }
    Write-Host "[i] Tesseract exe at: $tessDir (system install, auto-detected at runtime)" -ForegroundColor Cyan
} else {
    Write-Host "[!] Tesseract not found - OCR will require manual install" -ForegroundColor Yellow
}

# ─── Note about LibreOffice ──────────────────────────────────
if ($loDir) {
    Write-Host "[i] LibreOffice found: $loDir (auto-detected at runtime)" -ForegroundColor Cyan
} else {
    Write-Host "[!] LibreOffice not found - office format conversion requires separate install" -ForegroundColor Yellow
}

$pyArgs += $entry

# ─── Run PyInstaller ─────────────────────────────────────────
Write-Host ""
Write-Host "Running PyInstaller ($pyinstallerCmd)..." -ForegroundColor Green
& $pyinstallerCmd @pyArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller failed!" -ForegroundColor Red
    exit 1
}

# ─── Post-build: Copy tools/ into dist ───────────────────────
if (-not $OneFile) {
    if (Test-Path $toolsDir) {
        Write-Host "Copying tools/ to distribution..." -ForegroundColor Cyan
        if (-not (Test-Path "$distDir\_internal")) { New-Item -ItemType Directory "$distDir\_internal" | Out-Null }
        Copy-Item -Recurse -Force $toolsDir "$distDir\_internal\"
    }

    $readmeContent = @"
MultiConvert - Công Cụ Chuyển Đổi Tài Liệu Tiếng Việt v$projectVersion
==========================================================
Copyright: Lê Ngọc Tường, Đại học Khoa học Tự nhiên (HCMUS)

HƯỚNG DẪN SỬ DỤNG:
- Chỉ cần chạy file MultiConvert.exe để sử dụng ngay.

CÁC BỘ CHUYỂN ĐỔI ĐÃ TÍCH HỢP SẴN (Không cần cài đặt gì thêm):
  * Pandoc 3.x  - Chuyển đổi giữa MD, RST, TXT, HTML, DOCX, ODT, RTF, EPUB
  * Poppler      - Chuyển PDF thành dạng ảnh (dành cho OCR)

CÁC BỘ CHUYỂN ĐỔI MỞ RỘNG (Cài 1 lần, phần mềm sẽ tự nhận diện):
  * LibreOffice  -> https://www.libreoffice.org/
    Giúp chuyển đổi: DOC, PPTX, XLSX, CSV <-> PDF và các định dạng Office khác
    
  * Tesseract OCR -> https://github.com/UB-Mannheim/tesseract/wiki  
    Giúp nhận diện chữ: JPG, PNG, TIF, BMP, PDF scan -> TXT, MD, HTML, DOCX
    Gói Tiếng Việt: Tải file vie.traineddata bỏ vào thư mục Tesseract-OCR\tessdata\

CÁC ĐỊNH DẠNG HỖ TRỢ HIỆN TẠI:
  MD, RST, TXT, HTML, DOCX, DOC, ODT, RTF, EPUB, PDF, PPTX, XLSX, CSV
  + Hình ảnh (JPG, PNG, TIF, BMP, GIF, WEBP) sử dụng OCR

TÍNH NĂNG NỔI BẬT:
  * Kéo & Thả nhiều file trực tiếp vào ứng dụng
  * Chuyển đổi hàng loạt nhiều file cùng một lúc
  * Chỉnh sửa trực tiếp file bằng trình soạn thảo nội bộ ngay trong app
  * Lưu và Xuất file vừa chỉnh sửa ra mọi định dạng văn bản

"@
    $readmeContent | Out-File "$distDir\README.txt" -Encoding UTF8
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
if (-not $OneFile) {
    $exeSize = [math]::Round((Get-Item "$distDir\$name.exe").Length / 1MB, 1)
    $totalSize = [math]::Round((Get-ChildItem $distDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
    Write-Host "Output folder: $(Resolve-Path $distDir)" -ForegroundColor White
    Write-Host "Launcher:      $name.exe ($exeSize MB)" -ForegroundColor White
    Write-Host "Total size:    $totalSize MB" -ForegroundColor White
    Write-Host ""
    Write-Host "To run: .\dist\$name\$name.exe" -ForegroundColor Cyan
} else {
    $exeSize = [math]::Round((Get-Item "dist\$name.exe").Length / 1MB, 1)
    Write-Host "Single exe: $(Resolve-Path "dist\$name.exe") ($exeSize MB)" -ForegroundColor White
}
