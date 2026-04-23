from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paste_keyboard.layouts import LayoutResolver, get_layout
from paste_keyboard import win32


@unittest.skipUnless(sys.platform == "win32", "Windows-only tests")
class LayoutResolverTests(unittest.TestCase):
    def test_de_layout_resolves_at(self) -> None:
        resolver = LayoutResolver(get_layout("de-DE"))
        result = resolver.compile_text("@")
        self.assertFalse(result.errors)
        self.assertEqual(len(result.key_presses), 1)
        self.assertEqual(result.key_presses[0].vk, ord("Q"))
        self.assertEqual(result.key_presses[0].modifiers, ("ctrl", "alt"))

    def test_us_layout_rejects_umlaut(self) -> None:
        resolver = LayoutResolver(get_layout("en-US"))
        result = resolver.compile_text("ä")
        self.assertTrue(result.errors)

    def test_us_intl_supports_umlaut(self) -> None:
        resolver = LayoutResolver(get_layout("en-US-intl"))
        result = resolver.compile_text("ä")
        self.assertFalse(result.errors)

    def test_newline_becomes_enter(self) -> None:
        resolver = LayoutResolver(get_layout("de-DE"))
        result = resolver.compile_text("a\nb")
        self.assertFalse(result.errors)
        self.assertEqual(result.key_presses[1].vk, win32.VK_RETURN)
