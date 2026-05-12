from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def _default_state_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "PasteKeyboard"
    return ROOT_DIR / "state"


STATE_DIR = _default_state_dir()
SETTINGS_PATH = STATE_DIR / "settings.json"


@dataclass(slots=True)
class AppSettings:
    hotkey: str = "Ctrl+Alt+V"
    layout_id: str = "de-DE"
    start_delay_ms: int = 250
    key_delay_ms: int = 25
    skip_unsupported: bool = False
    clipboard_typing_limit: int = 1000
    notify_on_finish: bool = False


DEFAULT_SETTINGS = AppSettings()


def ensure_state_dir(path: Path = SETTINGS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _clamp_int(value: object, default: int, minimum: int, maximum: int) -> int:
    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, numeric))


def load_settings(path: Path = SETTINGS_PATH) -> AppSettings:
    if not path.exists():
        return AppSettings()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppSettings()

    return AppSettings(
        hotkey=str(data.get("hotkey", DEFAULT_SETTINGS.hotkey)),
        layout_id=str(data.get("layout_id", DEFAULT_SETTINGS.layout_id)),
        start_delay_ms=_clamp_int(data.get("start_delay_ms"), DEFAULT_SETTINGS.start_delay_ms, 0, 5000),
        key_delay_ms=_clamp_int(data.get("key_delay_ms"), DEFAULT_SETTINGS.key_delay_ms, 0, 1000),
        skip_unsupported=bool(data.get("skip_unsupported", DEFAULT_SETTINGS.skip_unsupported)),
        clipboard_typing_limit=_clamp_int(
            data.get("clipboard_typing_limit"),
            DEFAULT_SETTINGS.clipboard_typing_limit,
            1,
            1_000_000,
        ),
        notify_on_finish=bool(data.get("notify_on_finish", DEFAULT_SETTINGS.notify_on_finish)),
    )


def save_settings(settings: AppSettings, path: Path = SETTINGS_PATH) -> None:
    ensure_state_dir(path)
    payload = asdict(settings)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
