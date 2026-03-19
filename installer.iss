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
Name: "download_lo"; Description: "Tải và Cài đặt thêm LibreOffice (Cần thiết để chuyển Office sang PDF)"; GroupDescription: "Công cụ bổ sung (Khuyên dùng nếu chưa có):"; Flags: unchecked
Name: "download_ocr"; Description: "Tải và Cài đặt thêm Tesseract OCR (Cần thiết để quét chữ từ ảnh/PDF scan)"; GroupDescription: "Công cụ bổ sung (Khuyên dùng nếu chưa có):"; Flags: unchecked

[Files]
; Main application files
Source: "dist\{#MyAppName}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
; Install downloaded tools silently if downloaded
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\LibreOffice.msi"" /qn"; Tasks: download_lo; StatusMsg: "Đang cài đặt LibreOffice (Vui lòng chờ, quá trình này mất khoảng 3-5 phút)..."
Filename: "{tmp}\Tesseract.exe"; Parameters: "/S"; Tasks: download_ocr; StatusMsg: "Đang cài đặt Tesseract OCR..."

[Code]
var
  DownloadPage: TDownloadWizardPage;

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
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpSelectTasks then
  begin
    // Disable tasks if already installed
    if CheckLibreOffice() then
      WizardForm.TasksList.ItemEnabled[1] := False; // 'download_lo' is 2nd item (index 1) usually if desktopicon is 0
    if CheckTesseract() then
      WizardForm.TasksList.ItemEnabled[2] := False; // 'download_ocr' is 3rd item
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    if IsTaskSelected('download_lo') and not CheckLibreOffice() then
      DownloadPage.Add('https://download.documentfoundation.org/libreoffice/stable/7.6.6/win/x86_64/LibreOffice_7.6.6_Win_x86-64.msi', ExpandConstant('{tmp}\LibreOffice.msi'), '');
    if IsTaskSelected('download_ocr') and not CheckTesseract() then
      DownloadPage.Add('https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe', ExpandConstant('{tmp}\Tesseract.exe'), '');
    
    if DownloadPage.Msg1Label.Caption <> '' then // Meaning files were added
    begin
      DownloadPage.Show;
      try
        try
          DownloadPage.Download;
          Result := True;
        except
          if DownloadPage.AbortedByUser then
            Log('Aborted by user.')
          else
            MsgBox('Lỗi khi tải xuống các gói bổ sung. Vui lòng kiểm tra lại mạng.', mbError, MB_OK);
          Result := False; // Stop installation if download fails
        end;
      finally
        DownloadPage.Hide;
      end;
    end else
      Result := True;
  end else
    Result := True;
end;
