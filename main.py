from pathlib import Path
import sys
import argparse


try:
    from paste_keyboard import win32
    from paste_keyboard.config import load_settings
    from paste_keyboard.gui import run_app
    from paste_keyboard.i18n import translate
except ModuleNotFoundError:
    ROOT = Path(__file__).resolve().parent
    SRC = ROOT / "src"
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from paste_keyboard import win32
    from paste_keyboard.config import load_settings
    from paste_keyboard.gui import run_app
    from paste_keyboard.i18n import translate


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paste Keyboard starten.")
    parser.add_argument(
        "--minimized",
        action="store_true",
        help="Fenster minimiert starten, z. B. fuer Windows-Autostart.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    settings = load_settings()
    instance_lock = win32.SingleInstanceLock()
    if not instance_lock.acquire():
        win32.show_info_message("Paste Keyboard", translate(settings.language, "single_instance"))
        return
    try:
        run_app(start_minimized=args.minimized)
    finally:
        instance_lock.close()


if __name__ == "__main__":
    main()
