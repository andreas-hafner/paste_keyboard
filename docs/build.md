# Windows-Build

## Ziel

Diese Anleitung beschreibt einen reproduzierbaren Weg, um aus dem Projekt eine Windows-`.exe` zu bauen.

## GitHub CI/CD

Im Repository ist ein GitHub-Actions-Workflow unter `.github/workflows/cicd.yml` hinterlegt.

Ablauf:

1. Bei jedem Push und bei jedem Pull Request startet ein Build auf `windows-latest`.
2. Der Runner fuehrt die Unit-Tests aus und baut anschliessend mit `PyInstaller`.
3. Die erzeugte EXE wird als ZIP-Datei verpackt und als Workflow-Artefakt hochgeladen.
4. Wenn ein GitHub Release veroeffentlicht wird, werden das ZIP und die aktuelle Endanwender-Anleitung als Release-Assets angehaengt.

Wichtig:

- Der Workflow deckt CI und CD in einer Datei ab.
- Der Release-Upload reagiert auf veroeffentlichte Releases, nicht nur auf Tags.
- Fuer das Hochladen wird der eingebaute `GITHUB_TOKEN` mit `contents: write` verwendet.
- Das Release-Asset heisst `PasteKeyboard-windows.zip`.
- Die Endanwender-Anleitung wird als `docs/enduser.md` aus dem aktuellen Commit an das Release angehaengt.

## Releases und Versionierung

Dieses Projekt verwendet Semantic Versioning (SemVer).

Regeln:

- `MAJOR` fuer inkompatible Aenderungen
- `MINOR` fuer neue, rueckwaertskompatible Funktionen
- `PATCH` fuer Bugfixes und kleine Korrekturen

Beispiele:

- `0.1.1` fuer einen reinen Fix-Release
- `0.2.0` fuer neue Funktionen ohne Breaking Changes
- `1.0.0` fuer die erste stabile Hauptversion

Release-Ablauf:

1. Die Versionsnummer in `pyproject.toml` anheben.
2. Die Aenderung committen und nach `main` pushen.
3. Das Release mit passendem Tag erstellen.
4. GitHub Actions baut danach automatisch die Windows-Datei und haengt die Release-Assets an.

Beispiel:

```bash
git add pyproject.toml
git commit -m "release: bump version to 0.1.1"
git push origin main
gh release create v0.1.1 --title "v0.1.1" --notes "Bugfix release."
```

Wichtig:

- Tag und Projektversion muessen zusammenpassen.
- Wenn in `pyproject.toml` `0.1.1` steht, sollte das Release-Tag `v0.1.1` sein.
- Das Release laedt aktuell `PasteKeyboard-windows.zip` und `enduser.md` hoch.

## Voraussetzungen

- Windows
- Python 3.14 oder kompatible lokale Python-Installation
- funktionierender Start mit:

```powershell
python main.py
```

## Empfohlener Build-Weg

Fuer dieses Projekt ist `PyInstaller` der pragmatischste Weg.

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

Im aktuellen Workspace wurde der Build erfolgreich ausgefuehrt mit:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --paths src --name PasteKeyboard main.py
```

Verifiziert:

- EXE wurde erzeugt: `dist/PasteKeyboard.exe`
- Groesse im aktuellen Lauf: ca. 9,26 MB
- Smoke-Test: EXE startet die GUI erfolgreich, der Fenstertitel ist `Paste Keyboard`
- Nachlaufender Python-Testlauf: `python -m unittest discover -s tests -v`

## Smoke-Test nach dem Build

Nach dem Build sollte mindestens geprueft werden:

1. Startet die GUI?
2. Laesst sich der globale Hotkey speichern?
3. Funktioniert `Zwischenablage tippen` in Notepad?
4. Stimmen Layout-Auswahl und Sonderzeichenverhalten?

## Typische Stolperstellen

- Unsigned EXEs koennen von SmartScreen oder Defender markiert werden.
- `tkinter` muss in der Python-Installation vorhanden sein.
- Manche Hotkeys sind bereits durch Windows oder andere Tools belegt.
- Das Ziel-Layout in der VM muss zur Auswahl in der App passen.

## Aktueller Stand im Workspace

`PyInstaller` ist in der aktuellen Umgebung installiert und der Build wurde bereits erfolgreich getestet. Fuer spaetere Aenderungen sollte der Build nach GUI- oder Packaging-Aenderungen erneut einmal lokal geprueft werden.
