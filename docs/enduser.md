# Endanwender-Anleitung

Diese Anleitung ist fuer die ausgelieferte `PasteKeyboard.exe` gedacht.

## Zweck

`Paste Keyboard` tippt Text aus der Zwischenablage per simulierten Tastendruecken ein. Das ist besonders nuetzlich fuer:

- Proxmox- oder noVNC-Konsolen
- Browser-basierte Remote-Sitzungen
- Systeme, in denen normales Einfuegen nicht funktioniert

## Starten

1. `PasteKeyboard.exe` starten.
2. Das Hauptfenster oeffnet sich.
3. Die gewuenschten Einstellungen einmalig setzen.

Fuer eine Windows-Autostart-Verknuepfung kann die App minimiert starten:

```text
PasteKeyboard.exe --minimized
```

Mit diesem Parameter startet `Paste Keyboard` direkt im Windows-Infobereich. Das Hauptfenster erscheint dann nicht als normaler Taskleisten-Button. Wenn das Hauptfenster minimiert oder geschlossen wird, bleibt die App dort weiter aktiv. Ueber das Tray-Symbol kann das Fenster wieder geoeffnet oder die App beendet werden.

## Windows-Autostart einrichten

Der Autostart wird ueber eine Windows-Verknuepfung eingerichtet. Die EXE selbst wird nicht verschoben oder veraendert.

1. `Win+R` druecken.
2. `shell:startup` eingeben und bestaetigen.
3. Eine Verknuepfung zu `PasteKeyboard.exe` in den geoeffneten Ordner legen.
4. Rechtsklick auf die Verknuepfung, dann `Eigenschaften` oeffnen.
5. Im Feld `Ziel` den Parameter `--minimized` hinter den EXE-Pfad setzen.

Beispiel:

```text
"C:\Tools\PasteKeyboard\PasteKeyboard.exe" --minimized
```

Wichtig: Der Parameter muss ausserhalb der Anfuehrungszeichen stehen. Nur der Pfad zur EXE wird in Anfuehrungszeichen gesetzt.

Beim naechsten Windows-Login startet `Paste Keyboard` dadurch minimiert im Infobereich und ist fuer den globalen Hotkey bereit. Soll die App sichtbar starten, den Parameter `--minimized` aus dem Feld `Ziel` wieder entfernen.

## Hauptfenster

![Hauptfenster](screenshots/01-main-window.png)

Wichtige Felder:

- `Globaler Hotkey`
  Damit wird das Eintippen global ausgeloest.
- `Ziel-Layout`
  Legt fest, welches Tastaturlayout fuer die Eingabe simuliert wird.
- `Startverzoegerung (ms)`
  Wartezeit zwischen Ausloesen und Start der Eingabe.
- `Tastendelay (ms)`
  Kleine Pause zwischen einzelnen Tasten.
- `Nicht unterstuetzte Zeichen ueberspringen`
  Ueberspringt Zeichen, die im gewaehlten Layout nicht abbildbar sind.

## Typischer Ablauf

1. Passendes `Ziel-Layout` auswaehlen.
2. Einen Hotkey festlegen.
3. Auf `Einstellungen speichern` klicken.
4. Den gewuenschten Text in die Zwischenablage kopieren.
5. Das Zielfenster oder die VM-Konsole fokussieren.
6. Den Hotkey druecken.

## Zwischenablage

- Verarbeitet wird nur Text.
- Bilder, Dateien und andere Clipboard-Formate werden nicht unterstuetzt.
- `Zwischenablage tippen` und der Hotkey sind auf `1000` Zeichen pro Ausloesung begrenzt.
- Wenn der Text laenger ist: zuerst `Zwischenablage laden`, dann im Vorschaufeld pruefen und mit `Textfeld tippen` senden.

## Zeichenunterstuetzung

- Es funktionieren nur Zeichen, die im gewaehlten Ziel-Layout direkt oder ueber unterstuetzte Dead-Keys erzeugt werden koennen.
- `Enter` und `Tab` werden unterstuetzt.
- `en-US` ist gut fuer ASCII und einfache englische Texte, aber nicht fuer viele Umlaute.
- `en-US-intl` ist oft besser, wenn Umlaute oder Akzentzeichen gebraucht werden.
- Nicht garantiert sind z. B. Emoji, CJK-Zeichen und viele Unicode-Sonderzeichen.

## Nicht unterstuetzte Zeichen ueberspringen

- Ist diese Option aus:
  - Die Eingabe stoppt am ersten nicht unterstuetzten Zeichen.
  - Das ist fuer genaue Eingaben meist die sicherere Einstellung.
- Ist diese Option an:
  - Nicht unterstuetzte Zeichen werden ausgelassen und der Rest wird weiter geschrieben.
  - Das ist nur sinnvoll, wenn fehlende Zeichen im Ergebnis akzeptabel sind.

## Arbeiten mit dem Vorschautext

![Text im Vorschaufeld](screenshots/02-text-loaded.png)

Das Vorschaufeld ist hilfreich fuer Tests oder vorbereitete Texte:

1. `Zwischenablage laden` laedt den aktuellen Text in das Feld.
2. Der Text kann dort geprueft oder angepasst werden.
3. Mit `Textfeld tippen` wird genau dieser Text eingegeben.

## Empfohlene Einstellungen

### Fuer deutsche Zielsysteme

- `Ziel-Layout`: `de-DE`
- gut geeignet fuer Umlaute und deutsche Sonderzeichen

### Fuer einfache englische Zielsysteme

- `Ziel-Layout`: `en-US`
- gut geeignet fuer ASCII und typische Shell-Kommandos

### Fuer englische Zielsysteme mit Umlauten

- `Ziel-Layout`: `en-US-intl`
- sinnvoll, wenn Umlaute oder Akzentzeichen benoetigt werden

## Tipps fuer Proxmox und noVNC

- Vor dem Ausloesen immer sicherstellen, dass die VM-Konsole den Fokus hat.
- Fuer Browser-Konsolen ist der globale Hotkey meist zuverlaessiger als der Button.
- Wenn nichts ankommt, `Startverzoegerung` erhoehen.
- Wenn Sonderzeichen falsch erscheinen, stimmt meist das gewaehlte Layout nicht.

## Fehlersuche

### Es wird nichts geschrieben

Pruefen:

1. Ist wirklich das Zielfenster aktiv?
2. Ist die Startverzoegerung hoch genug?
3. Wurde der Hotkey gespeichert?
4. Funktioniert `Textfeld tippen` lokal in Notepad?

### Zwischenablage wird abgewiesen

Pruefen:

1. Enthaelt die Zwischenablage Text?
2. Ist der Inhalt laenger als `1000` Zeichen?
3. Fuer lange Inhalte: `Zwischenablage laden` und danach `Textfeld tippen` verwenden.

### Sonderzeichen sind falsch

Pruefen:

1. Stimmt das `Ziel-Layout`?
2. Stimmt das Layout in der Ziel-VM?
3. Bei Umlauten auf englischen Systemen `en-US-intl` testen.
4. Falls einzelne Zeichen fehlen: pruefen, ob das Zeichen im gewaehlten Layout ueberhaupt unterstuetzt wird.

### Der Hotkey funktioniert nicht

Pruefen:

1. Wird die Tastenkombination bereits von einer anderen Anwendung benutzt?
2. Testweise `Ctrl+Shift+F8` oder `Alt+F9` verwenden.
3. Nach Aenderungen immer `Einstellungen speichern` klicken.

## Speicherort der Einstellungen

Die Anwendung speichert ihre Einstellungen pro Benutzer unter:

```text
%APPDATA%\PasteKeyboard\settings.json
```
