from __future__ import annotations

from dataclasses import dataclass

from . import win32


MODIFIER_TOKENS = {
    "CTRL": win32.MOD_CONTROL,
    "CONTROL": win32.MOD_CONTROL,
    "ALT": win32.MOD_ALT,
    "SHIFT": win32.MOD_SHIFT,
    "WIN": win32.MOD_WIN,
}

SPECIAL_KEYS = {
    "TAB": win32.VK_TAB,
    "SPACE": win32.VK_SPACE,
    "ENTER": win32.VK_RETURN,
    "ESC": win32.VK_ESCAPE,
    "ESCAPE": win32.VK_ESCAPE,
    "INSERT": win32.VK_INSERT,
    "DELETE": win32.VK_DELETE,
    "HOME": win32.VK_HOME,
    "END": win32.VK_END,
    "PAGEUP": win32.VK_PRIOR,
    "PAGEDOWN": win32.VK_NEXT,
}

DISPLAY_TOKENS = {
    "CTRL": "Ctrl",
    "CONTROL": "Ctrl",
    "ALT": "Alt",
    "SHIFT": "Shift",
    "WIN": "Win",
    "TAB": "Tab",
    "SPACE": "Space",
    "ENTER": "Enter",
    "ESC": "Escape",
    "ESCAPE": "Escape",
    "INSERT": "Insert",
    "DELETE": "Delete",
    "HOME": "Home",
    "END": "End",
    "PAGEUP": "PageUp",
    "PAGEDOWN": "PageDown",
}


@dataclass(frozen=True, slots=True)
class ParsedHotkey:
    display: str
    modifiers: int
    vk: int


def parse_hotkey(value: str) -> ParsedHotkey:
    tokens = [token.strip().upper() for token in value.split("+") if token.strip()]
    if len(tokens) < 2:
        raise ValueError("Hotkey braucht mindestens einen Modifier und eine Taste.")

    modifiers = 0
    main_tokens: list[str] = []

    for token in tokens:
        if token in MODIFIER_TOKENS:
            modifiers |= MODIFIER_TOKENS[token]
        else:
            main_tokens.append(token)

    if modifiers == 0 or len(main_tokens) != 1:
        raise ValueError("Hotkey muss genau eine Haupttaste und mindestens einen Modifier enthalten.")

    main = main_tokens[0]
    vk = _parse_main_key(main)
    normalized = _normalize_display(tokens)
    return ParsedHotkey(display=normalized, modifiers=modifiers, vk=vk)


def _parse_main_key(token: str) -> int:
    if token in SPECIAL_KEYS:
        return SPECIAL_KEYS[token]
    if len(token) == 1 and "A" <= token <= "Z":
        return ord(token)
    if len(token) == 1 and "0" <= token <= "9":
        return ord(token)
    if token.startswith("F") and token[1:].isdigit():
        index = int(token[1:])
        if 1 <= index <= 24:
            return 0x6F + index
    raise ValueError(f"Nicht unterstützte Haupttaste: {token}")


def _normalize_display(tokens: list[str]) -> str:
    display_tokens = []
    for token in tokens:
        if token in DISPLAY_TOKENS:
            display_tokens.append(DISPLAY_TOKENS[token])
        else:
            display_tokens.append(token if len(token) > 1 else token.upper())
    return "+".join(display_tokens)
