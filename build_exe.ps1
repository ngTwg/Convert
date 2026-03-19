param(
    [switch]$OneFile
)

$entry = "main.py"
$name = "MultiConvert"

$args = @(
    "--noconfirm",
    "--name", $name,
    "--clean",
    "--paths", "src",
    "--collect-all", "PySide6",
    "--hidden-import", "PySide6.QtWebEngineWidgets"
)

if ($OneFile) {
    $args += "--onefile"
}
else {
    $args += "--onedir"
}

$args += $entry

pyinstaller @args
