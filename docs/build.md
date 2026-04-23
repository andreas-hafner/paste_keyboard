# Windows-Build

## Ziel

Diese Anleitung beschreibt einen reproduzierbaren Weg, um aus dem Projekt eine Windows-`.exe` zu bauen.

## Voraussetzungen

- Windows
- Python 3.14 oder kompatible lokale Python-Installation
- funktionierender Start mit:

```powershell
python main.py
```

## Empfohlener Build-Weg

Für dieses Projekt ist `PyInstaller` der pragmatischste Weg.

Installation:

```powershell
python -m pip install pyinstaller
```

Build:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --paths src --name PasteKeyboard main.py
```

Ergebnis:

- `dist/PasteKeyboard.exe`
- Laufzeiteinstellungen werden unter `%APPDATA%\\PasteKeyboard\\settings.json` gespeichert

## Verifizierter Build im aktuellen Workspace

Im aktuellen Workspace wurde der Build erfolgreich ausgeführt mit:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --paths src --name PasteKeyboard main.py
```

Verifiziert:

- EXE wurde erzeugt: `dist/PasteKeyboard.exe`
- Größe im aktuellen Lauf: ca. 9,26 MB
- Smoke-Test: EXE startet die GUI erfolgreich, der Fenstertitel ist `Paste Keyboard`
- Nachlaufender Python-Testlauf: `python -m unittest discover -s tests -v`

## Smoke-Test nach dem Build

Nach dem Build sollte mindestens geprüft werden:

1. Startet die GUI?
2. Lässt sich der globale Hotkey speichern?
3. Funktioniert `Zwischenablage tippen` in Notepad?
4. Stimmen Layout-Auswahl und Sonderzeichenverhalten?

## Typische Stolperstellen

- Unsigned EXEs können von SmartScreen oder Defender markiert werden.
- `tkinter` muss in der Python-Installation vorhanden sein.
- Manche Hotkeys sind bereits durch Windows oder andere Tools belegt.
- Das Ziel-Layout in der VM muss zur Auswahl in der App passen.

## Aktueller Stand im Workspace

`PyInstaller` ist in der aktuellen Umgebung installiert und der Build wurde bereits erfolgreich getestet. Für spätere Änderungen sollte der Build nach GUI- oder Packaging-Änderungen erneut einmal lokal geprüft werden.
