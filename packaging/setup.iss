; Inno Setup Script for Chat TTS Multi-Platform
; Version: 2.2.1

[Setup]
AppId={{C6E2A3B4-D8E9-4A0B-B1C2-E3F4A5B6C7D8}
AppName=Chat TTS Multi-Platform
AppVersion=2.2.1
AppPublisher=Chat TTS Team
DefaultDirName={autopf}\ChatTTS
DefaultGroupName=Chat TTS Multi-Platform
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..
OutputBaseFilename=ChatTTS-v2.2.1-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "thai"; MessagesFile: "compiler:Languages\Thai.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ChatTTS.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\ChatTTS-CLI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\manual_th.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\docs\ai_recommendations.md"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{group}\Chat TTS Multi-Platform"; Filename: "{app}\ChatTTS.exe"
Name: "{group}\Chat TTS CLI Mode"; Filename: "{app}\ChatTTS-CLI.exe"
Name: "{group}\{cm:UninstallProgram,Chat TTS Multi-Platform}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Chat TTS Multi-Platform"; Filename: "{app}\ChatTTS.exe"; Tasks: desktopicon
Name: "{autodesktop}\Chat TTS CLI"; Filename: "{app}\ChatTTS-CLI.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ChatTTS.exe"; Description: "{cm:LaunchProgram,Chat TTS Multi-Platform}"; Flags: nowait postinstall skipifsilent
