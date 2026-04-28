# Nutzung aus dem Quellcode

Diese Datei beschreibt den Start und die manuelle Pruefung aus dem Repository heraus. Die vollstaendige Anleitung fuer ausgelieferte Nutzer der fertigen EXE steht in der [Endanwender-Anleitung](enduser.md).

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

## Einstellungen

Die App speichert ihre Einstellungen pro Benutzer unter:

```text
%APPDATA%\PasteKeyboard\settings.json
```

Diese Datei wird sowohl beim Start aus dem Quellcode als auch bei der gebauten EXE verwendet.

## Typischer Entwicklungs-Check

1. App mit `python main.py` starten.
2. Ziel-Layout passend zum Testziel auswaehlen.
3. Hotkey, Startverzoegerung und Tastendelay bei Bedarf anpassen.
4. `Einstellungen speichern` klicken.
5. Text in die Zwischenablage kopieren.
6. Testziel fokussieren.
7. Hotkey druecken oder die Eingabe ueber die GUI starten.

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
- ein sehr langer Text mit mehr als `1000` Zeichen fuer den Clipboard-Guard

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
