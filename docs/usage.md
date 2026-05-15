# Nutzung aus dem Quellcode

Diese Datei beschreibt den Start und die manuelle Pruefung aus dem Repository heraus. Die vollstaendige Anleitung fuer ausgelieferte Nutzer der fertigen EXE steht in der [Endanwender-Anleitung](enduser.md).

English guide: [usage.en.md](usage.en.md)

## Voraussetzungen

- Windows
- Python 3.14 oder kompatible lokale Python-Installation
- `tkinter` in der Python-Installation

## Starten

Aus dem Repository:

```powershell
python main.py
```

Minimiert starten:

```powershell
python main.py --minimized
```

Mit `--minimized` startet die App direkt im Windows-Infobereich. Das Hauptfenster erscheint dann nicht als normaler Taskleisten-Button; geoeffnet und beendet wird die App ueber das Tray-Symbol.

Es kann nur eine Instanz gleichzeitig laufen. Wenn bereits eine Instanz aktiv ist, beendet sich der zweite Start nach einem kurzen Hinweis.

## Einstellungen

Die App speichert ihre Einstellungen pro Benutzer unter:

```text
%APPDATA%\PasteKeyboard\settings.json
```

Diese Datei wird sowohl beim Start aus dem Quellcode als auch bei der gebauten EXE verwendet.
Gespeichert werden auch die App-Sprache, der Hotkey, das Ziel-Layout, Delays, Zwischenablage-Limit, Zeichenverhalten und Benachrichtigungsoption.

## Typischer Entwicklungs-Check

1. App mit `python main.py` starten.
2. Deutsch oder Englisch unter `Sprache` waehlen.
3. Ziel-Layout passend zum Testziel auswaehlen.
4. Hotkey mit `Aufzeichnen` uebernehmen oder vorhandenen Hotkey beibehalten.
5. Startverzoegerung, Tastendelay, Zwischenablage-Limit und Benachrichtigung bei Bedarf anpassen.
6. `Einstellungen speichern` klicken.
7. Text in die Zwischenablage kopieren.
8. Testziel fokussieren.
9. Hotkey druecken oder die Eingabe ueber die GUI starten.

Sinnvolle Testziele:

- Notepad
- Browser-`textarea`
- Proxmox/noVNC-Konsole

Empfohlene Testtexte:

- `Hello World`
- `aeoeueAeOeUeSs`
- `@ EUR { } [ ] \ | ~ ^`
- mehrzeiliger Text
- Tabs
- ein sehr langer Text oberhalb des eingestellten Zwischenablage-Limits fuer den Clipboard-Guard
- aktivierte `Benachrichtigung nach Tippvorgang`, um das lokale Abschluss-Popup zu pruefen

## Screenshots aktualisieren

Die Screenshots in `docs/screenshots` koennen aus dem Workspace heraus neu erzeugt werden:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_screenshots.ps1
```

Das Script startet eine isolierte App-Instanz mit eigenen Test-Einstellungen unter `build\screenshot-appdata` und rendert:

- `docs\screenshots\01-main-window.png`
- `docs\screenshots\02-text-loaded.png`

## Tests

Unit-Tests:

```powershell
python -m unittest discover -s tests -v
```

## Build

Die gebaute EXE wird ueber das Build-Script erzeugt:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

Details stehen in der [Windows-Build-Anleitung](build.md).

## Bedienung der EXE

Alles zur Bedienung der ausgelieferten App, Windows-Autostart, Zwischenablage, Layout-Empfehlungen und Fehlersuche steht in der [Endanwender-Anleitung](enduser.md).
