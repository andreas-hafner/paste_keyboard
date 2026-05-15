# End User Guide

This guide is for the delivered `PasteKeyboard.exe`.

German guide: [enduser.md](enduser.md)

## Purpose

`Paste Keyboard` types clipboard text as simulated keystrokes. This is useful for:

- Proxmox or noVNC consoles
- browser-based remote sessions
- systems where normal paste does not work reliably

## Start

1. Start `PasteKeyboard.exe`.
2. The main window opens.
3. Set the options once.

For Windows startup shortcuts, the app can start minimized:

```text
PasteKeyboard.exe --minimized
```

With this parameter, `Paste Keyboard` starts directly in the Windows notification area. The main window is not shown as a normal taskbar button. If the main window is minimized or closed, the app keeps running there. Use the tray icon to show the window again or exit the app.

Only one instance can run at the same time. If `Paste Keyboard` is already active, a second start does not open another instance and only shows a short message.

## Language

The app supports German and English. Choose `Sprache` / `Language` in the main window and click `Einstellungen speichern` / `Save settings`. The selected app language is stored per user in the settings file.

The app language is separate from `Target layout`. Choose the target layout to match the keyboard layout inside the VM or remote system.

## Windows Startup

Startup is configured through a Windows shortcut. The EXE itself is not moved or changed.

1. Press `Win+R`.
2. Enter `shell:startup` and confirm.
3. Put a shortcut to `PasteKeyboard.exe` into the opened folder.
4. Right-click the shortcut and open `Properties`.
5. In `Target`, add `--minimized` after the EXE path.

Example:

```text
"C:\Tools\PasteKeyboard\PasteKeyboard.exe" --minimized
```

The parameter must be outside the quotes. Only the path to the EXE is quoted.

## Main Window

![Main window](screenshots/01-main-window.png)

Important fields:

- `Language`
  Selects the UI language: German or English.
- `Global hotkey`
  Triggers typing globally. The field is read-only. Use `Record` to press and capture a key combination, then click `Save settings`.
- `Target layout`
  Selects the keyboard layout used for simulated input.
- `Start delay (ms)`
  Wait time between trigger and typing start.
- `Key delay (ms)`
  Short delay between individual keys.
- `Clipboard typing limit`
  Maximum number of characters sent directly by `Type clipboard` or the hotkey. Default: `1000`.
- `Notify after typing`
  Shows a small local popup after typing and also tries a tray or Windows notification.
- `Skip unsupported characters`
  Skips characters that cannot be represented by the selected layout.

## Typical Workflow

1. Select the matching `Target layout`.
2. Choose a hotkey or use `Record`.
3. Click `Save settings`.
4. Copy the text to the clipboard.
5. Focus the target window or VM console.
6. Press the hotkey.

## Clipboard

- Only text is processed.
- Images, files, and other clipboard formats are not supported.
- `Type clipboard` and the hotkey are limited to `1000` characters by default.
- For longer text, use `Load clipboard`, check or edit the preview, then use `Type text field`.

## Character Support

- Only characters available in the selected target layout, directly or through supported dead keys, can be typed.
- `Enter` and `Tab` are supported.
- `en-US` is good for ASCII and simple English text, but not for many umlauts.
- `en-US-intl` is often better when umlauts or accent characters are required.
- Emoji, CJK characters, and many other Unicode symbols are not guaranteed.

## Skip Unsupported Characters

When this option is off, typing stops at the first unsupported character. This is usually safer for exact input.

When this option is on, unsupported characters are omitted and the rest is typed. Use this only when missing characters are acceptable.

## Preview Text

![Text in preview field](screenshots/02-text-loaded.png)

The preview field is useful for tests or prepared text:

1. `Load clipboard` loads the current text into the field.
2. Review or edit the text.
3. `Type text field` types exactly this text.

## Recommended Settings

For German target systems:

- `Target layout`: `de-DE`
- suitable for umlauts and German special characters

For simple English target systems:

- `Target layout`: `en-US`
- suitable for ASCII and common shell commands

For English target systems with umlauts:

- `Target layout`: `en-US-intl`
- useful when umlauts or accent characters are needed

## Proxmox and noVNC Tips

- Always make sure the VM console has focus before triggering.
- For browser consoles, the global hotkey is usually more reliable than the button.
- If nothing arrives, increase `Start delay`.
- If special characters are wrong, the selected layout usually does not match the target system.

## Troubleshooting

### Nothing is typed

Check:

1. Is the target window active?
2. Is the start delay high enough?
3. Was the hotkey saved?
4. Does `Type text field` work locally in Notepad?

### Clipboard is rejected

Check:

1. Does the clipboard contain text?
2. Is the content longer than the configured clipboard limit?
3. For long content, use `Load clipboard` and then `Type text field`.

### Special characters are wrong

Check:

1. Does `Target layout` match the target system?
2. Does the VM use the same keyboard layout?
3. For umlauts on English systems, try `en-US-intl`.
4. If characters are missing, check whether the selected layout supports them.

### The hotkey does not work

Check:

1. Is the key combination already used by another app?
2. Try `Ctrl+Shift+F8` or `Alt+F9`.
3. Always click `Save settings` after changes.

### Hotkey recording captures the wrong combination

Check:

1. Click `Record`.
2. Hold modifiers first, then press the main key.
3. Release only after the combination appears in the field.
4. If Windows or another tool intercepts the combination, choose another one.

### No Windows notification appears

When enabled, the app always shows a small local popup in the lower right. The additional Windows or tray notification can be suppressed by Focus Assist, notification settings, or tray behavior.

## Settings Location

The app stores settings per user:

```text
%APPDATA%\PasteKeyboard\settings.json
```
