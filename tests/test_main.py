from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main
from paste_keyboard.config import AppSettings


class MainTests(unittest.TestCase):
    def test_main_starts_minimized_when_flag_is_set(self) -> None:
        with patch("main.win32.SingleInstanceLock") as lock_class_mock, patch("main.run_app") as run_app_mock:
            lock_mock = lock_class_mock.return_value
            lock_mock.acquire.return_value = True

            main.main(["--minimized"])

        run_app_mock.assert_called_once_with(start_minimized=True)
        lock_mock.acquire.assert_called_once()
        lock_mock.close.assert_called_once()

    def test_main_starts_normal_without_flag(self) -> None:
        with patch("main.win32.SingleInstanceLock") as lock_class_mock, patch("main.run_app") as run_app_mock:
            lock_mock = lock_class_mock.return_value
            lock_mock.acquire.return_value = True

            main.main([])

        run_app_mock.assert_called_once_with(start_minimized=False)
        lock_mock.acquire.assert_called_once()
        lock_mock.close.assert_called_once()

    def test_main_does_not_start_when_instance_is_already_running(self) -> None:
        with patch("main.win32.SingleInstanceLock") as lock_class_mock, patch(
            "main.win32.show_info_message"
        ) as show_info_message_mock, patch("main.run_app") as run_app_mock, patch(
            "main.load_settings", return_value=AppSettings(language="en")
        ):
            lock_mock = lock_class_mock.return_value
            lock_mock.acquire.return_value = False

            main.main([])

        run_app_mock.assert_not_called()
        show_info_message_mock.assert_called_once_with("Paste Keyboard", "Paste Keyboard is already running.")
        lock_mock.close.assert_not_called()

    def test_main_closes_instance_lock_when_app_exits_with_error(self) -> None:
        with patch("main.win32.SingleInstanceLock") as lock_class_mock, patch("main.run_app") as run_app_mock:
            lock_mock = lock_class_mock.return_value
            lock_mock.acquire.return_value = True
            run_app_mock.side_effect = RuntimeError("boom")

            with self.assertRaises(RuntimeError):
                main.main([])

        lock_mock.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
