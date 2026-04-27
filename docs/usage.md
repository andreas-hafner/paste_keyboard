# Bedienungsanleitung

## Zweck

`Paste Keyboard` tippt Text aus der Zwischenablage per simulierten Tastendruecken ein. Das ist fuer Remote-Konsolen und Browser-VMs gedacht, in denen normales Einfuegen nicht oder nur unzuverlaessig funktioniert.

## Hauptfenster

![Hauptfenster](screenshots/01-main-window.png)

Das Hauptfenster enthaelt die wichtigsten Einstellungen:

- `Globaler Hotkey`: loest das Eintippen global aus.
- `Ziel-Layout`: bestimmt, wie Zeichen in Tastendruecke uebersetzt werden.
- `Startverzoegerung (ms)`: Wartezeit zwischen Ausloesen und Beginn der Eingabe.
- `Tastendelay (ms)`: kleine Pause zwischen einzelnen Tastendruecken.
- `Nicht unterstuetzte Zeichen ueberspringen`: ignoriert Zeichen, die im gewaehlten Layout nicht abbildbar sind.
- `Zwischenablage tippen`: tippt den aktuellen Clipboard-Text, aber nur wenn die Zwischenablage Text enthaelt und der Inhalt nicht groesser als `1000` Zeichen ist.
- `Zwischenablage laden`: laedt den Clipboard-Text in das Textfeld, auch wenn er laenger als `1000` Zeichen ist.

## Beispiel mit geladenem Text

![Text im Vorschaufeld](screenshots/02-text-loaded.png)

Das Vorschaufeld ist nuetzlich zum Testen:

- Text aus der Zwischenablage laden
- Text pruefen oder anpassen
- direkt mit `Textfeld tippen` ausloesen

## Speicherort der Einstellungen

Die App speichert ihre Einstellungen pro Benutzer unter:

```text
%APPDATA%\PasteKeyboard\settings.json
```

## Minimierter Start

Fuer Windows-Autostart kann die App minimiert gestartet werden:

```powershell
python main.py --minimized
```

Dabei startet die App direkt im Windows-Infobereich. Das normale Schliessen oder Minimieren blendet nur das Hauptfenster aus; die App laeuft fuer den globalen Hotkey weiter. Ueber das Tray-Symbol kann das Fenster wieder geoeffnet oder die App beendet werden.

Bei der gebauten EXE wird derselbe Parameter an die Verknuepfung angehaengt:

```text
PasteKeyboard.exe --minimized
```

## Windows-Autostart

Autostart fuer die gebaute EXE einrichten:

1. `Win+R` druecken.
2. `shell:startup` eingeben und bestaetigen.
3. Eine Verknuepfung zu `PasteKeyboard.exe` in den geoeffneten Autostart-Ordner legen.
4. Die Eigenschaften der Verknuepfung oeffnen.
5. Im Feld `Ziel` den Parameter `--minimized` hinter den EXE-Pfad setzen.

Beispiel:

```text
"C:\Tools\PasteKeyboard\PasteKeyboard.exe" --minimized
```

Wichtig: Der Parameter steht ausserhalb der Anfuehrungszeichen. Nur der Pfad zur EXE wird in Anfuehrungszeichen gesetzt.

## Typischer Ablauf

1. App mit `python main.py` starten.
2. Ziel-Layout passend zur VM auswaehlen.
3. Einen Hotkey festlegen, z. B. `Ctrl+Alt+V` oder `Ctrl+Shift+F8`.
4. Einen sinnvollen Wert fuer `Startverzoegerung` setzen.
Fuer manuelle Tests per Button sind `1000` bis `1500` ms oft praktisch.
5. Text in die Zwischenablage kopieren.
6. Zielkonsole fokussieren.
7. Hotkey druecken oder die Eingabe ueber die GUI starten.

## Zwischenablage

- Verarbeitet wird nur Text.
- Bilder, Dateien und andere Clipboard-Formate werden nicht unterstuetzt.
- Direktes Tippen aus der Zwischenablage ist auf `1000` Zeichen begrenzt.
- Fuer laengere Inhalte: erst `Zwischenablage laden`, dann den Text im Vorschaufeld mit `Textfeld tippen` senden.

## Zeichenunterstuetzung

- Unterstuetzt werden nur Zeichen, die im gewaehlten Ziel-Layout direkt oder ueber unterstuetzte Dead-Keys abbildbar sind.
- `Enter` und `Tab` werden explizit unterstuetzt.
- Beispiele:
  - `de-DE` eignet sich gut fuer deutsche Umlaute und typische deutsche Sonderzeichen.
  - `en-US` eignet sich gut fuer ASCII und typische englische Shell-Kommandos, aber nicht fuer viele Umlaute.
  - `en-US-intl` ist fuer Umlaute und Akzentzeichen oft besser geeignet als `en-US`.
- Nicht garantiert sind z. B. Emoji, CJK-Zeichen und viele Unicode-Sonderzeichen.

## Nicht unterstuetzte Zeichen ueberspringen

- Standardmaessig ist diese Option deaktiviert.
- Deaktiviert:
  - Die Eingabe bricht am ersten Zeichen ab, das im gewaehlten Layout nicht abbildbar ist.
  - Das ist sicherer, weil kein Text stillschweigend verkuerzt oder veraendert wird.
- Aktiviert:
  - Nicht abbildbare Zeichen werden ausgelassen, der Rest wird weiter getippt.
  - Das ist praktisch fuer unkritische Texte, kann aber Inhalte stillschweigend veraendern.

## Layout-Empfehlungen

### `de-DE`

Empfohlen, wenn die Ziel-VM ein deutsches Tastaturlayout verwendet.

Geeignet fuer:

- deutsche Umlaute
- `@`
- `EUR`
- viele typische deutsche Sonderzeichen

### `en-US`

Empfohlen fuer einfache englische Layouts ohne internationale Dead Keys.

Geeignet fuer:

- ASCII
- typische englische Shell-Kommandos

Eingeschraenkt bei:

- `aeoeuess`
- einigen Sonderzeichen, die im US-Layout nicht direkt existieren

### `en-US-intl`

Sinnvoll, wenn die Ziel-VM ein US-International-Layout verwendet und Umlaute oder Akzentzeichen benoetigt werden.

## Tipps fuer Proxmox und noVNC

- Vor dem Ausloesen immer sicherstellen, dass die VM-Konsole wirklich den Fokus hat.
- Fuer Browser-VM-Konsolen ist der globale Hotkey meist zuverlaessiger als der Button in der App.
- Wenn nichts im Ziel landet, zuerst die `Startverzoegerung` erhoehen.
- Wenn Sonderzeichen falsch erscheinen, stimmt meist das Ziel-Layout nicht.

## Fehlersuche

### Es wird nichts geschrieben

Pruefen:

1. Ist das richtige Fenster fokussiert?
2. Ist die Startverzoegerung hoch genug?
3. Ist der globale Hotkey wirklich gespeichert worden?
4. Funktioniert `Textfeld tippen` im lokalen Notepad?

### Zwischenablage wird abgewiesen

Pruefen:

1. Enthaelt die Zwischenablage wirklich Text?
2. Ist der Inhalt groesser als `1000` Zeichen?
3. Wenn der Text laenger ist: `Zwischenablage laden` und danach `Textfeld tippen` verwenden.

### Sonderzeichen sind falsch

Pruefen:

1. Stimmt das Ziel-Layout in der App?
2. Stimmt das tatsaechliche Tastaturlayout in der VM?
3. Falls Umlaute auf englischer VM gebraucht werden: `en-US-intl` testen.
4. Falls einzelne Zeichen komplett fehlen: pruefen, ob sie im gewaehlten Layout ueberhaupt unterstuetzt werden.

### Hotkey funktioniert nicht

Pruefen:

1. Ist die gewaehlte Tastenkombination schon von Windows oder einer anderen App belegt?
2. Testweise `Ctrl+Shift+F8` oder `Alt+F9` verwenden.
3. Nach Aenderungen immer `Einstellungen speichern` druecken.

## Manuelle Pruefung

Sinnvolle Testziele:

1. Notepad
2. Browser-`textarea`
3. Proxmox/noVNC-Konsole

Empfohlene Testtexte:

- `Hello World`
- `aeoeueAeOeUeSs`
- `@ EUR { } [ ] \ | ~ ^`
- mehrzeiliger Text
- Tabs
- ein sehr langer Text mit mehr als `1000` Zeichen fuer den Clipboard-Guard
