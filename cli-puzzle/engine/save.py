"""Auto-save system."""

import json
from pathlib import Path

SAVE_DIR = Path(__file__).parent.parent / "saves"
SAVE_FILE = SAVE_DIR / "save.json"


def save_game(scene_id: str, inventory: dict, flags: list[str]):
    SAVE_DIR.mkdir(exist_ok=True)
    data = {
        "scene_id": scene_id,
        "inventory": inventory,
        "flags": flags,
    }
    SAVE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_game() -> dict | None:
    if not SAVE_FILE.exists():
        return None
    try:
        return json.loads(SAVE_FILE.read_text())
    except (json.JSONDecodeError, KeyError):
        return None


def delete_save():
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()
