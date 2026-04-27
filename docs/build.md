# Windows-Build

## Ziel

Diese Anleitung beschreibt einen reproduzierbaren Weg, um aus dem Projekt eine Windows-`.exe` zu bauen und zu signieren.

## Voraussetzungen

- Windows
- Python 3.14 oder kompatible lokale Python-Installation
- PyInstaller:

```powershell
python -m pip install pyinstaller
```

- Windows SDK mit `signtool.exe`, wenn signiert werden soll
- Signaturzertifikat im Zertifikatsspeicher des Build-Benutzers
- funktionierender Start mit:

```powershell
python main.py
```

## Empfohlener Build-Weg

Das zentrale Build-Script ist:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

Das Script fuehrt standardmaessig aus:

1. Unit-Tests
2. PyInstaller-Build aus `PasteKeyboard.spec`
3. Kopie nach `dist\PasteKeyboard.exe`
4. Signatur mit SHA256 und DigiCert-Timestamp, wenn ein Thumbprint uebergeben oder per Environment Variable gesetzt ist
5. Signaturpruefung mit `signtool verify /pa /v`, wenn signiert wurde

Ergebnis:

- `dist\PasteKeyboard.exe`
- Laufzeiteinstellungen werden unter `%APPDATA%\PasteKeyboard\settings.json` gespeichert

Ohne Thumbprint wird der Build bewusst ohne Signatur abgeschlossen.

## Signing

Der Zertifikats-Thumbprint wird nicht im Repository gespeichert. Uebergib ihn beim Build per Parameter:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Thumbprint "<SHA1-Thumbprint>"
```

Oder setze ihn lokal als Environment Variable:

```powershell
$env:CODESIGN_THUMBPRINT = "<SHA1-Thumbprint>"
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

In den Windows-Umgebungsvariablen muss `CODESIGN_THUMBPRINT` fuer den Benutzer gesetzt sein, der den Build ausfuehrt. Wenn der Build in einem anderen Benutzer- oder Systemkontext laeuft, setze die Variable als Systemvariable oder uebergib den Wert direkt mit `-Thumbprint`.

Wenn weder `-Thumbprint` noch `CODESIGN_THUMBPRINT` gesetzt ist, baut das Script die EXE ohne Signatur. Der direkte `signtool`-Aufruf entspricht:

```powershell
signtool sign `
  /sha1 "<SHA1-Thumbprint>" `
  /fd SHA256 `
  /tr http://timestamp.digicert.com `
  /td SHA256 `
  "dist\PasteKeyboard.exe"
```

Wenn `signtool.exe` nicht im `PATH` liegt:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SignTool "C:\Pfad\zu\signtool.exe"
```

## Nuetzliche Varianten

Ohne Signing bauen:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SkipSigning
```

Ohne Unit-Tests bauen und signieren:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SkipTests
```

Python explizit setzen:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Python py
```

## Verifizierter Build im aktuellen Workspace

Im aktuellen Workspace wurde der Build erfolgreich ausgefuehrt mit:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SkipTests
```

Verifiziert:

- EXE wurde erzeugt: `dist\PasteKeyboard.exe`
- EXE wurde mit einem lokal bereitgestellten Zertifikats-Thumbprint signiert
- Signatur wurde mit `signtool verify /pa /v` erfolgreich geprueft
- Zeitstempel wurde ueber `http://timestamp.digicert.com` gesetzt
- Nachlaufender Python-Testlauf: `python -m unittest discover -s tests -v`

## Smoke-Test nach dem Build

Nach dem Build sollte mindestens geprueft werden:

1. Startet die GUI?
2. Startet `PasteKeyboard.exe --minimized` minimiert?
3. Laesst sich der globale Hotkey speichern?
4. Funktioniert `Zwischenablage tippen` in Notepad?
5. Stimmen Layout-Auswahl und Sonderzeichenverhalten?

## Typische Stolperstellen

- `signtool.exe` muss ueber `PATH` verfuegbar sein oder per `-SignTool <Pfad>` uebergeben werden.
- Das Signaturzertifikat muss im Zertifikatsspeicher des Build-Benutzers vorhanden sein.
- Unsigned EXEs koennen von SmartScreen oder Defender markiert werden.
- `tkinter` muss in der Python-Installation vorhanden sein.
- Manche Hotkeys sind bereits durch Windows oder andere Tools belegt.
- Das Ziel-Layout in der VM muss zur Auswahl in der App passen.
- Falls Windows das Bearbeiten von EXE-Ressourcen blockiert, nutzt `scripts\build.ps1` automatisch einen PyInstaller-Fallback ohne kosmetische Resource-Updates.
