param(
    [switch]$SkipBuild,
    [switch]$UseVenv,
    [string]$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  MultiConvert - Windows Installer Builder" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ─── Read version from pyproject.toml (single source of truth) ──
$projectVersion = "0.1.0"
if (Test-Path "pyproject.toml") {
    $versionLine = Get-Content "pyproject.toml" | Select-String -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
    if ($versionLine -and $versionLine.Matches.Count -gt 0) {
        $projectVersion = $versionLine.Matches[0].Groups[1].Value
    }
}

Write-Host "[i] Installer version: $projectVersion" -ForegroundColor Cyan
Write-Host ""

# ─── Step 1: Build the EXE if not skipped ───────────────────────
if (-not $SkipBuild) {
    Write-Host "[1/3] Building MultiConvert.exe..." -ForegroundColor Green
    Write-Host ""

    $buildArgs = @()
    if ($UseVenv) {
        $buildArgs += "-UseVenv"
    }

    & powershell -ExecutionPolicy Bypass -File "build_exe.ps1" @buildArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "✗ EXE build failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "✓ EXE build completed successfully" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[1/3] Skipping EXE build (using existing dist folder)" -ForegroundColor Yellow
    Write-Host ""
}

# ─── Step 2: Verify dist folder exists ──────────────────────────
$distFolder = "dist\MultiConvert"
if (-not (Test-Path $distFolder)) {
    Write-Host "✗ Error: dist\MultiConvert folder not found!" -ForegroundColor Red
    Write-Host "  Please build the EXE first or remove -SkipBuild flag" -ForegroundColor Yellow
    exit 1
}

# ─── Step 3: Check for Inno Setup ───────────────────────────────
Write-Host "[2/3] Checking for Inno Setup..." -ForegroundColor Green
Write-Host ""

# Try to find Inno Setup in common locations
$innoSetupLocations = @(
    $InnoSetupPath,
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe"
)

$iscc = $null
foreach ($location in $innoSetupLocations) {
    if (Test-Path $location) {
        $iscc = $location
        break
    }
}

if (-not $iscc) {
    Write-Host "✗ Inno Setup not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Inno Setup from:" -ForegroundColor Yellow
    Write-Host "  https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or specify custom path with:" -ForegroundColor Yellow
    Write-Host "  .\build_installer.ps1 -InnoSetupPath 'C:\Path\To\ISCC.exe'" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "✓ Found Inno Setup: $iscc" -ForegroundColor Green
Write-Host ""

# ─── Step 4: Build the installer ────────────────────────────────
Write-Host "[3/3] Building Windows installer..." -ForegroundColor Green
Write-Host ""

& $iscc "/DMyAppVersion=$projectVersion" "installer.iss"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Installer build failed!" -ForegroundColor Red
    exit 1
}

# ─── Step 5: Success! ────────────────────────────────────────────
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✓ INSTALLER BUILD COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

$installerPath = Get-ChildItem "installer_output\MultiConvert_Setup_v$projectVersion.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($installerPath) {
    $installerSize = [math]::Round($installerPath.Length / 1MB, 1)
    Write-Host "Installer: $(Resolve-Path $installerPath.FullName)" -ForegroundColor White
    Write-Host "Size:      $installerSize MB" -ForegroundColor White
    Write-Host ""
    Write-Host "Người dùng chỉ cần tải file này và chạy để cài đặt!" -ForegroundColor Cyan
    Write-Host "Users just need to download and run this file to install!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installer features:" -ForegroundColor Yellow
    Write-Host "  ✓ Professional installation wizard (English + optional Vietnamese)" -ForegroundColor White
    Write-Host "  ✓ Auto-detect LibreOffice and Tesseract OCR" -ForegroundColor White
    Write-Host "  ✓ Desktop shortcut creation (optional)" -ForegroundColor White
    Write-Host "  ✓ Start menu integration" -ForegroundColor White
    Write-Host "  ✓ Proper uninstaller" -ForegroundColor White
    Write-Host "  ✓ Double-click to install like any Windows app" -ForegroundColor White
    Write-Host ""
}
