from __future__ import annotations


DEFAULT_LANGUAGE = "de"
SUPPORTED_LANGUAGES = {
    "de": "Deutsch",
    "en": "English",
}


TEXTS = {
    "de": {
        "settings": "Einstellungen",
        "language": "Sprache",
        "hotkey": "Globaler Hotkey",
        "record": "Aufzeichnen",
        "cancel": "Abbrechen",
        "layout": "Ziel-Layout",
        "start_delay": "Startverzoegerung (ms)",
        "key_delay": "Tastendelay (ms)",
        "clipboard_limit": "Zwischenablage-Limit beim Tippen",
        "skip_unsupported": "Nicht unterstuetzte Zeichen ueberspringen",
        "notify_on_finish": "Benachrichtigung nach Tippvorgang",
        "save_settings": "Einstellungen speichern",
        "type_clipboard": "Zwischenablage tippen",
        "load_clipboard": "Zwischenablage laden",
        "preview_text": "Test- / Vorschautext",
        "type_editor": "Textfeld tippen",
        "clear_editor": "Textfeld leeren",
        "ready": "Bereit.",
        "ready_hotkey": "Bereit. Hotkey aktiv: {hotkey}",
        "hotkey_not_active": "Hotkey nicht aktiv: {error}",
        "hotkey_invalid": "Hotkey ungueltig: {error}",
        "hotkey_capture_cancelled": "Hotkey-Aufzeichnung abgebrochen.",
        "hotkey_capture_active": "Hotkey-Aufzeichnung aktiv: Tastenkombination druecken. Escape bricht ab.",
        "hotkey_captured": "Hotkey uebernommen: {hotkey}. Einstellungen speichern, um ihn zu aktivieren.",
        "hotkey_restore_failed": "Hotkey konnte nach Aufzeichnung nicht wieder aktiviert werden: {error}",
        "invalid_settings": "Ungueltige Einstellungen",
        "valid_layout_required": "Bitte ein gueltiges Ziel-Layout waehlen.",
        "clipboard_limit_min": "Zwischenablage-Limit muss mindestens 1 sein.",
        "hotkey_not_saved": "Hotkey nicht gespeichert",
        "hotkey_enable_failed": "Hotkey konnte nicht aktiviert werden: {error} {active}",
        "settings_not_saved": "Einstellungen nicht gespeichert. {message}",
        "settings_saved": "Einstellungen gespeichert. Hotkey aktiv: {hotkey}",
        "no_active_hotkey": "Kein Hotkey aktiv.",
        "hotkey_still_active": "Hotkey weiter aktiv: {hotkey}",
        "clipboard": "Zwischenablage",
        "clipboard_no_text": "Zwischenablage enthaelt keinen Text. Bilder, Dateien und andere Formate werden nicht unterstuetzt.",
        "clipboard_empty": "Zwischenablage ist leer.",
        "clipboard_too_large": "Zwischenablage ist zu gross zum Tippen ({count} Zeichen, Limit {limit}).",
        "clipboard_loaded": "Zwischenablage in das Textfeld geladen.",
        "source_clipboard": "Zwischenablage",
        "source_clipboard_hotkey": "Zwischenablage via Hotkey",
        "source_editor": "Textfeld",
        "editor_empty": "Im Textfeld steht nichts.",
        "typing_in_progress": "Es laeuft bereits ein Tippvorgang.",
        "typing_sending": "{source}: sende Tastendruecke...",
        "unexpected_error": "Unerwarteter Fehler: {error}",
        "paste_finished": "Einfuegen beendet.",
        "skipped": "Uebersprungen: {chars}",
        "single_instance": "Paste Keyboard laeuft bereits.",
    },
    "en": {
        "settings": "Settings",
        "language": "Language",
        "hotkey": "Global hotkey",
        "record": "Record",
        "cancel": "Cancel",
        "layout": "Target layout",
        "start_delay": "Start delay (ms)",
        "key_delay": "Key delay (ms)",
        "clipboard_limit": "Clipboard typing limit",
        "skip_unsupported": "Skip unsupported characters",
        "notify_on_finish": "Notify after typing",
        "save_settings": "Save settings",
        "type_clipboard": "Type clipboard",
        "load_clipboard": "Load clipboard",
        "preview_text": "Test / preview text",
        "type_editor": "Type text field",
        "clear_editor": "Clear text field",
        "ready": "Ready.",
        "ready_hotkey": "Ready. Active hotkey: {hotkey}",
        "hotkey_not_active": "Hotkey not active: {error}",
        "hotkey_invalid": "Invalid hotkey: {error}",
        "hotkey_capture_cancelled": "Hotkey recording cancelled.",
        "hotkey_capture_active": "Hotkey recording active: press the key combination. Escape cancels.",
        "hotkey_captured": "Hotkey captured: {hotkey}. Save settings to activate it.",
        "hotkey_restore_failed": "Hotkey could not be reactivated after recording: {error}",
        "invalid_settings": "Invalid settings",
        "valid_layout_required": "Choose a valid target layout.",
        "clipboard_limit_min": "Clipboard limit must be at least 1.",
        "hotkey_not_saved": "Hotkey not saved",
        "hotkey_enable_failed": "Hotkey could not be activated: {error} {active}",
        "settings_not_saved": "Settings were not saved. {message}",
        "settings_saved": "Settings saved. Active hotkey: {hotkey}",
        "no_active_hotkey": "No hotkey active.",
        "hotkey_still_active": "Hotkey still active: {hotkey}",
        "clipboard": "Clipboard",
        "clipboard_no_text": "Clipboard does not contain text. Images, files, and other formats are not supported.",
        "clipboard_empty": "Clipboard is empty.",
        "clipboard_too_large": "Clipboard is too large to type ({count} characters, limit {limit}).",
        "clipboard_loaded": "Clipboard loaded into the text field.",
        "source_clipboard": "Clipboard",
        "source_clipboard_hotkey": "Clipboard via hotkey",
        "source_editor": "Text field",
        "editor_empty": "The text field is empty.",
        "typing_in_progress": "Typing is already in progress.",
        "typing_sending": "{source}: sending keystrokes...",
        "unexpected_error": "Unexpected error: {error}",
        "paste_finished": "Paste finished.",
        "skipped": "Skipped: {chars}",
        "single_instance": "Paste Keyboard is already running.",
    },
}


def normalize_language(value: object) -> str:
    language = str(value or "").strip().lower()
    if language in SUPPORTED_LANGUAGES:
        return language
    for code, label in SUPPORTED_LANGUAGES.items():
        if language == label.lower():
            return code
    return DEFAULT_LANGUAGE


def language_label(language: str) -> str:
    return SUPPORTED_LANGUAGES[normalize_language(language)]


def translate(language: str, key: str, **kwargs) -> str:
    texts = TEXTS.get(normalize_language(language), TEXTS[DEFAULT_LANGUAGE])
    template = texts.get(key, TEXTS[DEFAULT_LANGUAGE][key])
    return template.format(**kwargs)
