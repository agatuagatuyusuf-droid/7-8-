; Inno Setup script for AutoDoor Pro
; Requires Inno Setup 6+ (https://jrsoftware.org/isdl.php)

#define MyAppName "AutoDoor Pro"
#define MyAppPublisher "AutoDoor"
#define MyAppURL "https://autodoor.ai"
#define MyAppExeName "AutoDoorPro.exe"

[Setup]
AppId={{B8F7A3D2-9E4C-4F1A-8B5D-6E2C3F1A7B9C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=..\dist\installers
OutputBaseFilename=AutoDoorPro-{#MyAppVersion}-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\dist\autodoor-pro-{#MyAppVersion}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Exclude source code patterns
Source: "..\dist\autodoor-pro-{#MyAppVersion}\CoreService\*"; DestDir: "{app}\CoreService"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\autodoor-pro-{#MyAppVersion}\OCRWorker\OCRWorker.exe"; DestDir: "{app}\OCRWorker"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
