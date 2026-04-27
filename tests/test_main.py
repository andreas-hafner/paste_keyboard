from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main


class MainTests(unittest.TestCase):
    def test_main_starts_minimized_when_flag_is_set(self) -> None:
        with patch("main.run_app") as run_app_mock:
            main.main(["--minimized"])

        run_app_mock.assert_called_once_with(start_minimized=True)

    def test_main_starts_normal_without_flag(self) -> None:
        with patch("main.run_app") as run_app_mock:
            main.main([])

        run_app_mock.assert_called_once_with(start_minimized=False)


if __name__ == "__main__":
    unittest.main()
