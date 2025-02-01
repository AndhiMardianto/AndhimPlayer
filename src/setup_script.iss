[Setup]
AppName=AndhimPlayer
AppVersion=1.0 Beta
DefaultDirName={pf}\AndhimPlayer
DefaultGroupName=AndhimPlayer
OutputDir=.
OutputBaseFilename=AndhimPlayer-v1.0-Beta
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\AndhimPlayer\AndhimPlayer.exe"; DestDir: "{app}"
Source: "dist\AndhimPlayer\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs

[Icons]
Name: "{commondesktop}\AndhimPlayer"; Filename: "{app}\AndhimPlayer.exe"
Name: "{userstartmenu}\AndhimPlayer"; Filename: "{app}\AndhimPlayer.exe"

[Registry]
; Menjadikan AndhimPlayer sebagai pemutar media default untuk file audio/video
Root: HKCU; Subkey: "Software\Classes\Applications\AndhimPlayer.exe"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\AndhimPlayer.exe\shell\open\command"; ValueType: string; ValueData: """{app}\AndhimPlayer.exe"" ""%1"""; Flags: uninsdeletevalue

; 🔹 Menambahkan "Open With AndhimPlayer" di menu klik kanan untuk file 🔹
Root: HKCU; Subkey: "Software\Classes\*\shell\OpenWithAndhimPlayer"; ValueType: string; ValueData: "Open with AndhimPlayer"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\OpenWithAndhimPlayer\command"; ValueType: string; ValueData: """{app}\AndhimPlayer.exe"" ""%1"""; Flags: uninsdeletevalue

; 🔹 Menambahkan "Open With AndhimPlayer" di menu klik kanan untuk folder 🔹
Root: HKCU; Subkey: "Software\Classes\Directory\shell\OpenWithAndhimPlayer"; ValueType: string; ValueData: "Open with AndhimPlayer"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\OpenWithAndhimPlayer\command"; ValueType: string; ValueData: """{app}\AndhimPlayer.exe"" ""%1"""; Flags: uninsdeletevalue

; Mendaftarkan AndhimPlayer sebagai aplikasi media yang bisa dipilih oleh pengguna
Root: HKCU; Subkey: "Software\RegisteredApplications\AndhimPlayer"; ValueType: string; ValueData: "Software\Classes\Applications\AndhimPlayer.exe\Capabilities"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\AndhimPlayer.exe\Capabilities"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\AndhimPlayer.exe\Capabilities\FileAssociations"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Applications\AndhimPlayer.exe\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mp3"; ValueData: "AndhimPlayer.mp3"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\Applications\AndhimPlayer.exe\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mp4"; ValueData: "AndhimPlayer.mp4"; Flags: uninsdeletevalue

; Memberikan icon untuk file yang dikaitkan dengan AndhimPlayer
Root: HKCU; Subkey: "Software\Classes\AndhimPlayer.mp3"; ValueType: string; ValueData: "AndhimPlayer MP3 File"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AndhimPlayer.mp3\DefaultIcon"; ValueType: string; ValueData: """{app}\AndhimPlayer.exe"""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\AndhimPlayer.mp3\shell\open\command"; ValueType: string; ValueData: """{app}\AndhimPlayer.exe"" ""%1"""; Flags: uninsdeletevalue

Root: HKCU; Subkey: "Software\Classes\AndhimPlayer.mp4"; ValueType: string; ValueData: "AndhimPlayer MP4 File"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\AndhimPlayer.mp4\DefaultIcon"; ValueType: string; ValueData: """{app}\AndhimPlayer.exe"""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\AndhimPlayer.mp4\shell\open\command"; ValueType: string; ValueData: """{app}\AndhimPlayer.exe"" ""%1"""; Flags: uninsdeletevalue

[Run]
Filename: "{app}\AndhimPlayer.exe"; Description: "Jalankan AndhimPlayer"; Flags: nowait postinstall
