import os

import platform
import subprocess
from functools import lru_cache

from datetime import datetime

from pathlib import Path

import psutil

from PIL import Image

from rich.style import Style

from rich.text import Text

from textual.app import App, ComposeResult

from textual.containers import Horizontal, Vertical, VerticalScroll

from textual.widgets import Footer, Input, RichLog, Static

BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = BASE_DIR / "assets" / "ebisu.png"

# ---------------------------------------------------------

# SYSTEM INFORMATION

# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_gpu():
    cmds = (
        ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
        ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_VideoController).Name"],
    )
    for cmd in cmds:
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout.strip()
        except Exception:
            continue
        if out:
            return out.splitlines()[0].strip()
    return "Unavailable"


def get_system_info():

    try:

        ram = f"{psutil.virtual_memory().total / (1024 ** 3):.1f} GB"

    except Exception:

        ram = "Unavailable"

    try:

        cpu = platform.processor().strip() or platform.machine()

    except Exception:

        cpu = "Unknown"

    if len(cpu) > 34:

        cpu = cpu[:31] + "..."

    now = datetime.now().astimezone()

    return {

        "os": f"{platform.system()} {platform.release()}",

        "cpu": cpu,

        "ram": ram,

        "gpu": get_gpu(),

        "python": platform.python_version(),

        "time": now.strftime("%H:%M:%S"),

        "date": now.strftime("%Y-%m-%d"),

        "timezone": now.strftime("%Z (UTC%z)"),

        "location": os.getenv("EBISU_LOCATION", "Not configured"),

    }

# ---------------------------------------------------------

# LOGO RENDERER

# ---------------------------------------------------------

def render_ebisu_logo(image_path, width=30):

    """

    Render an image using Unicode half-block characters.

    Dark, low-saturation pixels are treated as background.

    This is an approximation for checkerboard-background images.

    A genuinely transparent PNG produces the best result.

    """

    image_path = Path(image_path)

    if not image_path.is_file():

        return Text(

            "\n       EBISU\n"

            "       恵比寿\n\n"

            "  Logo not found\n"

            "  assets/ebisu.png",

            style="dim",

        )

    # Flood-fill the white backdrop from the edges to transparent (inner whites stay),
    # and lift the black outlines to navy so they show on a dark terminal.
    image = Image.open(image_path).convert("RGBA")
    px = image.load()
    w, h = image.size
    white = lambda x, y: min(px[x, y][:3]) >= 238
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if 0 <= x < w and 0 <= y < h and px[x, y][3] and white(x, y):
            px[x, y] = (0, 0, 0, 0)
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and max(r, g, b) < 70:
                px[x, y] = (38, 70, 130, 255)

    new_width = max(1, width)

    new_height = max(

        2,

        round(image.height * new_width / image.width),

    )

    # Each terminal character represents two vertical pixels.

    if new_height % 2:

        new_height += 1

    image = image.resize(

        (new_width, new_height),

        Image.Resampling.LANCZOS,

    )

    output = Text()

    def get_color(x, y):

        r, g, b, a = image.getpixel((x, y))

        if a < 100:

            return None

        return f"#{r:02x}{g:02x}{b:02x}"

    for y in range(0, new_height, 2):

        for x in range(new_width):

            top = get_color(x, y)

            bottom = get_color(x, y + 1)

            if top and bottom:

                output.append(

                    "▀",

                    style=Style(color=top, bgcolor=bottom),

                )

            elif top:

                output.append(

                    "▀",

                    style=Style(color=top),

                )

            elif bottom:

                output.append(

                    "▄",

                    style=Style(color=bottom),

                )

            else:

                output.append(" ")

        if y + 2 < new_height:

            output.append("\n")

    return output

# ---------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------

VERSION = "0.1.0"
PRIMARY = "#98A86F"
ACCENT = "#485034"
MUTED = "#636A4C"

GLYPHS = {
    "E": ["█████", "█    ", "████ ", "█    ", "█████"],
    "B": ["████ ", "█   █", "████ ", "█   █", "████ "],
    "I": ["█████", "  █  ", "  █  ", "  █  ", "█████"],
    "S": [" ████", "█    ", " ███ ", "    █", "████ "],
    "U": ["█   █", "█   █", "█   █", "█   █", " ███ "],
}


def blend(t):
    a = [int(PRIMARY[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(ACCENT[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def render_banner(word="EBISU"):
    out = Text()
    for row in range(5):
        out.append("  ".join(GLYPHS[c][row] for c in word), style=Style(color=blend(row / 4), bold=True))
        if row < 4:
            out.append("\n")
    return out


def section(title, rows):
    out = Text(title + "\n", style=f"bold {PRIMARY}")
    for label, value in rows:
        out.append(f"{label}: " if label else "", style=MUTED)
        out.append(value + "\n", style=ACCENT)
    return out


class EbisuApp(App):

    TITLE = "EBISU"

    CSS = f"""
    Screen {{ background: transparent; color: $text; }}
    #banner {{ height: 5; margin: 1 2 0 2; }}
    #tagline {{ height: 1; margin: 0 2; color: {MUTED}; }}
    #dashboard {{
        height: 1fr;
        margin: 1 1 0 1;
        border: round {PRIMARY};
        border-title-color: {ACCENT};
        border-subtitle-color: {MUTED};
        background: transparent;
    }}
    #left {{ width: 42%; min-width: 40; padding: 1; align: center top; border-right: solid {PRIMARY}; }}
    #art {{ width: 100%; height: 18; content-align: center middle; overflow: hidden; }}
    #wordmark {{ height: 2; width: 100%; content-align: center middle; color: {ACCENT}; text-style: bold; }}
    #right {{ width: 58%; padding: 1 2; scrollbar-size: 0 0; }}
    #workspace {{ height: auto; border: round {PRIMARY}; padding: 0 1; margin: 1 0; color: {MUTED}; }}
    #welcome {{ margin: 0 2; height: 1; }}
    #conversation {{ height: 4; margin: 0 1; padding: 0 1; border: round {PRIMARY}; border-title-color: {ACCENT}; background: transparent; }}
    #input-row {{ height: 3; margin: 0 1; }}
    #prompt-label {{ width: 10; padding: 1 0; color: {PRIMARY}; text-style: bold; }}
    #task-input {{ width: 1fr; border: round {PRIMARY}; background: transparent; }}
    #task-input:focus {{ border: round {ACCENT}; }}
    #notice {{ height: 1; margin: 0 2; color: {MUTED}; }}
    Footer {{ background: transparent; color: {MUTED}; }}
    """

    BINDINGS = [("ctrl+c", "quit", "Quit"), ("ctrl+l", "clear_log", "Clear log"), ("f1", "help", "Help")]

    def compose(self) -> ComposeResult:
        yield Static(render_banner(), id="banner")
        yield Static("EBISU // LOCAL CODING AGENT · MODEL-DRIVEN • TOOL-ENABLED • LOCAL-FIRST", id="tagline")
        with Horizontal(id="dashboard"):
            with Vertical(id="left"):
                yield Static(render_ebisu_logo(LOGO_PATH, width=36), id="art")
                yield Static("EBISU  /  恵比寿", id="wordmark")
            with VerticalScroll(id="right"):
                yield Static("", id="monitor")
                yield Static("", id="specs")
                yield Static(section("MODEL STATUS", [
                    ("Provider", "not connected"), ("Inference", "offline"),
                    ("Tools", "preview only"), ("Session", "ready")]))
                yield Static(f"WORKSPACE\n{Path.cwd()}", id="workspace")
                yield Static(section("SHORTCUTS", [
                    ("/help", "Show commands"), ("/status", "Session details"),
                    ("/clear", "Clear session log"), ("/exit", "Quit Ebisu")]))
                yield Static(section("AVAILABLE TOOLS", [
                    ("filesystem", "list_files, read_file, search_files"),
                    ("editing", "apply_patch, write_file"),
                    ("execution", "run_command, run_tests"),
                    ("git", "git_status, git_diff")]))
                yield Static(section("AGENT CAPABILITIES", [
                    ("", "Repository understanding and navigation"),
                    ("", "Targeted code editing and refactoring"),
                    ("", "Test execution and verification"),
                    ("", "Multi-step task planning"),
                    ("", "Local LLM inference")]))
        yield Static("Welcome to Ebisu! Type your message or /help for commands.", id="welcome")
        yield RichLog(id="conversation", wrap=True, markup=True, highlight=False)
        with Horizontal(id="input-row"):
            yield Static("ebisu >", id="prompt-label")
            yield Input(placeholder="Describe a coding task or type /help", id="task-input")
        yield Static("UI prototype only — model and tools are not connected.", id="notice")
        yield Footer()

    def on_mount(self) -> None:
        dash = self.query_one("#dashboard")
        dash.border_title = f"Ebisu v{VERSION} · YOUR TERMINAL WORKSPACE"
        dash.border_subtitle = "/help for commands"
        log = self.query_one("#conversation", RichLog)
        log.border_title = "SESSION LOG"
        log.write("[bold]Ebisu session initialized.[/bold]")
        log.write(f"[{ACCENT}]Local model: not connected.[/]")
        log.write("[dim]Enter a coding task or type /help.[/]")
        self.refresh_system_info()
        self.set_interval(1, self.refresh_system_info)
        self.query_one("#task-input", Input).focus()

    def refresh_system_info(self) -> None:
        i = get_system_info()
        self.query_one("#monitor", Static).update(section("SYSTEM MONITOR", [
            ("TIME", i["time"]), ("DATE", i["date"]), ("ZONE", i["timezone"]),
            ("LOCATION", i["location"])]))
        self.query_one("#specs", Static).update(section("SYSTEM SPECS", [
            ("OS", i["os"]), ("CPU", i["cpu"]), ("RAM", i["ram"]), ("GPU", i["gpu"]), ("Python", i["python"])]))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if not value:
            return
        log = self.query_one("#conversation", RichLog)
        self.query_one("#task-input", Input).value = ""
        command = value.lower()
        if command in {"/exit", "/quit"}:
            self.exit()
        elif command == "/help":
            log.write("[bold]COMMANDS[/bold]  /help  /status  /clear  /exit")
        elif command == "/status":
            log.write("[bold]SYSTEM STATUS[/bold]")
            for key, val in get_system_info().items():
                log.write(f"{key}: {val}")
            log.write("Model provider: not connected")
            log.write("Agent runtime: UI prototype")
        elif command == "/clear":
            log.clear()
            log.write("[dim]Session log cleared.[/]")
        elif value.startswith("/"):
            log.write(f"[dim]Unknown command: {value}. Type /help.[/]")
        else:
            log.write(f"[bold]you >[/bold] {value}")
            log.write(f"[{ACCENT}]ebisu >[/] Task received. The agent runtime is not connected yet.")

    def action_clear_log(self) -> None:
        self.query_one("#conversation", RichLog).clear()

    def action_help(self) -> None:
        self.query_one("#conversation", RichLog).write("[bold]COMMANDS[/bold]  /help  /status  /clear  /exit")


if __name__ == "__main__":
    EbisuApp().run()
