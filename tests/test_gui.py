from __future__ import annotations

import queue
from pathlib import Path
import sys
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paste_keyboard import gui
from paste_keyboard.hotkeys import parse_hotkey


class DummyVar:
    def __init__(self, value) -> None:
        self.value = value

    def get(self):
        return self.value

    def set(self, value) -> None:
        self.value = value


class GuiHotkeyTests(unittest.TestCase):
    def test_load_clipboard_text_rejects_non_text_content(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.clipboard_get.side_effect = tk.TclError("no text")

        with self.assertRaisesRegex(RuntimeError, "Zwischenablage enthaelt keinen Text"):
            app._load_clipboard_text()

    def test_type_clipboard_from_button_rejects_large_clipboard(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.clipboard_get.return_value = "x" * (gui.MAX_CLIPBOARD_TEXT_CHARS + 1)
        app._start_typing = Mock()

        with patch("paste_keyboard.gui.messagebox.showerror") as showerror_mock:
            app._type_clipboard_from_button()

        app._start_typing.assert_not_called()
        showerror_mock.assert_called_once()
        self.assertIn("zu gross zum Tippen", showerror_mock.call_args.args[1])

    def test_type_clipboard_from_hotkey_rejects_large_clipboard(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.clipboard_get.return_value = "x" * (gui.MAX_CLIPBOARD_TEXT_CHARS + 1)
        app.status_var = DummyVar("Bereit.")
        app._start_typing = Mock()

        app._type_clipboard_from_hotkey()

        app._start_typing.assert_not_called()
        self.assertIn("zu gross zum Tippen", app.status_var.get())

    def test_load_clipboard_into_editor_allows_large_text(self) -> None:
        large_text = "x" * (gui.MAX_CLIPBOARD_TEXT_CHARS + 1)
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.clipboard_get.return_value = large_text
        app.editor = Mock()
        app.status_var = DummyVar("Bereit.")

        app._load_clipboard_into_editor()

        app.editor.delete.assert_called_once_with("1.0", "end")
        app.editor.insert.assert_called_once_with("1.0", large_text)
        self.assertEqual(app.status_var.get(), "Zwischenablage in das Textfeld geladen.")

    def test_register_hotkey_from_form_handles_win32_error_on_startup(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.hotkey_var = DummyVar("Ctrl+Alt+V")
        app.status_var = DummyVar("Bereit.")
        app._register_hotkey = Mock(side_effect=gui.win32.Win32Error("belegt"))

        app._register_hotkey_from_form(initial=True)

        self.assertEqual(app.hotkey_var.get(), "Ctrl+Alt+V")
        self.assertEqual(app.status_var.get(), "Hotkey nicht aktiv: belegt")

    def test_save_settings_keeps_active_hotkey_when_registration_fails(self) -> None:
        current_hotkey = parse_hotkey("Ctrl+Alt+V")
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.hotkey_var = DummyVar("Ctrl+Alt+Escape")
        app.layout_var = DummyVar("de-DE")
        app.start_delay_var = DummyVar(250)
        app.key_delay_var = DummyVar(25)
        app.skip_unsupported_var = DummyVar(False)
        app.status_var = DummyVar("Bereit.")
        app.current_hotkey = current_hotkey
        app._register_hotkey = Mock(side_effect=gui.win32.Win32Error("belegt"))

        with patch("paste_keyboard.gui.save_settings") as save_settings_mock, patch(
            "paste_keyboard.gui.messagebox.showerror"
        ) as showerror_mock:
            app._save_settings()

        save_settings_mock.assert_not_called()
        showerror_mock.assert_called_once()
        self.assertEqual(app.hotkey_var.get(), current_hotkey.display)
        self.assertEqual(app.status_var.get(), f"Hotkey weiter aktiv: {current_hotkey.display}")

    def test_register_hotkey_restores_previous_listener_on_failure(self) -> None:
        old_hotkey = parse_hotkey("Ctrl+Alt+V")
        new_hotkey = parse_hotkey("Ctrl+Alt+Escape")
        old_listener = Mock()
        failed_listener = Mock()
        failed_listener.start.side_effect = gui.win32.Win32Error("belegt")
        restored_listener = Mock()

        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.hotkey_queue = queue.SimpleQueue()
        app.hotkey_listener = old_listener
        app.current_hotkey = old_hotkey

        with patch("paste_keyboard.gui.win32.HotkeyListener", side_effect=[failed_listener, restored_listener]):
            with self.assertRaises(gui.win32.Win32Error):
                app._register_hotkey(new_hotkey)

        old_listener.close.assert_called_once()
        failed_listener.start.assert_called_once()
        restored_listener.start.assert_called_once()
        self.assertIs(app.hotkey_listener, restored_listener)
        self.assertEqual(app.current_hotkey, old_hotkey)


if __name__ == "__main__":
    unittest.main()
