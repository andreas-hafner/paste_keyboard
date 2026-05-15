# Source Usage

German guide: [usage.md](usage.md)

This file describes how to run and manually test the app from the repository. The full guide for users of the delivered EXE is in the [End User Guide](enduser.en.md).

## Requirements

- Windows
- Python 3.14 or a compatible local Python installation
- `tkinter` in the Python installation

## Start

From the repository:

```powershell
python main.py
```

Start minimized:

```powershell
python main.py --minimized
```

With `--minimized`, the app starts directly in the Windows notification area. The main window is not shown as a normal taskbar button; use the tray icon to open or exit it.

Only one instance can run at the same time. If an instance is already active, the second start exits after a short message.

## Settings

The app stores settings per user:

```text
%APPDATA%\PasteKeyboard\settings.json
```

The same file is used when running from source and from the built EXE. The settings include app language, hotkey, target layout, delays, clipboard limit, skip behavior, and notification preference.

## Typical Development Check

1. Start the app with `python main.py`.
2. Select German or English in `Language`.
3. Select the target layout for the test target.
4. Capture a hotkey with `Record` or keep the existing hotkey.
5. Adjust start delay, key delay, clipboard limit, and notification preference if needed.
6. Click `Save settings`.
7. Copy text to the clipboard.
8. Focus the test target.
9. Press the hotkey or start typing through the GUI.

Useful test targets:

- Notepad
- browser `textarea`
- Proxmox/noVNC console

Recommended test texts:

- `Hello World`
- `aeoeueAeOeUeSs`
- `@ EUR { } [ ] \ | ~ ^`
- multi-line text
- tabs
- text longer than the configured clipboard limit
- enabled `Notify after typing`, to check the local finish popup

## Update Screenshots

Screenshots in `docs/screenshots` can be regenerated from the workspace:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_screenshots.ps1
```

The script starts an isolated app instance with test settings under `build\screenshot-appdata` and renders:

- `docs\screenshots\01-main-window.png`
- `docs\screenshots\02-text-loaded.png`

## Tests

Unit tests:

```powershell
python -m unittest discover -s tests -v
```

## Build

The EXE is built through the build script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

Details are in the [Windows Build Guide](build.en.md).
