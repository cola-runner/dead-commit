"""Command parser for the puzzle game."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.scene import SceneManager
    from engine.inventory import Inventory


import os


def _get_player_name_for_cmd() -> str:
    """Get player name for immersive command responses."""
    try:
        return os.getlogin()
    except OSError:
        return os.environ.get("USER", os.environ.get("USERNAME", "player"))


def _get_pwd_for_scene(scene) -> str:
    """Get a fake pwd based on current scene."""
    _scene_paths = {
        "bedroom": f"/home/{_get_player_name_for_cmd()}",
        "prod_server": "/var/log",
        "code_review": "/repos/nova-geo-core",
        "supply_chain": "/var/vault/forensics",
        "the_mirror": f"/home/{_get_player_name_for_cmd()}",
        "ending": f"/home/{_get_player_name_for_cmd()}",
        "dawn": f"/home/{_get_player_name_for_cmd()}",
        "shadow": f"/home/{_get_player_name_for_cmd()}/.shadow",
        "emergency": "/var/log",
        "defuse": "/opt/nova/deploy",
        "ch2_ending": f"/home/{_get_player_name_for_cmd()}",
    }
    return _scene_paths.get(scene.id, "/unknown") if scene else "/unknown"


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
        return _cmd_ls(scene, scene_mgr)
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
    if cmd == "ps":
        return _cmd_ps(scene, scene_mgr)
    if cmd == "kill":
        return _cmd_kill(arg, scene, scene_mgr, inventory)
    if cmd == "crontab":
        return _cmd_crontab(scene, scene_mgr)
    if cmd == "run":
        return _cmd_run(arg, scene, scene_mgr, inventory)

    # Check scene-specific commands
    if cmd in scene.commands:
        sc = scene.commands[cmd]
        result = CommandResult(message=sc.get("response", ""))
        if "add_flag" in sc:
            result.add_flag = sc["add_flag"]
        if "transition" in sc:
            result.scene_change = sc["transition"]
        return result

    # Friendly messages for common Linux commands that aren't part of the game
    en = scene_mgr.lang == "en"
    _IMMERSIVE = {
        "cd":        ("[dim]No directory switching. Use [bold]ssh[/bold] to move between machines.[/dim]" if en else
                      "[dim]目录切换不可用。用 [bold]ssh[/bold] 在不同机器间移动。[/dim]"),
        "vim":       ("[dim]Editor locked. Use [bold]cat[/bold] to view files.[/dim]" if en else
                      "[dim]编辑器被锁定了。用 [bold]cat[/bold] 查看文件内容。[/dim]"),
        "nano":      ("[dim]Editor locked. Use [bold]cat[/bold] to view files.[/dim]" if en else
                      "[dim]编辑器被锁定了。用 [bold]cat[/bold] 查看文件内容。[/dim]"),
        "sudo":      ("[dim]Access denied. You only have current user privileges.[/dim]" if en else
                      "[dim]权限不足。你只有当前用户的权限。[/dim]"),
        "su":        ("[dim]Cannot switch user.[/dim]" if en else "[dim]无法切换用户。[/dim]"),
        "whoami":    f"[dim]uid=1000({_get_player_name_for_cmd()}) — " + ("You know who you are... but are you sure?" if en else "你知道你是谁……但你确定吗？") + "[/dim]",
        "id":        f"[dim]uid=1000({_get_player_name_for_cmd()}) gid=1000(nova) groups=1000(nova),27(sudo)[/dim]",
        "pwd":       f"[dim]{_get_pwd_for_scene(scene)}[/dim]",
        "rm":        ("[red]Delete the evidence? ...No. You need this.[/red]" if en else
                      "[red]你确定要删除证据？……不。你需要这些。[/red]"),
        "mv":        ("[dim]Files cannot be moved.[/dim]" if en else "[dim]文件不可移动。[/dim]"),
        "cp":        ("[dim]File copy restricted.[/dim]" if en else "[dim]文件复制被限制了。[/dim]"),
        "curl":      ("[dim]Network tools restricted. Use [bold]scan[/bold].[/dim]" if en else
                      "[dim]网络工具被限制了。用 [bold]scan[/bold] 扫描网络。[/dim]"),
        "wget":      ("[dim]Network tools restricted. Use [bold]scan[/bold].[/dim]" if en else
                      "[dim]网络工具被限制了。用 [bold]scan[/bold] 扫描网络。[/dim]"),
        "head":      ("[dim]Use [bold]cat[/bold] to view full content.[/dim]" if en else
                      "[dim]用 [bold]cat[/bold] 查看完整内容。[/dim]"),
        "tail":      ("[dim]Use [bold]cat[/bold] to view full content.[/dim]" if en else
                      "[dim]用 [bold]cat[/bold] 查看完整内容。[/dim]"),
        "find":      ("[dim]Use [bold]ls[/bold] to list files, [bold]grep[/bold] to search.[/dim]" if en else
                      "[dim]用 [bold]ls[/bold] 查看当前场景的文件，用 [bold]grep[/bold] 搜索内容。[/dim]"),
        "man":       ("[dim]No manual available. Type [bold]help[/bold].[/dim]" if en else
                      "[dim]手册不可用。输入 [bold]help[/bold] 查看可用命令。[/dim]"),
        "less":      ("[dim]Use [bold]cat[/bold] to view full content.[/dim]" if en else
                      "[dim]用 [bold]cat[/bold] 查看完整内容。[/dim]"),
        "more":      ("[dim]Use [bold]cat[/bold] to view full content.[/dim]" if en else
                      "[dim]用 [bold]cat[/bold] 查看完整内容。[/dim]"),
        "echo":      ("[dim]...the echo fades into darkness.[/dim]" if en else
                      "[dim]……回声消失在黑暗中。[/dim]"),
        "clear":     ("[dim]Screen cannot be cleared. Everything is logged.[/dim]" if en else
                      "[dim]屏幕无法清除。一切都被记录了。[/dim]"),
        "top":       ("[dim]Use [bold]ps[/bold] to view processes.[/dim]" if en else
                      "[dim]用 [bold]ps[/bold] 查看进程列表。[/dim]"),
        "htop":      ("[dim]Use [bold]ps[/bold] to view processes.[/dim]" if en else
                      "[dim]用 [bold]ps[/bold] 查看进程列表。[/dim]"),
        "ping":      ("[dim]Use [bold]scan[/bold] to discover nodes.[/dim]" if en else
                      "[dim]用 [bold]scan[/bold] 扫描网络节点。[/dim]"),
        "nmap":      ("[dim]Use [bold]scan[/bold] to discover nodes.[/dim]" if en else
                      "[dim]用 [bold]scan[/bold] 扫描网络节点。[/dim]"),
        "netstat":   ("[dim]Use [bold]scan[/bold] to view connections.[/dim]" if en else
                      "[dim]用 [bold]scan[/bold] 扫描网络连接。[/dim]"),
        "ifconfig":  ("[dim]Use [bold]scan[/bold] to view network.[/dim]" if en else
                      "[dim]用 [bold]scan[/bold] 查看网络状态。[/dim]"),
        "ip":        ("[dim]Use [bold]scan[/bold] to view network.[/dim]" if en else
                      "[dim]用 [bold]scan[/bold] 查看网络状态。[/dim]"),
        "systemctl": ("[dim]Service management restricted.[/dim]" if en else "[dim]服务管理被限制了。[/dim]"),
        "service":   ("[dim]Service management restricted.[/dim]" if en else "[dim]服务管理被限制了。[/dim]"),
        "git":       ("[dim]Git operations restricted. Use [bold]cat[/bold] to view code and logs.[/dim]" if en else
                      "[dim]Git 操作被限制了。用 [bold]cat[/bold] 查看代码和日志。[/dim]"),
        "docker":    ("[dim]Container operations restricted.[/dim]" if en else "[dim]容器操作被限制了。[/dim]"),
        "kubectl":   ("[dim]K8s operations require the deploy terminal.[/dim]" if en else
                      "[dim]Kubernetes 操作需要通过部署终端执行。[/dim]"),
        "env":       ("[dim]Environment variables restricted.[/dim]" if en else "[dim]环境变量被限制了。[/dim]"),
        "export":    ("[dim]Environment variables restricted.[/dim]" if en else "[dim]环境变量设置被限制了。[/dim]"),
        "chmod":     ("[dim]Permission change restricted.[/dim]" if en else "[dim]权限修改被限制了。[/dim]"),
        "chown":     ("[dim]Permission change restricted.[/dim]" if en else "[dim]权限修改被限制了。[/dim]"),
    }

    if cmd in _IMMERSIVE:
        return CommandResult(message=_IMMERSIVE[cmd])

    unknown = f"[dim]Unknown command: {cmd}. Type [bold]help[/bold] for available commands.[/dim]" if en else f"[dim]不认识的命令：{cmd}。输入 [bold]help[/bold] 查看可用命令。[/dim]"
    return CommandResult(message=unknown)


def _cmd_help(scene_mgr: SceneManager) -> CommandResult:
    en = scene_mgr.lang == "en"
    if en:
        lines = [
            "[bold]Available commands:[/bold]",
            "  [cyan]ls[/cyan]            - List items in current scene",
            "  [cyan]look[/cyan]          - Re-examine scene",
            "  [cyan]cat <item>[/cyan]    - Read/examine an item",
            "  [cyan]take <item>[/cyan]   - Pick up an item",
            "  [cyan]use <item> [target][/cyan] - Use an item",
            "  [cyan]bag[/cyan]           - View inventory",
            "  [cyan]help[/cyan]          - Show this help",
        ]
        if scene_mgr.has_flag("unlock_advanced"):
            lines.extend([
                "",
                "[bold]Advanced commands:[/bold]",
                "  [cyan]ssh <host>[/cyan]      - Connect to remote machine",
                "  [cyan]scan[/cyan]            - Scan network nodes",
                "  [cyan]grep <keyword>[/cyan]  - Search file contents",
                "  [cyan]decrypt <file>[/cyan]  - Decrypt a file",
                "  [cyan]history[/cyan]         - View command history",
                "  [cyan]ps[/cyan]              - View running processes",
                "  [cyan]kill <PID>[/cyan]      - Terminate a process",
                "  [cyan]crontab[/cyan]         - View scheduled tasks",
                "  [cyan]run <script>[/cyan]    - Execute a script",
            ])
    else:
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
                "  [cyan]ps[/cyan]             - 查看运行中的进程",
                "  [cyan]kill <PID>[/cyan]     - 终止进程",
                "  [cyan]crontab[/cyan]        - 查看定时任务",
                "  [cyan]run <脚本>[/cyan]     - 执行脚本",
            ])
    return CommandResult(message="\n".join(lines))


def _cmd_ls(scene, scene_mgr=None) -> CommandResult:
    items = scene.list_visible_items()
    en = scene_mgr.lang == "en" if scene_mgr else False
    if not items:
        return CommandResult(message="[dim]Nothing here.[/dim]" if en else "[dim]这里没有什么东西了。[/dim]")
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


def _cmd_ps(scene, scene_mgr) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：ps。输入 [bold]help[/bold] 查看可用命令。[/dim]")

    ps_cmd = scene.commands.get("ps")
    if ps_cmd:
        result = CommandResult(message=ps_cmd.get("response", ""))
        if "add_flag" in ps_cmd:
            result.add_flag = ps_cmd["add_flag"]
        return result

    return CommandResult(message="[dim]没有运行中的特殊进程。[/dim]")


def _cmd_kill(arg: str, scene, scene_mgr, inventory) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：kill。输入 [bold]help[/bold] 查看可用命令。[/dim]")
    if not arg:
        return CommandResult(message="[dim]kill 什么？试试 [bold]kill <PID>[/bold][/dim]")

    # Check transitions first (like ssh/decrypt)
    trigger = f"kill_{arg}"
    inv_names = list(inventory.items.keys())
    transition = scene.check_transition(trigger, scene_mgr.flags, inv_names)
    if transition:
        result = CommandResult(
            message=transition.get("message", f"终止进程 {arg}..."),
            scene_change=transition.get("target_scene", ""),
        )
        if "add_flag" in transition:
            result.add_flag = transition["add_flag"]
        return result

    # Check scene command keywords (like grep)
    kill_cmd = scene.commands.get("kill")
    if kill_cmd:
        keywords = kill_cmd.get("keywords", {})
        search_term = arg.split()[0]
        matched_key = None
        if search_term in keywords:
            matched_key = search_term
        else:
            for key in keywords:
                if key.lower() == search_term.lower():
                    matched_key = key
                    break
        if matched_key is not None:
            result = CommandResult(message=keywords[matched_key])
            if "add_flag" in kill_cmd:
                result.add_flag = kill_cmd["add_flag"]
            return result

    return CommandResult(message=f"[red]没有找到进程 {arg}。[/red]")


def _cmd_crontab(scene, scene_mgr) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：crontab。输入 [bold]help[/bold] 查看可用命令。[/dim]")

    crontab_cmd = scene.commands.get("crontab")
    if crontab_cmd:
        result = CommandResult(message=crontab_cmd.get("response", ""))
        if "add_flag" in crontab_cmd:
            result.add_flag = crontab_cmd["add_flag"]
        return result

    return CommandResult(message="[dim]没有定时任务。[/dim]")


def _cmd_run(arg: str, scene, scene_mgr, inventory) -> CommandResult:
    if not scene_mgr.has_flag("unlock_advanced"):
        return CommandResult(message="[dim]不认识的命令：run。输入 [bold]help[/bold] 查看可用命令。[/dim]")
    if not arg:
        return CommandResult(message="[dim]run 什么？试试 [bold]run <脚本>[/bold][/dim]")

    # Check transitions (run_execute.sh etc.)
    trigger = f"run_{arg}"
    inv_names = list(inventory.items.keys())
    transition = scene.check_transition(trigger, scene_mgr.flags, inv_names)
    if transition:
        result = CommandResult(
            message=transition.get("message", f"执行 {arg}..."),
            scene_change=transition.get("target_scene", ""),
        )
        if "add_flag" in transition:
            result.add_flag = transition["add_flag"]
        return result

    return CommandResult(message=f"[red]找不到脚本 {arg}。[/red]")
