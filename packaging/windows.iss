[Setup]
AppId=TitulUtil
AppName=Titul Util
AppVersion=1.0.0
DefaultDirName={localappdata}\Programs\TitulUtil
DefaultGroupName=Titul Util
PrivilegesRequired=lowest
OutputDir=..\dist\installers
OutputBaseFilename=TitulUtil-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\TitulUtil.exe

[Files]
Source: "..\dist\TitulUtil\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Titul Util"; Filename: "{app}\TitulUtil.exe"
Name: "{group}\Удалить Titul Util"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\TitulUtil.exe"; Description: "Запустить Titul Util"; Flags: nowait postinstall skipifsilent
