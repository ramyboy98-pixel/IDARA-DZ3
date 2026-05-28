; IDARA DZ Installer
; Built by GitHub Actions using Inno Setup

#define MyAppName "IDARA DZ"
#define MyAppVersion "1.1"
#define MyAppPublisher "Mohammed BELKEBIR ABDELKARIM"
#define MyAppExeName "IDARA DZ.exe"

[Setup]
AppId={{B8F72A90-7E2D-4A23-9A71-IDARADZ11000}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\IDARA DZ
DefaultGroupName=IDARA DZ
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=IDARA_DZ_Setup_v1.1
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\dist\IDARA DZ\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\IDARA DZ"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\IDARA DZ"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Run IDARA DZ"; Flags: nowait postinstall skipifsilent
