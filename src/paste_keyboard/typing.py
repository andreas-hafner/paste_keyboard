from __future__ import annotations

import time

from . import win32
from .layouts import LayoutResolver, get_layout


class TypingError(RuntimeError):
    pass


def type_text(text: str, layout_id: str, start_delay_ms: int, key_delay_ms: int, skip_unsupported: bool) -> tuple[int, list[str]]:
    resolver = LayoutResolver(get_layout(layout_id))
    result = resolver.compile_text(text, skip_unsupported=skip_unsupported)

    if result.errors and not skip_unsupported:
        first = result.errors[0]
        char_label = first.char.encode("unicode_escape").decode("ascii")
        raise TypingError(f"Zeichen {char_label} an Position {first.index + 1} ist im Layout {layout_id} nicht verfügbar.")

    win32.wait_for_modifiers_release()
    if start_delay_ms:
        time.sleep(start_delay_ms / 1000.0)

    for press in result.key_presses:
        win32.send_key_press(press)
        if key_delay_ms:
            time.sleep(key_delay_ms / 1000.0)

    skipped = [error.char for error in result.errors]
    return len(result.key_presses), skipped
