from pathlib import Path
import sys
import argparse


try:
    from paste_keyboard.gui import run_app
except ModuleNotFoundError:
    ROOT = Path(__file__).resolve().parent
    SRC = ROOT / "src"
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from paste_keyboard.gui import run_app


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
    run_app(start_minimized=args.minimized)


if __name__ == "__main__":
    main()
