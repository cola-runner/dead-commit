"""Scene management engine."""

from __future__ import annotations

import json
import random
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content"


class Scene:
    def __init__(self, data: dict):
        self.id: str = data["id"]
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.ascii_art_file: str = data.get("ascii_art", "")
        self.items: dict[str, dict] = {
            item["name"]: item for item in data.get("items", [])
        }
        raw_cmds = data.get("commands", {})
        if isinstance(raw_cmds, list):
            self.commands: dict[str, dict] = {cmd["name"]: cmd for cmd in raw_cmds}
        elif isinstance(raw_cmds, dict) and "name" in raw_cmds:
            # Single command as dict
            self.commands = {raw_cmds["name"]: raw_cmds}
        else:
            self.commands = dict(raw_cmds)

        raw_trans = data.get("transitions", {})
        if isinstance(raw_trans, list):
            self.transitions: dict[str, dict] = {t["trigger"]: t for t in raw_trans}
        else:
            self.transitions = dict(raw_trans)
        self.on_enter: str = data.get("on_enter", "")
        self.picked_up: set[str] = set()

    def get_ascii_art(self) -> str:
        if not self.ascii_art_file:
            return ""
        art_path = CONTENT_DIR / "ascii_art" / self.ascii_art_file
        if art_path.exists():
            return art_path.read_text()
        return ""

    def list_visible_items(self) -> list[str]:
        return [name for name in self.items if name not in self.picked_up]

    def take_item(self, name: str) -> tuple[bool, str, str]:
        """Returns (success, message, item_description)."""
        if name not in self.items:
            return False, f"这里没有 [yellow]{name}[/yellow]。", ""
        if name in self.picked_up:
            return False, f"你已经拿过 [yellow]{name}[/yellow] 了。", ""
        item = self.items[name]
        if not item.get("takeable", True):
            return False, item.get("take_fail", f"[yellow]{name}[/yellow] 拿不动。"), ""
        self.picked_up.add(name)
        return True, "", item.get("description", "")

    def read_item(self, name: str) -> str:
        if name in self.items:
            return self.items[name].get("content", f"[yellow]{name}[/yellow] 没什么可看的。")
        return f"找不到 [yellow]{name}[/yellow]。"

    def check_transition(self, trigger: str, flags: list[str], inventory_names: list[str]) -> dict | None:
        if trigger not in self.transitions:
            return None
        t = self.transitions[trigger]
        required_flags = t.get("requires_flags", [])
        required_items = t.get("requires_items", [])
        if all(f in flags for f in required_flags) and all(i in inventory_names for i in required_items):
            return t
        return None


class SceneManager:
    def __init__(self):
        self.scenes: dict[str, Scene] = {}
        self.current: Scene | None = None
        self.flags: list[str] = []

    def load_chapter(self, chapter_file: str):
        path = CONTENT_DIR / chapter_file
        data = json.loads(path.read_text())
        for scene_data in data["scenes"]:
            scene = Scene(scene_data)
            self.scenes[scene.id] = scene

    def go_to(self, scene_id: str) -> tuple[Scene, str]:
        self.current = self.scenes[scene_id]
        return self.current, self.current.on_enter

    def add_flag(self, flag: str):
        if flag not in self.flags:
            self.flags.append(flag)

    def has_flag(self, flag: str) -> bool:
        return flag in self.flags

    def to_save_data(self) -> tuple[str, list[str]]:
        return self.current.id if self.current else "", list(self.flags)

    def restore(self, scene_id: str, flags: list[str]):
        self.flags = list(flags)
        if scene_id in self.scenes:
            self.current = self.scenes[scene_id]
