; MultiConvert Installer Script for Inno Setup
; This creates a professional Windows installer with proper installation dialogs
; Download Inno Setup from: https://jrsoftware.org/isdl.php

#define MyAppName "MultiConvert"
#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif
#define MyAppPublisher "Lê Ngọc Tường - Đại học Khoa học Tự nhiên (HCMUS)"
#define MyAppURL "https://github.com/ngTwg/Convert"
#define MyAppExeName "MultiConvert.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
OutputDir=installer_output
OutputBaseFilename=MultiConvert_Setup_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

#ifexist "tools\logo.ico"
SetupIconFile=tools\logo.ico
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
#ifexist "C:\Program Files (x86)\Inno Setup 6\Languages\Vietnamese.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"
#endif

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main application files
Source: "dist\{#MyAppName}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DependencyPage: TOutputMsgMemoWizardPage;
  LibreOfficeInstalled: Boolean;
  TesseractInstalled: Boolean;

function CheckLibreOffice(): Boolean;
var
  Path1, Path2: String;
begin
  Path1 := ExpandConstant('{commonpf}\LibreOffice\program\soffice.exe');
  Path2 := ExpandConstant('{commonpf32}\LibreOffice\program\soffice.exe');
  Result := FileExists(Path1) or FileExists(Path2);
end;

function CheckTesseract(): Boolean;
var
  Path1, Path2: String;
begin
  Path1 := ExpandConstant('{commonpf}\Tesseract-OCR\tesseract.exe');
  Path2 := ExpandConstant('{commonpf32}\Tesseract-OCR\tesseract.exe');
  Result := FileExists(Path1) or FileExists(Path2);
end;

procedure InitializeWizard;
begin
  DependencyPage := CreateOutputMsgMemoPage(wpWelcome,
    'Kiểm Tra Phụ Thuộc / Dependency Check',
    'Công cụ chuyển đổi bổ sung / Optional Conversion Engines',
    'MultiConvert có thể hoạt động với các bộ chuyển đổi sau để mở rộng khả năng:' + #13#10 + #13#10 +
    'MultiConvert can work with the following optional engines for enhanced capabilities:' + #13#10 + #13#10,
    '');

  LibreOfficeInstalled := CheckLibreOffice();
  TesseractInstalled := CheckTesseract();

  DependencyPage.RichEditViewer.Lines.Add('✓ PANDOC - Tích hợp sẵn (Bundled)');
  DependencyPage.RichEditViewer.Lines.Add('  Chuyển đổi: MD, HTML, DOCX, EPUB, ODT, RTF, TXT');
  DependencyPage.RichEditViewer.Lines.Add('');

  if LibreOfficeInstalled then
    DependencyPage.RichEditViewer.Lines.Add('✓ LIBREOFFICE - Đã cài đặt (Installed)')
  else begin
    DependencyPage.RichEditViewer.Lines.Add('✗ LIBREOFFICE - Chưa cài đặt (Not Installed)');
    DependencyPage.RichEditViewer.Lines.Add('  Khuyến nghị: Tải tại https://www.libreoffice.org/');
    DependencyPage.RichEditViewer.Lines.Add('  Recommended: Download from https://www.libreoffice.org/');
  end;
  DependencyPage.RichEditViewer.Lines.Add('  Chức năng: Chuyển đổi DOC, PPTX, XLSX → PDF');
  DependencyPage.RichEditViewer.Lines.Add('  Feature: Convert DOC, PPTX, XLSX → PDF');
  DependencyPage.RichEditViewer.Lines.Add('');

  if TesseractInstalled then
    DependencyPage.RichEditViewer.Lines.Add('✓ TESSERACT OCR - Đã cài đặt (Installed)')
  else begin
    DependencyPage.RichEditViewer.Lines.Add('✗ TESSERACT OCR - Chưa cài đặt (Not Installed)');
    DependencyPage.RichEditViewer.Lines.Add('  Khuyến nghị: Tải tại https://github.com/UB-Mannheim/tesseract/wiki');
    DependencyPage.RichEditViewer.Lines.Add('  Recommended: Download from https://github.com/UB-Mannheim/tesseract/wiki');
  end;
  DependencyPage.RichEditViewer.Lines.Add('  Chức năng: Nhận diện chữ từ ảnh (JPG, PNG) và PDF scan');
  DependencyPage.RichEditViewer.Lines.Add('  Feature: OCR from images (JPG, PNG) and scanned PDFs');
  DependencyPage.RichEditViewer.Lines.Add('');
  DependencyPage.RichEditViewer.Lines.Add('─────────────────────────────────────────────');
  DependencyPage.RichEditViewer.Lines.Add('');
  DependencyPage.RichEditViewer.Lines.Add('Lưu ý: Bạn có thể cài đặt các công cụ này sau.');
  DependencyPage.RichEditViewer.Lines.Add('Note: You can install these tools later.');
  DependencyPage.RichEditViewer.Lines.Add('MultiConvert sẽ tự động phát hiện khi chúng được cài đặt.');
  DependencyPage.RichEditViewer.Lines.Add('MultiConvert will automatically detect them when installed.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Additional post-install tasks can be added here
  end;
end;
