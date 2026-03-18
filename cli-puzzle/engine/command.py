"""Command parser for the puzzle game."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.scene import SceneManager
    from engine.inventory import Inventory


class CommandResult:
    def __init__(
        self,
        message: str = "",
        scene_change: str = "",
        add_flag: str = "",
        update_art: bool = False,
        game_over: bool = False,
    ):
        self.message = message
        self.scene_change = scene_change
        self.add_flag = add_flag
        self.update_art = update_art
        self.game_over = game_over


def parse_command(
    raw: str,
    scene_mgr: SceneManager,
    inventory: Inventory,
) -> CommandResult:
    raw = raw.strip()
    if not raw:
        return CommandResult()

    parts = raw.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    scene = scene_mgr.current
    if scene is None:
        return CommandResult(message="[red]错误：没有当前场景。[/red]")

    # Built-in commands
    if cmd == "help":
        return _cmd_help(scene_mgr)
    if cmd == "ls":
        return _cmd_ls(scene)
    if cmd == "look":
        return CommandResult(message=scene.description, update_art=True)
    if cmd in ("bag", "inventory"):
        return CommandResult(message=inventory.list_items())
    if cmd == "cat":
        return _cmd_cat(arg, scene, scene_mgr, inventory)
    if cmd == "take":
        return _cmd_take(arg, scene, inventory)
    if cmd == "use":
        return _cmd_use(arg, scene, scene_mgr, inventory)

    # Advanced commands (unlocked by flags)
    if cmd == "ssh":
        return _cmd_ssh(arg, scene, scene_mgr, inventory)
    if cmd == "scan":
        return _cmd_scan(scene, scene_mgr)
    if cmd == "grep":
        return _cmd_grep(arg, scene, scene_mgr, inventory)
    if cmd == "decrypt":
        return _cmd_decrypt(arg, scene, scene_mgr, inventory)
    if cmd == "history":
        return _cmd_history(scene, scene_mgr)

    # Check scene-specific commands
    if cmd in scene.commands:
        sc = scene.commands[cmd]
        result = CommandResult(message=sc.get("response", ""))
        if "add_flag" in sc:
            result.add_flag = sc["add_flag"]
        if "transition" in sc:
            result.scene_change = sc["transition"]
        return result

    return CommandResult(
        message=f"[dim]不认识的命令：{cmd}。输入 [bold]help[/bold] 查看可用命令。[/dim]"
    )


def _cmd_help(scene_mgr: SceneManager) -> CommandResult:
    lines = [
        "[bold]可用命令：[/bold]",
        "  [cyan]ls[/cyan]          - 查看当前场景的物品",
        "  [cyan]look[/cyan]        - 重新查看场景",
        "  [cyan]cat <物品>[/cyan]  - 查看/阅读某个物品",
        "  [cyan]take <物品>[/cyan] - 拾取物品",
        "  [cyan]use <物品> [目标][/cyan] - 使用道具",
        "  [cyan]bag[/cyan]         - 查看背包",
        "  [cyan]help[/cyan]        - 显示本帮助",
    ]
    if scene_mgr.has_flag("unlock_advanced"):
        lines.extend([
            "",
            "[bold]高级命令：[/bold]",
            "  [cyan]ssh <地址>[/cyan]     - 连接到远程机器",
            "  [cyan]scan[/cyan]           - 扫描网络节点",
            "  [cyan]grep <关键词> [文件][/cyan] - 搜索文件内容",
            "  [cyan]decrypt <文件>[/cyan] - 解密文件",
            "  [cyan]history[/cyan]        - 查看命令历史",
        ])
    return CommandResult(message="\n".join(lines))


def _cmd_ls(scene) -> CommandResult:
    items = scene.list_visible_items()
    if not items:
        return CommandResult(message="[dim]这里没有什么东西了。[/dim]")
    item_list = "  ".join(f"[cyan]{name}[/cyan]" for name in items)
    return CommandResult(message=item_list)


def _cmd_cat(arg: str, scene, scene_mgr, inventory) -> CommandResult:
    if not arg:
        return CommandResult(message="[dim]cat 什么？试试 [bold]cat <物品名>[/bold][/dim]")

    # Check if cat triggers a scene transition
    trigger = f"cat_{arg}"
    inv_names = list(inventory.items.keys())
    transition = scene.check_transition(trigger, scene_mgr.flags, inv_names)
    if transition:
        # Read the item content first, then transition
        content = scene.read_item(arg)
        message = content if content and arg in scene.items else ""
        if transition.get("message"):
            message = (message + "\n\n" + transition["message"]) if message else transition["message"]
        result = CommandResult(
            message=message,
            scene_change=transition.get("target_scene", ""),
        )
        if "add_flag" in transition:
            result.add_flag = transition["add_flag"]
        return result

    # Check inventory first, then scene
    if inventory.has(arg):
        item_data = None
        for s_item in scene.items.values():
            if s_item["name"] == arg:
                item_data = s_item
                break
        if item_data and "content" in item_data:
            return CommandResult(message=item_data["content"])
        return CommandResult(message=f"[yellow]{arg}[/yellow] 没什么可读的。")

    content = scene.read_item(arg)
    return CommandResult(message=content)


def _cmd_take(arg: str, scene, inventory) -> CommandResult:
    if not arg:
        return CommandResult(message="[dim]take 什么？试试 [bold]take <物品名>[/bold][/dim]")
    success, msg, desc = scene.take_item(arg)
    if success:
        return CommandResult(message=inventory.add(arg, desc))
    return CommandResult(message=msg)


def _cmd_use(arg: str, scene, scene_mgr, inventory) -> CommandResult:
    if not arg:
        return CommandResult(message="[dim]use 什么？试试 [bold]use <物品> [目标][/bold][/dim]")

    parts = arg.split(maxsplit=1)
    item_name = parts[0]
    target = parts[1] if len(parts) > 1 else ""

    if not inventory.has(item_name):
        return CommandResult(message=f"你没有 [yellow]{item_name}[/yellow]。")

    # Check for scene transitions triggered by use
    trigger = f"use_{item_name}_{target}" if target else f"use_{item_name}"
    inv_names = list(inventory.items.keys())
    transition = scene.check_transition(trigger, scene_mgr.flags, inv_names)

    if transition:
        result = CommandResult(
            message=transition.get("message", f"你使用了 {item_name}。"),
            scene_change=transition.get("target_scene", ""),
        )
        if "add_flag" in transition:
            result.add_flag = transition["add_flag"]
        if transition.get("consume_item", False):
            inventory.remove(item_name)
        return result

    return CommandResult(
        message=f"在这里没法用 [yellow]{item_name}[/yellow]" + (f" 对 [yellow]{target}[/yellow]" if target else "") + "。"
    )


def _cmd_ssh(arg: str, scene, scene_mgr, inventory) -> CommandResult:
    if not arg:
        if not scene_mgr.has_flag("unlock_advanced"):
            return CommandResult(message="[dim]不认识的命令：ssh。输入 [bold]help[/bold] 查看可用命令。[/dim]")
        return CommandResult(message="[dim]ssh 到哪里？试试 [bold]ssh <地址>[/bold][/dim]")

    # Always check for scene transitions first (some scenes use ssh to progress)
    trigger = f"ssh_{arg}"
    inv_names = list(inventory.items.keys())
    transition = scene.check_transition(trigger, scene_mgr.flags, inv_names)
    if transition:
        result = CommandResult(
            message=transition.get("message", f"连接到 {arg}..."),
            scene_change=transition.get("target_scene", ""),
        )
        if "add_flag" in transition:
            result.add_flag = transition["add_flag"]
        return result

    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：ssh。输入 [bold]help[/bold] 查看可用命令。[/dim]")

    return CommandResult(message=f"[red]连接失败：{arg} 无法访问。[/red]")


def _cmd_scan(scene, scene_mgr) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：scan。输入 [bold]help[/bold] 查看可用命令。[/dim]")

    scan_cmd = scene.commands.get("scan")
    if scan_cmd:
        result = CommandResult(message=scan_cmd.get("response", "扫描中..."))
        if "add_flag" in scan_cmd:
            result.add_flag = scan_cmd["add_flag"]
        return result

    return CommandResult(message="[dim]扫描完成。未发现新的网络节点。[/dim]")


def _cmd_grep(arg: str, scene, scene_mgr, inventory) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：grep。输入 [bold]help[/bold] 查看可用命令。[/dim]")
    if not arg:
        return CommandResult(message="[dim]grep 什么？试试 [bold]grep <关键词> [文件][/bold][/dim]")

    grep_cmd = scene.commands.get("grep")
    if grep_cmd:
        # Check if the keyword matches (case-insensitive)
        keywords = grep_cmd.get("keywords", {})
        search_term = arg.split()[0].lower()
        # Try exact match first, then case-insensitive
        matched_key = None
        if search_term in keywords:
            matched_key = search_term
        else:
            for key in keywords:
                if key.lower() == search_term:
                    matched_key = key
                    break
        if matched_key is not None:
            result = CommandResult(message=keywords[matched_key])
            if "add_flag" in grep_cmd:
                result.add_flag = grep_cmd["add_flag"]
            return result

    return CommandResult(message=f"[dim]没有找到匹配 '{arg}' 的内容。[/dim]")


def _cmd_decrypt(arg: str, scene, scene_mgr, inventory) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：decrypt。输入 [bold]help[/bold] 查看可用命令。[/dim]")
    if not arg:
        return CommandResult(message="[dim]decrypt 什么？试试 [bold]decrypt <文件>[/bold][/dim]")

    trigger = f"decrypt_{arg}"
    inv_names = list(inventory.items.keys())
    transition = scene.check_transition(trigger, scene_mgr.flags, inv_names)
    if transition:
        result = CommandResult(
            message=transition.get("message", "解密中..."),
            scene_change=transition.get("target_scene", ""),
        )
        if "add_flag" in transition:
            result.add_flag = transition["add_flag"]
        return result

    return CommandResult(message=f"[red]无法解密 {arg}。也许你需要先找到密钥。[/red]")


def _cmd_history(scene, scene_mgr) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：history。输入 [bold]help[/bold] 查看可用命令。[/dim]")

    history_cmd = scene.commands.get("history")
    if history_cmd:
        result = CommandResult(message=history_cmd.get("response", ""))
        if "add_flag" in history_cmd:
            result.add_flag = history_cmd["add_flag"]
        return result

    return CommandResult(message="[dim]这台机器上没有命令历史。[/dim]")
