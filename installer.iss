; MultiConvert Installer Script for Inno Setup
; This creates a professional Windows installer with proper installation dialogs
; Download Inno Setup from: https://jrsoftware.org/isdl.php

#define MyAppName "MultiConvert"
#ifndef MyAppVersion
  #define MyAppVersion "0.2.0"
#endif
#define MyAppPublisher "Lê Ngọc Tường - Đại học Khoa học Tự nhiên (HCMUS)"
#define MyAppURL "https://github.com/ngTwg/Convert"
#define MyAppExeName "MultiConvert.exe"
#define MyAppDescription "Premium multi-format file converter - 35+ input formats, 25+ output formats"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright=Copyright (C) 2024-2026 {#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
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
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription={#MyAppDescription}

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
Name: "quicklaunchicon"; Description: "Create a &Quick Launch icon"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "download_lo"; Description: "Download and Install LibreOffice (Required for Office→PDF conversion)"; GroupDescription: "Optional Tools (Recommended if not installed):"; Flags: unchecked
Name: "download_ocr"; Description: "Download and Install Tesseract OCR (Required for OCR from images/scanned PDFs)"; GroupDescription: "Optional Tools (Recommended if not installed):"; Flags: unchecked

[Files]
; Main application files
Source: "dist\{#MyAppName}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "{#MyAppDescription}"

[Registry]
; Register application path
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
; Install downloaded tools silently if downloaded - Check file exists first
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\LibreOffice.msi"" /qn"; Tasks: download_lo; StatusMsg: "Installing LibreOffice (Please wait, this may take 3-5 minutes)..."; Check: FileExists(ExpandConstant('{tmp}\LibreOffice.msi'))
Filename: "{tmp}\Tesseract.exe"; Parameters: "/S"; Tasks: download_ocr; StatusMsg: "Installing Tesseract OCR..."; Check: FileExists(ExpandConstant('{tmp}\Tesseract.exe'))

[Code]
var
  DownloadPage: TDownloadWizardPage;
  NeedsDownload: Boolean;

function CheckLibreOffice(): Boolean;
var
  Path1, Path2, Path3: String;
begin
  Path1 := ExpandConstant('{commonpf}\LibreOffice\program\soffice.exe');
  Path2 := ExpandConstant('{commonpf32}\LibreOffice\program\soffice.exe');
  Path3 := ExpandConstant('{localappdata}\Programs\LibreOffice\program\soffice.exe');
  Result := FileExists(Path1) or FileExists(Path2) or FileExists(Path3);
end;

function CheckTesseract(): Boolean;
var
  Path1, Path2, Path3: String;
begin
  Path1 := ExpandConstant('{commonpf}\Tesseract-OCR\tesseract.exe');
  Path2 := ExpandConstant('{commonpf32}\Tesseract-OCR\tesseract.exe');
  Path3 := ExpandConstant('{localappdata}\Programs\Tesseract-OCR\tesseract.exe');
  Result := FileExists(Path1) or FileExists(Path2) or FileExists(Path3);
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
  NeedsDownload := False;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpSelectTasks then
  begin
    // Disable tasks if already installed
    if CheckLibreOffice() then
      WizardForm.TasksList.ItemEnabled[2] := False; // 'download_lo' index adjusted
    if CheckTesseract() then
      WizardForm.TasksList.ItemEnabled[3] := False; // 'download_ocr' index adjusted
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    NeedsDownload := False;

    // LibreOffice 24.2.x (latest stable as of 2024)
    if IsTaskSelected('download_lo') and not CheckLibreOffice() then begin
      DownloadPage.Add('https://download.documentfoundation.org/libreoffice/stable/24.2.5/win/x86_64/LibreOffice_24.2.5_Win_x86-64.msi', ExpandConstant('{tmp}\LibreOffice.msi'), '');
      NeedsDownload := True;
    end;

    // Tesseract 5.3.3 (latest stable)
    if IsTaskSelected('download_ocr') and not CheckTesseract() then begin
      DownloadPage.Add('https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe', ExpandConstant('{tmp}\Tesseract.exe'), '');
      NeedsDownload := True;
    end;

    if NeedsDownload then
    begin
      DownloadPage.Show;
      try
        try
          DownloadPage.Download;
          Result := True;
        except
          if DownloadPage.AbortedByUser then
            Log('Download aborted by user.')
          else begin
            // Show warning but continue installation without optional tools
            MsgBox('Could not download optional tools. The main application will still be installed. You can install LibreOffice and Tesseract manually later.', mbInformation, MB_OK);
          end;
          Result := True; // Continue installation anyway
        end;
      finally
        DownloadPage.Hide;
      end;
    end;
  end;
end;
