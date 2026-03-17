"""Player inventory system."""


class Inventory:
    def __init__(self):
        self.items: dict[str, str] = {}  # name -> description

    def add(self, name: str, description: str) -> str:
        if name in self.items:
            return f"你已经有 {name} 了。"
        self.items[name] = description
        return f"拾取了 [bold cyan]{name}[/bold cyan]。"

    def remove(self, name: str) -> bool:
        if name in self.items:
            del self.items[name]
            return True
        return False

    def has(self, name: str) -> bool:
        return name in self.items

    def list_items(self) -> str:
        if not self.items:
            return "[dim]背包是空的。[/dim]"
        lines = ["[bold]背包物品：[/bold]"]
        for name, desc in self.items.items():
            lines.append(f"  [cyan]{name}[/cyan] - {desc}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return dict(self.items)

    def from_dict(self, data: dict):
        self.items = dict(data)
