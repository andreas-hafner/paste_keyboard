# Paste Keyboard

`Paste Keyboard` ist ein kleines Windows-Werkzeug, das Text aus der Zwischenablage als simulierte Tastendruecke eintippt. Das ist besonders nuetzlich fuer Browser-basierte VM-Konsolen wie Proxmox/noVNC, in denen normales Copy & Paste oft nicht zuverlaessig funktioniert.

## Kurzueberblick

- Windows-Desktop-App mit `tkinter`
- globaler Hotkey zum Ausloesen
- Ziel-Layout umschaltbar:
  - `de-DE`
  - `en-US`
  - `en-US-intl`
- einstellbare Startverzoegerung und Tippgeschwindigkeit
- Eingabe aus Zwischenablage oder aus dem Test-/Vorschautext
- `Zwischenablage tippen` akzeptiert nur Text und ist auf `1000` Zeichen pro Ausloesung begrenzt
- Einstellungen werden unter `%APPDATA%\\PasteKeyboard\\settings.json` gespeichert

## Schnellstart

```powershell
python main.py
```

Minimiert starten, z. B. fuer eine Windows-Autostart-Verknuepfung:

```powershell
python main.py --minimized
```

Bei der gebauten EXE:

```text
PasteKeyboard.exe --minimized
```

Autostart einrichten:

1. `Win+R` druecken.
2. `shell:startup` eingeben und bestaetigen.
3. Eine Verknuepfung zu `PasteKeyboard.exe` in diesen Ordner legen.
4. In den Eigenschaften der Verknuepfung unter `Ziel` den Parameter `--minimized` anhaengen, z. B.:

```text
"C:\Tools\PasteKeyboard\PasteKeyboard.exe" --minimized
```

Danach:

1. Ziel-Layout waehlen.
2. Optional Hotkey, Startverzoegerung und Tastendelay anpassen.
3. Text in die Zwischenablage kopieren.
4. Ziel in der VM-Konsole fokussieren.
5. Hotkey druecken oder `Zwischenablage tippen` verwenden.

Hinweis:

- Es wird nur Text aus der Zwischenablage verarbeitet. Bilder, Dateien und andere Clipboard-Formate werden nicht unterstuetzt.
- Direktes Tippen aus der Zwischenablage ist auf `1000` Zeichen begrenzt.
- Fuer laengere Inhalte: zuerst `Zwischenablage laden`, dann im Vorschaufeld mit `Textfeld tippen` ausloesen.

## Dokumentation

- [Endanwender-Anleitung fuer die EXE](docs/enduser.md)
- [Bedienungsanleitung](docs/usage.md)
- [Windows-Build-Anleitung](docs/build.md)

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Build

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

Das erzeugt `dist\PasteKeyboard.exe`. Signiert wird nur, wenn ein Zertifikats-Thumbprint per `-Thumbprint` oder `CODESIGN_THUMBPRINT` bereitgestellt wird. Details stehen in [docs/build.md](docs/build.md).

## Hinweise

- Das ausgewaehlte Ziel-Layout muss zum tatsaechlichen Layout in der VM passen.
- `en-US` kann Umlaute und einige Sonderzeichen nicht nativ abbilden.
- Fuer englische VMs mit Umlauten ist `en-US-intl` oft die bessere Wahl.
- Die Zwischenablage wird nur als Text gelesen; nicht-textliche Inhalte werden abgewiesen.
- Unterstuetzt werden nur Zeichen, die im gewaehlten Layout direkt oder ueber unterstuetzte Dead-Keys abbildbar sind.
- `Enter` und `Tab` werden explizit unterstuetzt.
- Nicht garantiert sind z. B. Emoji, CJK-Zeichen und viele Unicode-Sonderzeichen.
- Wenn `Nicht unterstuetzte Zeichen ueberspringen` deaktiviert ist, bricht die Eingabe am ersten nicht abbildbaren Zeichen ab.
- Globaler Hotkey und simulierte Tasteneingabe sind Windows-spezifisch.
