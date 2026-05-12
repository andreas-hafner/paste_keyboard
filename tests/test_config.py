from __future__ import annotations

import ctypes
from contextlib import contextmanager
from dataclasses import fields
from pathlib import Path
import shutil
import sys
import unittest
from uuid import uuid4
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TEST_TEMP_ROOT = ROOT / "tests" / "_tmp"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paste_keyboard import win32
from paste_keyboard.config import AppSettings, load_settings, save_settings
from paste_keyboard.hotkeys import parse_hotkey


@contextmanager
def make_temp_dir():
    TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    temp_dir = TEST_TEMP_ROOT / f"tmp-{uuid4().hex}"
    temp_dir.mkdir(parents=True, exist_ok=False)
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


class HotkeyParserTests(unittest.TestCase):
    def test_parse_letter_hotkey(self) -> None:
        parsed = parse_hotkey("Ctrl+Alt+V")
        self.assertEqual(parsed.display, "Ctrl+Alt+V")
        self.assertEqual(parsed.vk, ord("V"))

    def test_parse_function_hotkey(self) -> None:
        parsed = parse_hotkey("Ctrl+Shift+F8")
        self.assertEqual(parsed.display, "Ctrl+Shift+F8")
        self.assertEqual(parsed.vk, 0x77)

    def test_parse_rejects_missing_modifier(self) -> None:
        with self.assertRaises(ValueError):
            parse_hotkey("F8")

    def test_parse_normalizes_special_key_display(self) -> None:
        self.assertEqual(parse_hotkey("control+alt+pageup").display, "Ctrl+Alt+PageUp")
        self.assertEqual(parse_hotkey("control+alt+escape").display, "Ctrl+Alt+Escape")


class SettingsTests(unittest.TestCase):
    def test_new_settings_fields_stay_after_skip_unsupported(self) -> None:
        field_names = [field.name for field in fields(AppSettings)]

        self.assertLess(field_names.index("skip_unsupported"), field_names.index("clipboard_typing_limit"))
        self.assertLess(field_names.index("skip_unsupported"), field_names.index("notify_on_finish"))

    def test_save_and_load_settings(self) -> None:
        with make_temp_dir() as temp_dir:
            path = temp_dir / "nested" / "test-settings-save.json"
            settings = AppSettings(
                hotkey="Ctrl+Shift+F8",
                layout_id="en-US-intl",
                start_delay_ms=500,
                key_delay_ms=15,
                skip_unsupported=True,
                clipboard_typing_limit=2500,
                notify_on_finish=True,
            )
            save_settings(settings, path)
            loaded = load_settings(path)
            parent_exists = path.parent.exists()
            file_exists = path.exists()

        self.assertEqual(loaded, settings)
        self.assertTrue(parent_exists)
        self.assertTrue(file_exists)

    def test_load_invalid_json_falls_back_to_defaults(self) -> None:
        with make_temp_dir() as temp_dir:
            path = temp_dir / "test-settings-invalid.json"
            path.write_text("{broken", encoding="utf-8")
            loaded = load_settings(path)

        self.assertEqual(loaded, AppSettings())

    def test_load_settings_with_custom_path_does_not_create_global_dirs(self) -> None:
        with make_temp_dir() as temp_dir:
            custom_path = temp_dir / "custom" / "settings.json"
            global_state_dir = temp_dir / "global-state"

            with patch("paste_keyboard.config.STATE_DIR", global_state_dir), patch(
                "paste_keyboard.config.SETTINGS_PATH", global_state_dir / "settings.json"
            ):
                loaded = load_settings(custom_path)
                custom_parent_exists = custom_path.parent.exists()
                global_exists = global_state_dir.exists()

        self.assertEqual(loaded, AppSettings())
        self.assertFalse(custom_parent_exists)
        self.assertFalse(global_exists)

    def test_save_settings_with_custom_path_creates_only_target_parent(self) -> None:
        with make_temp_dir() as temp_dir:
            custom_path = temp_dir / "custom" / "settings.json"
            global_state_dir = temp_dir / "global-state"
            settings = AppSettings(hotkey="Ctrl+Alt+Escape")

            with patch("paste_keyboard.config.STATE_DIR", global_state_dir), patch(
                "paste_keyboard.config.SETTINGS_PATH", global_state_dir / "settings.json"
            ):
                save_settings(settings, custom_path)
                custom_exists = custom_path.exists()
                custom_parent_exists = custom_path.parent.exists()
                global_exists = global_state_dir.exists()

        self.assertTrue(custom_exists)
        self.assertTrue(custom_parent_exists)
        self.assertFalse(global_exists)


class Win32InputTests(unittest.TestCase):
    def test_input_size_matches_native_windows_layout(self) -> None:
        expected_size = 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28
        self.assertEqual(ctypes.sizeof(win32.INPUT), expected_size)
        self.assertEqual(win32.INPUT._fields_[1][0], "data")
        self.assertGreaterEqual(ctypes.sizeof(win32.INPUTUNION), ctypes.sizeof(win32.KEYBDINPUT))


class SingleInstanceLockTests(unittest.TestCase):
    def test_acquire_returns_true_for_new_mutex(self) -> None:
        lock = win32.SingleInstanceLock("test-lock")

        with patch("paste_keyboard.win32.kernel32.CreateMutexW", return_value=123), patch(
            "paste_keyboard.win32.kernel32.GetLastError", return_value=0
        ):
            acquired = lock.acquire()

        self.assertTrue(acquired)
        self.assertEqual(lock.handle, 123)
        self.assertTrue(lock.acquired)

    def test_acquire_returns_false_when_mutex_already_exists(self) -> None:
        lock = win32.SingleInstanceLock("test-lock")

        with patch("paste_keyboard.win32.kernel32.CreateMutexW", return_value=123), patch(
            "paste_keyboard.win32.kernel32.GetLastError", return_value=win32.ERROR_ALREADY_EXISTS
        ), patch("paste_keyboard.win32.kernel32.CloseHandle") as close_handle_mock:
            acquired = lock.acquire()

        self.assertFalse(acquired)
        self.assertIsNone(lock.handle)
        self.assertFalse(lock.acquired)
        close_handle_mock.assert_called_once_with(123)

    def test_close_releases_and_closes_acquired_mutex(self) -> None:
        lock = win32.SingleInstanceLock("test-lock")
        lock.handle = 123
        lock.acquired = True

        with patch("paste_keyboard.win32.kernel32.ReleaseMutex") as release_mutex_mock, patch(
            "paste_keyboard.win32.kernel32.CloseHandle"
        ) as close_handle_mock:
            lock.close()

        release_mutex_mock.assert_called_once_with(123)
        close_handle_mock.assert_called_once_with(123)
        self.assertIsNone(lock.handle)
        self.assertFalse(lock.acquired)


if __name__ == "__main__":
    unittest.main()
