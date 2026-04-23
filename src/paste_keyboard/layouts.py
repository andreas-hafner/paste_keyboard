from __future__ import annotations

from dataclasses import dataclass
import unicodedata

from . import win32


COMBINING_TO_ACCENT = {
    "\u0300": "`",
    "\u0301": "'",
    "\u0302": "^",
    "\u0303": "~",
    "\u0308": '"',
}


@dataclass(frozen=True, slots=True)
class LayoutProfile:
    id: str
    name: str
    klid: str
    dead_key_literals: frozenset[str]
    compose_dead_keys: frozenset[str]


BUILTIN_LAYOUTS = {
    "de-DE": LayoutProfile(
        id="de-DE",
        name="Deutsch (Deutschland)",
        klid=win32.KLID_DE_DE,
        dead_key_literals=frozenset({"^", "`", "´"}),
        compose_dead_keys=frozenset({"^", "`"}),
    ),
    "en-US": LayoutProfile(
        id="en-US",
        name="English (US)",
        klid=win32.KLID_EN_US,
        dead_key_literals=frozenset(),
        compose_dead_keys=frozenset(),
    ),
    "en-US-intl": LayoutProfile(
        id="en-US-intl",
        name="English (US International)",
        klid=win32.KLID_EN_US_INTL,
        dead_key_literals=frozenset({"'", '"', "^", "`", "~"}),
        compose_dead_keys=frozenset(COMBINING_TO_ACCENT.values()),
    ),
}


@dataclass(frozen=True, slots=True)
class CompileError:
    char: str
    index: int
    reason: str


@dataclass(frozen=True, slots=True)
class CompileResult:
    key_presses: tuple[win32.KeyPress, ...]
    errors: tuple[CompileError, ...]


class LayoutResolver:
    def __init__(self, profile: LayoutProfile) -> None:
        self.profile = profile
        self.layout_handle = win32.load_keyboard_layout(profile.klid)

    def compile_text(self, text: str, skip_unsupported: bool = False) -> CompileResult:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        presses: list[win32.KeyPress] = []
        errors: list[CompileError] = []

        for index, char in enumerate(normalized):
            resolved = self._resolve_char(char)
            if resolved is None:
                errors.append(CompileError(char=char, index=index, reason=f"Nicht im Layout {self.profile.id} abbildbar"))
                if not skip_unsupported:
                    break
                continue
            presses.extend(resolved)

        return CompileResult(tuple(presses), tuple(errors))

    def _resolve_char(self, char: str) -> tuple[win32.KeyPress, ...] | None:
        if char == "\n":
            return (self._special_key(win32.VK_RETURN),)
        if char == "\t":
            return (self._special_key(win32.VK_TAB),)

        direct = self._direct_key_press(char)
        if direct is not None:
            return (direct,)

        decomposed = unicodedata.normalize("NFD", char)
        if len(decomposed) == 2 and decomposed[1] in COMBINING_TO_ACCENT:
            accent_char = COMBINING_TO_ACCENT[decomposed[1]]
            if accent_char in self.profile.compose_dead_keys:
                accent_press = self._direct_key_press(accent_char, literal_space_after=False)
                base_press = self._direct_key_press(decomposed[0], literal_space_after=False)
                if accent_press and base_press:
                    return (accent_press, base_press)
        return None

    def _direct_key_press(self, char: str, literal_space_after: bool | None = None) -> win32.KeyPress | None:
        encoded = win32.vk_key_scan_ex(char, self.layout_handle)
        if encoded == -1:
            return None

        vk = encoded & 0xFF
        modifier_bits = (encoded >> 8) & 0xFF
        scan_code = win32.map_virtual_key_ex(vk, self.layout_handle)
        if scan_code == 0:
            return None

        modifiers: list[str] = []
        if modifier_bits & 0x01:
            modifiers.append("shift")
        if modifier_bits & 0x02:
            modifiers.append("ctrl")
        if modifier_bits & 0x04:
            modifiers.append("alt")

        needs_space = char in self.profile.dead_key_literals if literal_space_after is None else literal_space_after
        return win32.KeyPress(vk=vk, scan_code=scan_code, modifiers=tuple(modifiers), literal_space_after=needs_space)

    @staticmethod
    def _special_key(vk: int) -> win32.KeyPress:
        scan_code = win32.map_virtual_key_ex(vk, 0)
        return win32.KeyPress(vk=vk, scan_code=scan_code)


def get_layout(layout_id: str) -> LayoutProfile:
    try:
        return BUILTIN_LAYOUTS[layout_id]
    except KeyError as exc:
        raise KeyError(f"Unbekanntes Layout: {layout_id}") from exc
