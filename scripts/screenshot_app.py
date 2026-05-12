from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from paste_keyboard.gui import PasteKeyboardApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-text", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = PasteKeyboardApp()
    if args.with_text:
        app.editor.insert("1.0", "Beispieltext aus der Anleitung")
        app._set_status("Zwischenablage in das Textfeld geladen.")
    app.root.update()
    app.run()


if __name__ == "__main__":
    main()
