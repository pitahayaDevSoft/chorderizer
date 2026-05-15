"""
tui_widgets.py — Custom Textual widgets for Chorderizer
"""

from typing import Any, Dict, List, Set

from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView, Static

from .icons import IconManager
from .translations import Translations


class PianoWidget(Static):
    """FAT Piano Keyboard with Note Labels."""

    DEFAULT_CSS = "PianoWidget { height: 8; width: 100%; }"

    def __init__(self, active_notes: Set[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.active_notes = active_notes or set()
        self.base_midi = 48

    def update_notes(self, notes: List[int]):
        self.active_notes = set()
        for n in notes:
            pc = n % 12
            self.active_notes.add(48 + pc)
            self.active_notes.add(60 + pc)
        self.refresh()

    def render(self) -> Panel:
        rows = [Text() for _ in range(4)]
        label_row = Text()
        white_names = ["C", "D", "E", "F", "G", "A", "B"]
        white_indices = [0, 2, 4, 5, 7, 9, 11]

        for oct in range(2):
            for i, w_idx in enumerate(white_indices):
                midi = self.base_midi + (oct * 12) + w_idx
                is_active = midi in self.active_notes
                color = "bright_cyan" if is_active else "white"

                has_black = w_idx in {0, 2, 5, 7, 9}
                black_active = (midi + 1) in self.active_notes
                black_color = "cyan" if black_active else "grey15"

                for r in range(4):
                    if r < 2 and has_black:
                        rows[r].append("██", style=color)
                        rows[r].append("█", style=black_color)
                    else:
                        rows[r].append("███", style=color)
                    rows[r].append("|", style="grey37")

                label_color = "bold cyan" if is_active else "bold white"
                label_row.append(f"{white_names[i]:^3}", style=label_color)
                label_row.append("|", style="grey37")

        full_piano = Text("\n").join(rows)
        full_piano.append("\n")
        full_piano.append(label_row)
        return Panel(
            Align.center(full_piano),
            title=f"[bold blue]{Translations.t('piano_board')}[/bold blue]",
            border_style="bright_blue",
        )


class FretboardWidget(Static):
    """Refined Guitar Fretboard visualizer using clean dots or note labels."""

    DEFAULT_CSS = "FretboardWidget { height: 11; width: 100%; }"

    INTERVAL_LABELS = {
        0: "R",
        1: "b2",
        2: "2",
        3: "b3",
        4: "3",
        5: "4",
        6: "b5",
        7: "5",
        8: "b6",
        9: "6",
        10: "b7",
        11: "7",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scale_notes_pc = set()
        self.chord_notes_midi = set()
        self.tonic_pc = 0
        self.strings = [64, 59, 55, 50, 45, 40]
        self.string_names = ["e", "B", "G", "D", "A", "E"]
        self.display_mode = "simple"  # 'simple' or 'advanced'
        self.theory = None  # Will be set by app

    def update_view(
        self,
        scale_pcs: Set[int],
        chord_midis: List[int],
        tonic_pc: int,
        display_mode: str = "simple",
    ):
        self.scale_notes_pc = scale_pcs
        self.chord_notes_midi = set(chord_midis)
        self.tonic_pc = tonic_pc
        self.display_mode = display_mode
        self.refresh()

    def render(self) -> Panel:
        # Dynamic width calculation
        width = self.size.width
        num_frets = (width - 10) // 4
        num_frets = max(12, min(num_frets, 24))

        fretboard = Text()
        header = Text("      ")
        for f in range(num_frets + 1):
            header.append(f"{f:<4}", style="dim")
        fretboard.append(header)
        fretboard.append("\n")

        for i, start_midi in enumerate(self.strings):
            line = Text(f" {self.string_names[i]} ║")
            for fret in range(num_frets + 1):
                midi = start_midi + fret
                pc = midi % 12
                is_chord_note = midi in self.chord_notes_midi
                is_scale_note = pc in self.scale_notes_pc
                is_tonic = pc == self.tonic_pc

                style = "grey37"
                fret_content = "───"

                if is_chord_note or is_scale_note or is_tonic:
                    if self.display_mode == "advanced":
                        # Calculate interval relative to tonic
                        interval = (pc - self.tonic_pc) % 12
                        fret_content = f"{self.INTERVAL_LABELS.get(interval, ''):^3}"
                    else:
                        fret_content = f" {IconManager.get('dot')} "

                    if is_chord_note:
                        style = "bold bright_cyan"
                    elif is_tonic:
                        style = "bold yellow"
                    else:
                        style = "bold white"

                line.append(fret_content, style=style)
                line.append("|", style="grey37")
            fretboard.append(line)
            fretboard.append("\n")

        mode_label = f" ({self.display_mode.upper()})"
        return Panel(
            Align.center(fretboard),
            title=f"[bold yellow]{Translations.t('guitar_fretboard')}{mode_label}[/bold yellow]",
            border_style="yellow",
        )


class GuitarTabWidget(Static):
    """Visualizador de tablatura con Panel."""

    DEFAULT_CSS = "GuitarTabWidget { height: 100%; width: 100%; }"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chord_name = "None"
        self.tab_lines = []

    def update_tab(self, chord_name: str, tab_lines: List[str]):
        self.chord_name = chord_name
        self.tab_lines = tab_lines
        self.refresh()

    def render(self) -> Panel:
        content = Text()
        for line in self.tab_lines:
            if "|" in line:
                content.append(line.replace(" ", ""), style="bright_green")
                content.append("\n")

        return Panel(
            Align.center(content, vertical="middle"),
            title=f"[bold yellow]{Translations.t('tabs_title', chord_name=self.chord_name)}[/bold yellow]",
            border_style="bright_cyan",
        )


class ProgressionItem(ListItem):
    """Representa un acorde en la lista de progresión."""

    def __init__(self, chord_data: Dict[str, Any]):
        super().__init__()
        self.chord_data = chord_data

    def compose(self) -> ComposeResult:
        yield Label(f" {self.chord_data['name']} [dim]({self.chord_data['degree']})[/]")


class ProgressionPanel(Static):
    """Panel lateral de la progresión de acordes."""

    DEFAULT_CSS = """
    ProgressionPanel {
        padding: 0;
        background: transparent;
    }
    #prog-list {
        height: 1fr;
    }
    .prog-header {
        background: $accent;
        color: $text-primary;
        text-align: center;
        text-style: bold;
        padding: 1;
    }
    #prog-help {
        text-align: center;
        padding: 1;
        background: $surface;
    }
    #prog-empty {
        text-align: center;
        padding: 2;
        color: $text-muted;
    }
    #prog-empty.hidden {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label(
            f"{IconManager.get('list')} {Translations.t('sidebar_title')}", classes="prog-header"
        )
        yield Label(Translations.t("sidebar_empty_desc"), id="prog-empty")
        prog_list = ListView(id="prog-list")
        prog_list.tooltip = Translations.t("tooltip_prog_list")
        yield prog_list
        yield Label(
            f" [bold][A][/bold] {IconManager.get('plus')} Add  [bold][X][/bold] {IconManager.get('broom')} Clear",
            id="prog-help",
        )

    def add_chord(self, chord_data: Dict[str, Any]):
        self.query_one("#prog-empty", Label).add_class("hidden")
        self.query_one("#prog-list", ListView).append(ProgressionItem(chord_data))

    def clear_prog(self):
        self.query_one("#prog-list", ListView).clear()
        self.query_one("#prog-empty", Label).remove_class("hidden")

    def get_progression_data(self) -> List[Dict[str, Any]]:
        return [
            item.chord_data
            for item in self.query_one("#prog-list", ListView).query(ProgressionItem)
        ]
