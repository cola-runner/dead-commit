"""CLI Puzzle Game - Textual App."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, RichLog, Static
from textual.binding import Binding
from rich.text import Text
from rich_pixels import Pixels
from PIL import Image

from engine.scene import SceneManager
from engine.inventory import Inventory
from engine.command import parse_command
from engine import save

CONTENT_DIR = Path(__file__).parent / "content"
SCENE_IMAGES_DIR = CONTENT_DIR / "scene_images"

# Map scene ascii_art references to image files
ART_TO_IMAGE = {
    "locked_room.txt": "locked_room.png",
    "server_room.txt": "server_room.png",
    "encrypted_terminal.txt": "encrypted_terminal.png",
    "final_message.txt": "final_message.png",
    "title.txt": "title.png",
}


def load_scene_pixels(art_filename: str) -> Pixels | None:
    """Load a scene image and convert to terminal pixels, filling the panel."""
    image_name = ART_TO_IMAGE.get(art_filename, art_filename)
    png_path = SCENE_IMAGES_DIR / image_name
    if not png_path.exists():
        png_path = SCENE_IMAGES_DIR / Path(image_name).with_suffix(".png")
    if not png_path.exists():
        return None

    img = Image.open(png_path)
    # Use full terminal width; half-block chars double vertical resolution
    # so we render at (width, height/2) to fill the panel
    return Pixels.from_image(img)


class ScenePanel(Static):
    """Top panel displaying pixel art scene."""

    DEFAULT_CSS = """
    ScenePanel {
        height: 1fr;
        background: #080c14;
        padding: 0 1;
        overflow-y: auto;
        content-align: center middle;
    }
    """


class TerminalLog(RichLog):
    """Bottom panel for narrative text and command output."""

    DEFAULT_CSS = """
    TerminalLog {
        height: 2fr;
        background: #0c1018;
        color: #c8d6e5;
        border-top: solid #2a3a4a;
        padding: 0 1;
    }
    """


class CommandInput(Input):
    """Command input field."""

    DEFAULT_CSS = """
    CommandInput {
        dock: bottom;
        background: #0c1018;
        color: #5ce0d8;
        border: none;
        height: 3;
        padding: 0 1;
    }
    CommandInput:focus {
        border: none;
    }
    """


class PuzzleApp(App):
    """Main puzzle game application."""

    CSS = """
    Screen {
        background: #080c12;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit_game", "退出", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.scene_mgr = SceneManager()
        self.inventory = Inventory()
        self.started = False

    def compose(self) -> ComposeResult:
        yield ScenePanel(id="scene")
        with Vertical():
            yield TerminalLog(id="terminal", markup=True, wrap=True)
            yield CommandInput(
                placeholder="输入命令... (help 查看帮助)",
                id="cmd_input",
            )

    def _update_scene_art(self, art_filename: str):
        """Update the scene panel with pixel art from image."""
        scene_panel = self.query_one("#scene", ScenePanel)
        pixels = load_scene_pixels(art_filename)
        if pixels:
            scene_panel.update(pixels)
        else:
            # Fallback to text art
            art_path = CONTENT_DIR / "ascii_art" / art_filename
            if art_path.exists():
                scene_panel.update(art_path.read_text())

    def on_mount(self) -> None:
        self.scene_mgr.load_chapter("chapter1.json")
        terminal = self.query_one("#terminal", TerminalLog)

        # Show title image
        self._update_scene_art("title.txt")

        # Check for saved game
        saved = save.load_game()
        if saved:
            terminal.write(
                "[bold]发现存档。[/bold]\n"
                "[dim]输入 [bold]continue[/bold] 继续游戏，"
                "或 [bold]new[/bold] 开始新游戏。[/dim]\n"
            )
        else:
            terminal.write(
                "[bold cyan]《离线信号》[/bold cyan]\n\n"
                "[dim]输入 [bold]start[/bold] 开始游戏。[/dim]\n"
            )

        self.query_one("#cmd_input", CommandInput).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        if not raw:
            return

        input_widget = self.query_one("#cmd_input", CommandInput)
        terminal = self.query_one("#terminal", TerminalLog)

        input_widget.value = ""

        # Show command echo
        terminal.write(Text(f"> {raw}", style="bold #5ce0d8"))

        # Handle pre-game commands
        if not self.started:
            self._handle_pregame(raw.lower(), terminal)
            return

        # Handle quit
        if raw.lower() in ("quit", "exit"):
            self._save_and_quit()
            return

        # Handle decrypt with key as separate argument
        if raw.lower().startswith("decrypt "):
            parts = raw.split()
            if len(parts) == 3:
                raw = f"decrypt {parts[1]}_{parts[2]}"
            elif len(parts) == 2:
                raw = f"decrypt {parts[1]}"

        # Parse and execute command
        result = parse_command(raw, self.scene_mgr, self.inventory)

        if result.add_flag:
            self.scene_mgr.add_flag(result.add_flag)

        if result.message:
            terminal.write("")
            terminal.write(result.message)

        if result.scene_change:
            scene, enter_msg = self.scene_mgr.go_to(result.scene_change)
            if scene.ascii_art_file:
                self._update_scene_art(scene.ascii_art_file)
            if enter_msg:
                terminal.write("")
                terminal.write(enter_msg)

            # Auto-save on scene change
            scene_id, flags = self.scene_mgr.to_save_data()
            save.save_game(scene_id, self.inventory.to_dict(), flags)

        elif result.update_art and self.scene_mgr.current:
            if self.scene_mgr.current.ascii_art_file:
                self._update_scene_art(self.scene_mgr.current.ascii_art_file)

        terminal.write("")

    def _handle_pregame(self, cmd: str, terminal: TerminalLog):
        if cmd == "start" or cmd == "new":
            save.delete_save()
            self.started = True
            self._start_game(terminal)
        elif cmd == "continue":
            saved = save.load_game()
            if saved:
                self.started = True
                self.scene_mgr.restore(saved["scene_id"], saved["flags"])
                self.inventory.from_dict(saved["inventory"])
                scene = self.scene_mgr.current
                if scene:
                    if scene.ascii_art_file:
                        self._update_scene_art(scene.ascii_art_file)
                    terminal.write("[bold]存档已加载。[/bold]\n")
                    terminal.write(scene.description)
                    terminal.write("")
            else:
                terminal.write("[dim]没有找到存档。输入 [bold]start[/bold] 开始新游戏。[/dim]\n")
        elif cmd == "quit" or cmd == "exit":
            self.exit()
        else:
            terminal.write("[dim]输入 [bold]start[/bold] 开始游戏。[/dim]\n")

    def _start_game(self, terminal: TerminalLog):
        scene, enter_msg = self.scene_mgr.go_to("locked_room")
        if scene.ascii_art_file:
            self._update_scene_art(scene.ascii_art_file)
        terminal.clear()
        if enter_msg:
            terminal.write(enter_msg)
            terminal.write("")

        # Auto-save initial state
        scene_id, flags = self.scene_mgr.to_save_data()
        save.save_game(scene_id, self.inventory.to_dict(), flags)

    def _save_and_quit(self):
        if self.scene_mgr.current:
            scene_id, flags = self.scene_mgr.to_save_data()
            save.save_game(scene_id, self.inventory.to_dict(), flags)
        self.exit()

    def action_quit_game(self):
        self._save_and_quit()
