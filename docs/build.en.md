# Windows Build

German guide: [build.md](build.md)

## Goal

This guide describes a reproducible way to build and optionally sign a Windows `.exe` from this project.

## Requirements

- Windows
- Python 3.14 or a compatible local Python installation
- PyInstaller:

```powershell
python -m pip install pyinstaller
```

- Windows SDK with `signtool.exe`, if signing is required
- signing certificate in the certificate store of the build user, if signing is required
- Microsoft Edge or Google Chrome for PDF guide generation
- working app start with:

```powershell
python main.py
```

## Recommended Build

The central build script is:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

By default, the script runs:

1. unit tests
2. PyInstaller build from `PasteKeyboard.spec`
3. copy to `dist\PasteKeyboard.exe`
4. German PDF guide generation to `dist\PasteKeyboard-Anleitung.pdf`
5. English PDF guide generation to `dist\PasteKeyboard-Guide.pdf`
6. SHA256 signing with DigiCert timestamp, if a thumbprint is passed or configured through an environment variable
7. signature verification with `signtool verify /pa /v`, if signing was performed

Result:

- `dist\PasteKeyboard.exe`
- `dist\PasteKeyboard-Anleitung.pdf`
- `dist\PasteKeyboard-Guide.pdf`
- runtime settings under `%APPDATA%\PasteKeyboard\settings.json`

Without a thumbprint, the build intentionally finishes unsigned.

## Signing

The certificate thumbprint is not stored in the repository. Pass it as a parameter:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Thumbprint "<SHA1-Thumbprint>"
```

Or set it locally as an environment variable:

```powershell
$env:CODESIGN_THUMBPRINT = "<SHA1-Thumbprint>"
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

`CODESIGN_THUMBPRINT` must be available to the user running the build. If the build runs under another user or system context, set the variable there or pass the value directly with `-Thumbprint`. Spaces in the thumbprint are removed by the build script.

If neither `-Thumbprint` nor `CODESIGN_THUMBPRINT` is set, the EXE is built without a signature.

If `signtool.exe` is not in `PATH`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SignTool "C:\Path\to\signtool.exe"
```

## Useful Variants

Build without signing:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SkipSigning
```

Build without unit tests:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SkipTests
```

Set Python explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Python py
```

Skip PDF documentation:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -SkipDocs
```

Build only one PDF manually:

```powershell
python scripts\build_docs_pdf.py --source docs\enduser.en.md --output dist\PasteKeyboard-Guide.pdf --lang en --title "Paste Keyboard Guide"
```

## Smoke Test After Build

At minimum, check:

1. Does the GUI start?
2. Does `PasteKeyboard.exe --minimized` start minimized?
3. Are both PDF guides next to the EXE in `dist` and readable?
4. Does the app prevent a second parallel instance?
5. Can the global hotkey be recorded and saved?
6. Is an occupied hotkey rejected visibly without blocking the field?
7. Does `Type clipboard` work in Notepad?
8. Does the configured clipboard limit apply?
9. Does the local popup appear after completion when notifications are enabled?
10. Do German and English UI labels switch correctly?
11. Do target layout and special character behavior match expectations?

## Common Pitfalls

- `signtool.exe` must be available through `PATH` or passed with `-SignTool <path>`.
- The signing certificate must exist in the certificate store of the build user.
- Unsigned EXEs can be flagged by SmartScreen or Defender.
- `tkinter` must be present in the Python installation.
- Some hotkeys are already used by Windows or other tools.
- Hotkey recording reads the current physical keyboard state; during recording, the field is read-only and the active global hotkey is paused briefly.
- App language and target keyboard layout are separate settings.
- The target layout must match the layout in the VM or remote system.
- PDF generation requires Edge or Chrome in the default install path or in `PATH`.
- If Windows blocks EXE resource updates, `scripts\build.ps1` automatically uses a PyInstaller fallback without cosmetic resource updates.
