from __future__ import annotations

import queue
from pathlib import Path
import sys
import tkinter as tk
from types import SimpleNamespace
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

    def test_type_clipboard_uses_configured_limit(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.clipboard_get.return_value = "x" * 1500
        app.clipboard_typing_limit_var = DummyVar(2000)

        self.assertEqual(app._load_clipboard_text_for_typing(), "x" * 1500)

    def test_english_language_translates_clipboard_limit_error(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.clipboard_get.return_value = "x" * 3
        app.clipboard_typing_limit_var = DummyVar(2)
        app.language_var = DummyVar("English")

        with self.assertRaisesRegex(RuntimeError, "Clipboard is too large to type"):
            app._load_clipboard_text_for_typing()

    def test_collect_settings_stores_language_code(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.language_var = DummyVar("English")
        app.hotkey_var = DummyVar("Ctrl+Alt+V")
        app.layout_var = DummyVar("en-US")
        app.start_delay_var = DummyVar(250)
        app.key_delay_var = DummyVar(25)
        app.skip_unsupported_var = DummyVar(False)
        app.clipboard_typing_limit_var = DummyVar(1000)
        app.notify_on_finish_var = DummyVar(True)

        settings = app._collect_settings()

        self.assertEqual(settings.language, "en")
        self.assertEqual(settings.layout_id, "en-US")

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

    def test_schedule_minimized_start_registers_retry_delays(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()

        app._schedule_minimized_start()

        self.assertEqual(app.root.after.call_count, len(gui.MINIMIZE_RETRY_DELAYS_MS))
        self.assertEqual(
            [call.args for call in app.root.after.call_args_list],
            [(delay_ms, app._minimize_window) for delay_ms in gui.MINIMIZE_RETRY_DELAYS_MS],
        )

    def test_hide_window_from_taskbar_uses_toolwindow_style(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()

        app._hide_window_from_taskbar()

        app.root.attributes.assert_called_once_with("-toolwindow", True)

    def test_close_hides_window_to_tray_instead_of_destroying(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.exiting = False

        app._on_close()

        app.root.withdraw.assert_called_once()
        app.root.destroy.assert_not_called()

    def test_exit_app_closes_tray_icon_and_closes_hotkey_listener(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        tray_icon = Mock()
        app.tray_icon = tray_icon
        app.hotkey_listener = Mock()
        app.exiting = False

        app._exit_app()

        self.assertTrue(app.exiting)
        tray_icon.close.assert_called_once()
        app.hotkey_listener.close.assert_called_once()
        app.root.destroy.assert_called_once()

    def test_poll_tray_events_handles_show_and_exit(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.tray_queue = queue.SimpleQueue()
        app._show_from_tray = Mock()
        app.exiting = False

        def exit_app() -> None:
            app.exiting = True

        app._exit_app = Mock(side_effect=exit_app)

        app.tray_queue.put("show")
        app.tray_queue.put("exit")
        app._poll_tray_events()

        app._show_from_tray.assert_called_once()
        app._exit_app.assert_called_once()
        app.root.after.assert_not_called()

    def test_save_settings_keeps_active_hotkey_when_registration_fails(self) -> None:
        current_hotkey = parse_hotkey("Ctrl+Alt+V")
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.hotkey_var = DummyVar("Ctrl+Alt+Escape")
        app.layout_var = DummyVar("de-DE")
        app.start_delay_var = DummyVar(250)
        app.key_delay_var = DummyVar(25)
        app.clipboard_typing_limit_var = DummyVar(1000)
        app.notify_on_finish_var = DummyVar(False)
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
        self.assertEqual(showerror_mock.call_args.args[0], "Hotkey nicht gespeichert")
        self.assertIn("Hotkey konnte nicht aktiviert werden: belegt", showerror_mock.call_args.args[1])
        self.assertEqual(app.hotkey_var.get(), "Ctrl+Alt+Escape")
        self.assertIn("Einstellungen nicht gespeichert", app.status_var.get())
        self.assertIn("Hotkey konnte nicht aktiviert werden: belegt", app.status_var.get())
        self.assertIn(f"Hotkey weiter aktiv: {current_hotkey.display}", app.status_var.get())

    def test_hotkey_capture_builds_display_from_key_event(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        event = SimpleNamespace(keysym="v", char="v", state=999)

        with patch("paste_keyboard.gui.win32.is_key_down") as is_key_down_mock:
            is_key_down_mock.side_effect = lambda vk: vk in {gui.win32.VK_CONTROL, gui.win32.VK_SHIFT}
            captured = app._hotkey_from_key_event(event)

        self.assertEqual(captured, "Ctrl+Shift+V")

    def test_hotkey_capture_waits_for_main_key(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        event = SimpleNamespace(keysym="Control_L", char="", state=0)

        self.assertIsNone(app._hotkey_from_key_event(event))

    def test_hotkey_capture_requires_modifier(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        event = SimpleNamespace(keysym="v", char="v", state=0)

        with patch("paste_keyboard.gui.win32.is_key_down", return_value=False):
            self.assertIsNone(app._hotkey_from_key_event(event))

    def test_hotkey_capture_accepts_supported_special_key(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        event = SimpleNamespace(keysym="Prior", char="", state=0)

        with patch("paste_keyboard.gui.win32.is_key_down") as is_key_down_mock:
            is_key_down_mock.side_effect = lambda vk: vk in {gui.win32.VK_CONTROL, gui.win32.VK_MENU}
            captured = app._hotkey_from_key_event(event)

        self.assertEqual(captured, "Ctrl+Alt+PageUp")

    def test_hotkey_capture_ignores_false_alt_event_state(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        event = SimpleNamespace(keysym="v", char="v", state=0x0008)

        with patch("paste_keyboard.gui.win32.is_key_down") as is_key_down_mock:
            is_key_down_mock.side_effect = lambda vk: vk in {gui.win32.VK_CONTROL, gui.win32.VK_SHIFT}
            captured = app._hotkey_from_key_event(event)

        self.assertEqual(captured, "Ctrl+Shift+V")

    def test_hotkey_capture_pauses_and_restores_active_listener(self) -> None:
        current_hotkey = parse_hotkey("Ctrl+Alt+V")
        old_listener = Mock()
        restored_listener = Mock()
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.hotkey_var = DummyVar("Ctrl+Alt+V")
        app.status_var = DummyVar("Bereit.")
        app.current_hotkey = current_hotkey
        app.hotkey_listener = old_listener
        app.hotkey_capture_active = False
        app.hotkey_capture_bind_id = None
        app.hotkey_capture_paused_hotkey = None
        app.hotkey_entry = Mock()
        app.hotkey_entry.bind.return_value = "bind-id"
        app.hotkey_capture_button = Mock()
        app._start_hotkey_listener = Mock(return_value=restored_listener)

        app._start_hotkey_capture()
        with patch("paste_keyboard.gui.win32.is_key_down") as is_key_down_mock:
            is_key_down_mock.side_effect = lambda vk: vk in {gui.win32.VK_CONTROL, gui.win32.VK_SHIFT}
            result = app._on_hotkey_capture_key(SimpleNamespace(keysym="F8", char="", state=0))

        self.assertEqual(result, "break")
        old_listener.close.assert_called_once()
        app.hotkey_entry.configure.assert_any_call(state="normal")
        app.hotkey_entry.configure.assert_any_call(state="readonly")
        app.hotkey_entry.bind.assert_called_once()
        app.hotkey_entry.unbind.assert_called_once_with("<KeyPress>", "bind-id")
        app._start_hotkey_listener.assert_called_once_with(current_hotkey)
        self.assertIs(app.hotkey_listener, restored_listener)
        self.assertEqual(app.hotkey_var.get(), "Ctrl+Shift+F8")
        self.assertIn("Einstellungen speichern", app.status_var.get())

    def test_hotkey_capture_escape_cancels_and_restores_listener(self) -> None:
        current_hotkey = parse_hotkey("Ctrl+Alt+V")
        restored_listener = Mock()
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.hotkey_var = DummyVar("Ctrl+Alt+V")
        app.status_var = DummyVar("Bereit.")
        app.current_hotkey = current_hotkey
        app.hotkey_listener = None
        app.hotkey_capture_active = True
        app.hotkey_capture_bind_id = "bind-id"
        app.hotkey_capture_paused_hotkey = current_hotkey
        app.hotkey_entry = Mock()
        app.hotkey_capture_button = Mock()
        app._start_hotkey_listener = Mock(return_value=restored_listener)

        result = app._on_hotkey_capture_key(SimpleNamespace(keysym="Escape", char="", state=0))

        self.assertEqual(result, "break")
        app.hotkey_entry.unbind.assert_called_once_with("<KeyPress>", "bind-id")
        self.assertIs(app.hotkey_listener, restored_listener)
        self.assertFalse(app.hotkey_capture_active)
        self.assertEqual(app.hotkey_var.get(), "Ctrl+Alt+V")
        self.assertEqual(app.status_var.get(), "Hotkey-Aufzeichnung abgebrochen.")

    def test_finish_typing_sends_tray_notification_when_enabled(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.status_var = DummyVar("Bereit.")
        app.notify_on_finish_var = DummyVar(True)
        app.tray_icon = Mock()
        app._show_finish_popup = Mock()
        app.typing_in_progress = True

        app._finish_typing(success="Textfeld: 3 Tastendruecke gesendet.")

        self.assertFalse(app.typing_in_progress)
        app.tray_icon.notify.assert_called_once_with("Paste Keyboard", "Textfeld: 3 Tastendruecke gesendet.")
        app._show_finish_popup.assert_called_once_with("Textfeld: 3 Tastendruecke gesendet.")

    def test_finish_typing_shows_popup_without_tray_icon(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.status_var = DummyVar("Bereit.")
        app.notify_on_finish_var = DummyVar(True)
        app.tray_icon = None
        app._show_finish_popup = Mock()
        app.typing_in_progress = True

        app._finish_typing(success="fertig")

        self.assertEqual(app.status_var.get(), "fertig")
        app._show_finish_popup.assert_called_once_with("fertig")

    def test_finish_typing_does_not_notify_when_disabled(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.status_var = DummyVar("Bereit.")
        app.notify_on_finish_var = DummyVar(False)
        app.tray_icon = Mock()
        app._show_finish_popup = Mock()
        app.typing_in_progress = True

        app._finish_typing(success="fertig")

        app.tray_icon.notify.assert_not_called()
        app._show_finish_popup.assert_not_called()

    def test_typing_worker_success_uses_short_finish_message(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.after.side_effect = lambda _delay, callback: callback()
        app.status_var = DummyVar("Bereit.")
        app.notify_on_finish_var = DummyVar(False)
        app.tray_icon = None
        app.typing_in_progress = True
        settings = gui.AppSettings()

        with patch("paste_keyboard.gui.type_text", return_value=(1234, [])):
            app._typing_worker("abc", settings, "Zwischenablage via Hotkey")

        self.assertFalse(app.typing_in_progress)
        self.assertEqual(app.status_var.get(), "Einfuegen beendet.")

    def test_finish_popup_geometry_positions_bottom_right(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        app.root = Mock()
        app.root.winfo_screenwidth.return_value = 1920
        app.root.winfo_screenheight.return_value = 1080

        geometry = app._finish_popup_geometry(width=360, height=90)

        self.assertEqual(geometry, "360x90+1536+926")

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

    def test_apply_language_updates_registered_widgets(self) -> None:
        app = gui.PasteKeyboardApp.__new__(gui.PasteKeyboardApp)
        label = Mock()
        app.language_var = DummyVar("English")
        app._localized_widgets = [(label, "save_settings")]
        app.hotkey_capture_active = False

        app._apply_language()

        label.configure.assert_called_once_with(text="Save settings")


if __name__ == "__main__":
    unittest.main()
