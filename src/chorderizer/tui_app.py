"""
tui_app.py — Premium Harmony Station Dashboard
"""

import json
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from rich.markup import escape
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import Hit, Hits, Provider
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.theme import Theme
from textual.widgets import (
    Button,
    ContentSwitcher,
    DataTable,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    RadioButton,
    RadioSet,
    RichLog,
    Select,
    Static,
)

from .generators import ChordGenerator, MidiGenerator, TablatureGenerator
from .icons import IconManager
from .theory_utils import MusicTheory
from .translations import Translations
from .tui_widgets import FretboardWidget, GuitarTabWidget, PianoWidget, ProgressionPanel


class ManualScreen(ModalScreen):
    """Full-page manual with professional styling."""

    DEFAULT_CSS = """
    ManualScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #manual-container {
        width: 80%;
        max-width: 100;
        height: auto;
        background: $surface;
        border: thick $accent;
        padding: 2 4;
    }
    .manual-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
        border-bottom: double $accent;
    }
    .manual-section {
        color: $accent;
        text-style: bold;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="manual-container"):
            yield Label(Translations.t("manual_title"), classes="manual-title")
            yield Static(
                f"{Translations.t('manual_workflow')}\n"
                f"{Translations.t('manual_phase_1')}\n"
                f"{Translations.t('manual_phase_2')}\n"
                f"{Translations.t('manual_phase_3')}\n"
                f"{Translations.t('manual_phase_4')}\n\n"
                f"{Translations.t('manual_visualizers')}\n"
                f"{Translations.t('manual_piano')}\n"
                f"{Translations.t('manual_fretboard')}\n"
                f"{Translations.t('manual_tonic_dot')}\n"
                f"{Translations.t('manual_chord_dot')}\n\n"
                f"{Translations.t('manual_shortcuts')}\n"
                f"{Translations.t('manual_add')}\n"
                f"{Translations.t('manual_clear')}\n"
                f"{Translations.t('manual_export')}\n"
                f"{Translations.t('manual_jam')}\n"
                f"{Translations.t('manual_jam_desc')}\n"
                f"{Translations.t('manual_help')}\n"
                f"{Translations.t('manual_quit')}\n\n"
                f"{Translations.t('manual_footer')}",
                markup=True,
            )

    def on_key(self) -> None:
        if len(self.app._screen_stack) > 1:
            self.app.pop_screen()

    def on_click(self) -> None:
        if len(self.app._screen_stack) > 1:
            self.app.pop_screen()


# --- CUSTOM THEORY-DRIVEN THEMES ---
THEME_MONOLITH = Theme(
    name="monolith-ui",
    primary="#4285f4",
    secondary="#c5a9f5",
    accent="#fbbf24",
    background="#060608",
    surface="#252a3a",
    boost="#131720",
    error="#f28b82",
    success="#34a853",
    warning="#fbbf24",
)

THEME_CHROMATIC = Theme(
    name="chromatic-pro",
    primary="#4A90E2",  # Pure Interval Blue
    secondary="#50E3C2",  # Resolution Mint
    accent="#D0021B",  # Tonic Red
    background="#1A1A1A",
    surface="#2C2C2C",
    boost="#252525",
    error="#FF4B2B",
    success="#7ED321",
)

THEME_HARMONIC = Theme(
    name="harmonic-gold",
    primary="#D4AF37",  # Brass/Gold Harmony
    secondary="#8B4513",  # Woodwind Brown
    accent="#FFD700",  # Bright Tonic
    background="#151515",
    surface="#1F1F1F",
    boost="#1A1A1A",
)

THEME_DORIAN = Theme(
    name="dorian-deep",
    primary="#6C5CE7",  # Modal Purple
    secondary="#00CEC9",  # Cool Cyan
    accent="#FAB1A0",  # Soft Tension
    background="#0F0F0F",
    surface="#1E1E1E",
    boost="#151515",
)

THEME_MANGO = Theme(
    name="mango-tropical",
    primary="#FFB347",  # Mango Orange
    secondary="#F0E68C",  # Khaki
    accent="#FFCC80",
    background="#0D1017",
    surface="#12151C",
    boost="#1A1D24",
)

THEME_PITAHAYA = Theme(
    name="pitahaya-bcs",
    primary="#FF2400",  # Pitahaya Red
    secondary="#2E8B57",  # Sea Green
    accent="#FF5C4D",
    background="#05070A",
    surface="#0D1017",
    boost="#12151C",
)


class ConfigManager:
    """Handles persistence of app settings."""

    def __init__(self):
        self.config_path = Path(__file__).parent / "config.json"
        self.settings = self.load()

    def load(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Failed to load config: {e}")
        return {"theme": "monolith-ui", "mouse_enabled": True, "advanced_mode": False}

    def save(self, settings: Dict[str, Any]):
        try:
            with open(self.config_path, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")


class ThemePalette(ModalScreen):
    """Custom palette for themes with LIVE preview on highlight."""

    DEFAULT_CSS = """
    ThemePalette {
        align: center middle;
    }
    #palette-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    #palette-list {
        height: auto;
        max-height: 15;
    }
    """

    def compose(self) -> ComposeResult:
        themes = [
            "monolith-ui",
            "chromatic-pro",
            "harmonic-gold",
            "dorian-deep",
            "mango-tropical",
            "pitahaya-bcs",
            "textual-dark",
            "dracula",
            "nord",
        ]
        with Vertical(id="palette-container"):
            yield Label("[bold]SELECT THEME[/] (Live Preview)", classes="jam-list-label")
            with ListView(id="palette-list"):
                for t in themes:
                    item = ListItem(Label(f" {t.replace('-', ' ').title()} "))
                    item.theme_name = t
                    yield item
            yield Label(
                "[dim]Arrow Keys to Preview • Enter to Select • Esc to Cancel[/]", classes="ml-1"
            )

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item:
            theme_name = getattr(event.item, "theme_name", "textual-dark")
            self.app.theme = theme_name

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item:
            theme_name = getattr(event.item, "theme_name", "textual-dark")
            self.app.active_theme_name = theme_name
            self.app.save_config()
            self.dismiss(theme_name)

    def on_key(self, event: Any) -> None:
        if event.key == "escape":
            # Restore previous theme on cancel
            self.app.theme = getattr(self.app, "active_theme_name", "chromatic-pro")
            self.dismiss()


class ChorderizerProvider(Provider):
    """Custom command provider for Chorderizer actions."""

    async def search(self, query: str) -> Hits:
        """Search for Chorderizer commands."""
        matcher = self.matcher(query)
        app = self.app

        # Expert actions mapping
        commands = [
            (
                "Add Chord to Progression",
                app.action_add_to_progression,
                "Add current selection to composition",
            ),
            (
                "Clear Progression List",
                app.action_clear_progression,
                "Reset the composition sidebar",
            ),
            ("Export to MIDI File", app.action_export_midi, "Humanized MIDI generation"),
            ("Toggle Jam Mode", app.action_toggle_mode, "Switch practice/compose focus"),
            (
                "Toggle Advanced Fretboard",
                app.action_toggle_submode,
                "Show musical degrees on neck",
            ),
            ("Toggle Mouse Support", app.action_toggle_mouse, "Enable/Disable mouse interaction"),
            (
                "Change Theme (Live Preview)",
                app.action_theme_palette,
                "Open theme selector with live preview",
            ),
            (
                "Cycle Pro Theory Themes",
                app.action_cycle_themes,
                "Switch between custom musical palettes",
            ),
            ("Open Manual", lambda: app.push_screen("manual"), "Help and shortcuts guide"),
            ("Quit Application", app.action_quit, "Close Chorderizer"),
        ]

        for title, action, help_text in commands:
            score = matcher.match(title)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(title),
                    action,
                    help=help_text,
                )


class ChorderizerApp(App):
    """Premium Adaptive Dashboard."""

    TITLE = "chorderizer v0.3.2"
    SUB_TITLE = "TropicalDev"

    COMMANDS = App.COMMANDS | {ChorderizerProvider}

    SCREENS = {"manual": ManualScreen, "theme-palette": ThemePalette}

    BINDINGS = [
        Binding(
            "h",
            "push_screen('manual')",
            f"{IconManager.get('manual')} {Translations.t('Manual')}",
            show=True,
        ),
        Binding(
            "f1",
            "push_screen('manual')",
            f"{IconManager.get('manual')} {Translations.t('Manual')}",
            show=False,
        ),
        Binding("q", "quit", f"{IconManager.get('quit')} {Translations.t('Quit')}", show=True),
        Binding(
            "a",
            "add_to_progression",
            f"{IconManager.get('plus')} {Translations.t('Add Chord')}",
            show=True,
        ),
        Binding(
            "x",
            "clear_progression",
            f"{IconManager.get('broom')} {Translations.t('Clear List')}",
            show=True,
        ),
        Binding(
            "e",
            "export_midi",
            f"{IconManager.get('midi')} {Translations.t('Export MIDI')}",
            show=True,
        ),
        Binding(
            "v",
            "toggle_view",
            f"{IconManager.get('view')} {Translations.t('toggle_view')}",
            show=True,
        ),
        Binding(
            "j",
            "toggle_mode",
            f"{IconManager.get('jam')} {Translations.t('mode_jam')}",
            show=True,
        ),
        Binding(
            "s",
            "toggle_submode",
            f"{IconManager.get('gear')} {Translations.t('submode_advanced')}",
            show=True,
        ),
    ]

    CSS = """
    Screen {
        background: transparent;
    }
    #sidebar {
        width: 32;
        background: $boost;
        border-right: thick $primary;
        padding: 1 2;
    }
    #progression-sidebar {
        width: 32;
        background: $boost;
        border-left: thick $primary;
    }
    .config-label {
        margin-top: 1;
        text-style: bold;
        color: $accent;
        border-bottom: solid $accent;
        width: 100%;
        text-align: center;
        background: $boost;
    }
    #center-col {
        width: 1fr;
        background: transparent;
        padding: 0 1;
    }

    PianoWidget {
        height: 8;
        margin: 1 0;
    }
    FretboardWidget {
        height: 11;
        margin-bottom: 1;
    }

    #data-row-container {
        height: 1fr;
        min-height: 10;
        margin: 1 0;
    }
    DataTable {
        width: 60%;
        border: solid $primary;
        margin: 0;
    }
    GuitarTabWidget {
        width: 40%;
        margin-left: 1;
    }

    #status-log {
        height: 8;
        border: solid $accent;
        background: $surface;
        color: $text-secondary;
        padding: 0 1;
        margin-top: 1;
    }

    #btn-export {
        width: 100%;
        margin-top: 2;
        text-style: bold;
    }

    /* JAM MODE SPECIFIC (HORIZONTAL FOCUS) */
    #jam-top-bar {
        height: 3;
        background: $boost;
        border-bottom: thick $accent;
        align: center middle;
    }
    #jam-bottom-row {
        height: 1fr;
        margin-top: 1;
    }
    .config-label-small {
        text-style: bold;
        color: $accent;
    }
    .jam-list-label {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        text-align: center;
    }
    .ml-1 { margin-left: 1; }
    #jam-bottom-row {
        height: 1fr;
        margin-top: 1;
    }
    #jam-mood-container {
        width: 1fr;
        border: solid $primary;
        background: $boost;
        margin-right: 1;
        padding: 1;
    }
    #jam-list-container {
        width: 2fr;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    .dimmed-list {
        opacity: 0.5;
        color: $text-disabled;
        background: $boost;
    }
    .jam-list-label {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        text-align: center;
    }
    #jam-scale-title {
        margin-top: 1;
    }
    #jam-info-container {
        width: 3fr;
        margin-left: 1;
    }
    #jam-fretboard {
        width: 100%;
        margin: 2 0; /* More margin */
    }
    #jam-status-log {
        height: 1fr;
        border: solid $accent;
        background: $surface;
        padding: 0 1;
    }

    .hidden { display: none; }
    Header { background: $primary; color: $background; text-style: bold; }
    Footer { background: $primary; color: $background; text-style: bold; }
    """

    def __init__(self, **kwargs):
        # Configure logging...
        super().__init__(**kwargs)
        self.config_mgr = ConfigManager()
        self.settings = self.config_mgr.settings

        # Register custom themes immediately
        self.register_theme(THEME_MONOLITH)
        self.register_theme(THEME_CHROMATIC)
        self.register_theme(THEME_HARMONIC)
        self.register_theme(THEME_DORIAN)
        self.register_theme(THEME_MANGO)
        self.register_theme(THEME_PITAHAYA)

        self.theory = MusicTheory()
        self.chord_gen = ChordGenerator(self.theory)
        self.midi_gen = MidiGenerator(self.theory)
        self.tab_gen = TablatureGenerator(self.theory)
        self.current_chords = {}
        self.current_midi = {}
        self.mouse_enabled = self.settings.get("mouse_enabled", True)
        self.active_theme_name = self.settings.get("theme", "monolith-ui")
        self.theme = self.active_theme_name
        self.disable_mouse = not self.mouse_enabled

        self.pro_themes = [
            "monolith-ui",
            "chromatic-pro",
            "harmonic-gold",
            "dorian-deep",
            "mango-tropical",
            "pitahaya-bcs",
        ]
        self.current_theme_idx = (
            self.pro_themes.index(self.active_theme_name)
            if self.active_theme_name in self.pro_themes
            else 0
        )

        self.scale_notes_pc = set()
        self.tonic_pc = 0
        self.selected_row_data = None
        self.exit_requested_at = 0.0

    def compose(self) -> ComposeResult:
        yield Header()
        with ContentSwitcher(initial="compose-view"):
            # COMPOSE MODE (SIDEBAR LAYOUT)
            with Horizontal(id="compose-view"):
                with Vertical(id="sidebar"):
                    yield Label(
                        f"{IconManager.get('tonic')} {Translations.t('tonic')}",
                        classes="config-label",
                    )
                    yield Select(
                        [(n, n) for n in self.theory.CHROMATIC_NOTES], id="tonic-select", value="C"
                    )
                    yield Label(
                        f"{IconManager.get('scale')} {Translations.t('scale')}",
                        classes="config-label",
                    )
                    yield Select(
                        [(v["name"], k) for k, v in self.theory.AVAILABLE_SCALES.items()],
                        id="scale-select",
                        value="1",
                    )
                    yield Label(
                        f"{IconManager.get('ext')} {Translations.t('extensions')}",
                        classes="config-label",
                    )
                    with RadioSet(id="extension-set"):
                        yield RadioButton(Translations.t("ext_triads"), value=True)
                        yield RadioButton(Translations.t("ext_6ths"))
                        yield RadioButton(Translations.t("ext_7ths"))
                        yield RadioButton(Translations.t("ext_9ths"))
                        yield RadioButton(Translations.t("ext_11ths"))
                        yield RadioButton(Translations.t("ext_13ths"))
                    yield Label(
                        f"{IconManager.get('inv')} {Translations.t('inversion')}",
                        classes="config-label",
                    )
                    with RadioSet(id="inversion-set"):
                        yield RadioButton(Translations.t("inv_root"), value=True)
                        yield RadioButton(Translations.t("inv_1st"))
                        yield RadioButton(Translations.t("inv_2nd"))
                        yield RadioButton(Translations.t("inv_3rd"))
                    yield Button(
                        f"{IconManager.get('midi')} {Translations.t('export_midi')}",
                        variant="primary",
                        id="btn-export",
                        classes="mt-2",
                    )

                with Vertical(id="center-col"):
                    yield PianoWidget(id="piano")
                    yield FretboardWidget(id="fretboard")
                    with Horizontal(id="data-row-container"):
                        yield DataTable(id="chord-table")
                        yield GuitarTabWidget(id="guitar-tab")
                    yield RichLog(id="status-log", markup=True, max_lines=100)

                yield ProgressionPanel(id="progression-sidebar")

            # JAM MODE (HORIZONTAL FOCUS)
            with Vertical(id="jam-view"):
                with Horizontal(id="jam-top-bar"):
                    yield Label(
                        f"{IconManager.get('jam')} {Translations.t('mode_jam').upper()}",
                        classes="config-label-small",
                    )

                yield FretboardWidget(id="jam-fretboard")

                with Horizontal(id="jam-bottom-row"):
                    with Vertical(id="jam-mood-container"):
                        yield Label(
                            f"{IconManager.get('music')} {Translations.t('moods')}",
                            classes="jam-list-label",
                        )
                        yield ListView(id="jam-mood-list")
                    with Vertical(id="jam-list-container"):
                        yield Label(
                            f"{IconManager.get('tonic')} {Translations.t('tonic')}",
                            classes="jam-list-label",
                        )
                        yield Select(
                            [(n, n) for n in self.theory.CHROMATIC_NOTES],
                            id="jam-tonic-select",
                            value="C",
                        )
                        yield Label(
                            f"{IconManager.get('list')} {Translations.t('jam_scale_list')}",
                            classes="jam-list-label",
                            id="jam-scale-title",
                        )
                        yield ListView(id="jam-scale-list")
                    with Vertical(id="jam-info-container"):
                        yield Label(Translations.t("jam_hint"), classes="config-label-small")
                        yield RichLog(id="jam-status-log", markup=True, max_lines=1000)

        yield Footer()

    def log_status(self, msg: str, title: str = "SYSTEM", icon: str = "\u2139"):
        """Logs in traditional terminal style with prompt. Safe for both modes."""
        switcher = self.query_one(ContentSwitcher)
        target_id = "#status-log" if switcher.current == "compose-view" else "#jam-status-log"

        try:
            log = self.query_one(target_id, RichLog)
        except Exception:
            return

        now = datetime.now().strftime("%H:%M:%S")
        prompt = Text.assemble(
            (f"[{now}] ", "dim white"),
            (f"{icon} ", "bold cyan"),
            (f"{title} ", "bold magenta"),
            ("\u203a ", "bold white"),
            Text.from_markup(f"{msg}"),
        )
        log.write(prompt)

    def on_mount(self) -> None:
        # Apply tooltips here to avoid constructor TypeErrors in some Textual versions
        self.query_one("#tonic-select").tooltip = Translations.t("tooltip_tonic")
        self.query_one("#scale-select").tooltip = Translations.t("tooltip_scale")
        self.query_one("#extension-set").tooltip = Translations.t("tooltip_ext")
        self.query_one("#inversion-set").tooltip = Translations.t("tooltip_inv")
        self.query_one("#btn-export").tooltip = Translations.t("tooltip_export")

        table = self.query_one("#chord-table", DataTable)
        table.tooltip = Translations.t("tooltip_table")
        table.add_columns(Translations.t("degree"), Translations.t("name"), Translations.t("midi"))
        table.cursor_type = "row"

        if not IconManager.has_nerd_font():
            self.log_status(
                "[dim]Tip: Install a [bold cyan]Nerd Font[/] for a richer experience (icons & symbols).[/]",
                "SYSTEM",
                icon="i",
            )

        self.log_status(Translations.t("status_welcome"), "WELCOME", icon=IconManager.get("rocket"))
        self.update_chords()

        # Populate jam scale list
        jam_list = self.query_one("#jam-scale-list", ListView)
        for k, v in self.theory.AVAILABLE_SCALES.items():
            item = ListItem(Label(f" {v['name']} "), id=f"jam-scale-{k}")
            jam_list.append(item)

        # Populate moods
        mood_list = self.query_one("#jam-mood-list", ListView)
        moods = [
            "Happy",
            "Sad",
            "Dark",
            "Epic",
            "Jazz",
            "Mystery",
            "Bright",
            "Melancholy",
            "Tense",
            "No Presets",
        ]
        for m in moods:
            item = ListItem(Label(f" {m} "))
            item.mood_key = f"mood-{m.lower().replace(' ', '-')}"
            mood_list.append(item)

        self.rebuild_jam_scales()
        self.update_jam_view()

    def rebuild_jam_scales(self, filter_keys: List[str] = None) -> None:
        jam_list = self.query_one("#jam-scale-list", ListView)
        jam_list.clear()

        for k, v in self.theory.AVAILABLE_SCALES.items():
            if filter_keys is None or k in filter_keys:
                item = ListItem(Label(f" {v['name']} "))
                item.scale_key = k
                jam_list.append(item)

        if len(jam_list.children) > 0:
            jam_list.index = 0

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id in ["jam-tonic-select", "jam-scale-list"]:
            self.update_jam_view()
        else:
            self.update_chords()

    def on_radio_set_changed(self) -> None:
        self.update_chords()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-export":
            self.action_export_midi()

    def action_toggle_view(self) -> None:
        """Cycles through visualizer views: Both -> Piano -> Guitar -> Both."""
        piano = self.query_one("#piano", PianoWidget)
        guitar = self.query_one("#fretboard", FretboardWidget)

        if piano.display and guitar.display:
            piano.display = True
            guitar.display = False
            self.log_status(Translations.t("view_piano"), "VIEW", icon=IconManager.get("view"))
        elif piano.display and not guitar.display:
            piano.display = False
            guitar.display = True
            self.log_status(Translations.t("view_guitar"), "VIEW", icon=IconManager.get("view"))
        else:
            piano.display = True
            guitar.display = True
            self.log_status(Translations.t("view_split"), "VIEW", icon=IconManager.get("view"))

    def action_toggle_mode(self) -> None:
        """Switches between Compose and Jam modes."""
        switcher = self.query_one(ContentSwitcher)
        if switcher.current == "compose-view":
            switcher.current = "jam-view"
            self.log_status(Translations.t("mode_jam"), "MODE", icon=IconManager.get("jam"))
            self.update_jam_view()
        else:
            switcher.current = "compose-view"
            self.log_status(Translations.t("mode_compose"), "MODE", icon=IconManager.get("jam"))

    def action_toggle_submode(self) -> None:
        """Toggles between simple (dots) and advanced (labels) fretboard view in Jam Mode."""
        jam_fret = self.query_one("#jam-fretboard", FretboardWidget)
        if jam_fret.display_mode == "simple":
            jam_fret.display_mode = "advanced"
            self.log_status(Translations.t("submode_advanced"), "JAM", icon=IconManager.get("gear"))
        else:
            jam_fret.display_mode = "simple"
            self.log_status(Translations.t("submode_simple"), "JAM", icon=IconManager.get("gear"))

    def action_toggle_mouse(self) -> None:
        """Toggles mouse support."""
        self.mouse_enabled = not self.mouse_enabled
        self.disable_mouse = not self.mouse_enabled
        self.save_config()
        status = "ENABLED" if self.mouse_enabled else "DISABLED"
        self.log_status(f"Mouse Support: {status}", "SYSTEM", icon=IconManager.get("gear"))
        self.notify(f"Mouse Support {status}")

    def action_theme_palette(self) -> None:
        """Opens the custom theme palette with live preview."""
        self.push_screen("theme-palette")

    def action_cycle_themes(self) -> None:
        """Cycles through professional musical themes."""
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.pro_themes)
        new_theme = self.pro_themes[self.current_theme_idx]
        self.theme = new_theme
        self.active_theme_name = new_theme
        self.save_config()
        self.log_status(
            f"Theme: {new_theme.replace('-', ' ').title()}", "SYSTEM", icon=IconManager.get("view")
        )
        self.notify(f"Theme: {new_theme.upper()}")

    def save_config(self):
        """Saves current settings to global config.json."""
        self.settings["theme"] = self.active_theme_name
        self.settings["mouse_enabled"] = self.mouse_enabled
        self.config_mgr.save(self.settings)
        self.update_jam_view()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "jam-scale-list":
            self.update_jam_view()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if not event.item:
            return

        if event.list_view.id == "jam-scale-list":
            # Remove dimmed style and update
            self.query_one("#jam-scale-list").remove_class("dimmed-list")
            self.update_jam_view()
        elif event.list_view.id == "jam-mood-list":
            # Dim the scale list to show focus is on moods
            self.query_one("#jam-scale-list").add_class("dimmed-list")
            mood_key = getattr(event.item, "mood_key", "")
            self.apply_mood_preset(mood_key)

    def apply_mood_preset(self, mood_id: str) -> None:
        """Applies expert mood filtering."""
        # Refined Expert Mood Map based on scales.json keys:
        # 1:Major, 2:Minor, 3:Harmonic, 4:Melodic, 5:Dorian, 6:Phrygian, 7:Lydian, 8:Mixolydian, 9:Locrian, 10:MajPent, 11:MinPent
        mood_map = {
            "mood-happy": ["1", "7", "10"],  # Major, Lydian, Maj Pent
            "mood-sad": ["2", "5", "11"],  # Natural Minor, Dorian, Min Pent
            "mood-dark": ["3", "6", "9"],  # Harmonic Minor, Phrygian, Locrian
            "mood-epic": ["1", "8", "5"],  # Major, Mixolydian, Dorian
            "mood-jazz": ["4", "5", "8"],  # Melodic Minor, Dorian, Mixolydian
            "mood-mystery": ["7", "4"],  # Lydian, Melodic Minor
            "mood-bright": ["1", "7"],  # Major, Lydian
            "mood-melancholy": ["2", "5", "11"],  # Minor, Dorian
            "mood-tense": ["9", "6", "3"],  # Locrian, Phrygian, Harmonic Minor
            "mood-no-presets": None,
        }
        filter_keys = mood_map.get(mood_id)
        self.rebuild_jam_scales(filter_keys)
        self.update_jam_view()

    def on_data_table_row_selected(self) -> None:
        self.action_add_to_progression()

    def action_quit(self) -> None:
        """Custom quit logic with double-press confirmation."""
        import time

        now = time.time()
        if now - self.exit_requested_at < 2.0:
            self.exit()
        else:
            self.exit_requested_at = now
            self.log_status(
                "[bold yellow]Press [Q] again to exit station.[/bold yellow]",
                "QUIT",
                icon=IconManager.get("warn"),
            )
            self.notify("Press Q again to quit", severity="warning")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        degree = event.row_key.value
        if degree in self.current_midi:
            midi_notes = self.current_midi[degree]
            name = self.current_chords[degree]
            self.query_one("#piano", PianoWidget).update_notes(midi_notes)
            self.query_one("#fretboard", FretboardWidget).update_view(
                self.scale_notes_pc, midi_notes, self.tonic_pc
            )
            tabs = self.tab_gen.generate_simple_tab(name, midi_notes)
            self.query_one("#guitar-tab", GuitarTabWidget).update_tab(name, tabs)
            self.selected_row_data = {
                "degree": degree,
                "name": name,
                "midi_notes": midi_notes,
                "duration_beats": 4.0,
            }

    def action_add_to_progression(self) -> None:
        if self.selected_row_data:
            self.query_one("#progression-sidebar", ProgressionPanel).add_chord(
                self.selected_row_data
            )
            self.log_status(
                Translations.t("status_chord_added", name=self.selected_row_data["name"]),
                "COMPOSER",
                icon=IconManager.get("plus"),
            )

    def action_clear_progression(self) -> None:
        self.query_one("#progression-sidebar", ProgressionPanel).clear_prog()
        self.log_status(
            Translations.t("status_list_reset"), "COMPOSER", icon=IconManager.get("broom")
        )

    def action_export_midi(self) -> None:
        prog_panel = self.query_one("#progression-sidebar", ProgressionPanel)
        prog_data = prog_panel.get_progression_data()
        if not prog_data:
            prog_data = [
                {"degree": d, "name": n, "midi_notes": self.current_midi[d], "duration_beats": 4.0}
                for d, n in self.current_chords.items()
            ]

        home = os.path.expanduser("~")
        export_dir = os.path.join(home, "chord_generator_midi_exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        # Add timestamp to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(export_dir, f"comp_{len(prog_data)}_chds_{timestamp}.mid")

        midi_opts = {
            "bpm": 120,
            "base_velocity": 85,
            "velocity_randomization_range": 5,
            "chord_instrument": 0,
            "add_bass_track": True,
            "bass_instrument": 33,
            "arpeggio_style": None,
            "voice_leading": True,
        }

        try:
            self.midi_gen.generate_midi_file(prog_data, filename, midi_opts)

            filename_clean = escape(os.path.basename(filename))
            export_dir_clean = escape(export_dir)
            self.log_status(
                Translations.t("status_exported", filename=filename_clean, path=export_dir_clean),
                "MIDI EXPORT",
                icon=IconManager.get("midi"),
            )
            self.notify(Translations.t("notify_exported"))
        except Exception as e:
            logging.error(f"MIDI export failed: {e}\n{traceback.format_exc()}")
            self.log_status(
                Translations.t("status_export_failed", error=str(e)),
                "MIDI ERROR",
                icon=IconManager.get("error"),
            )
            self.notify(Translations.t("notify_export_failed"), severity="error")

    def update_chords(self) -> None:
        t_sel = self.query_one("#tonic-select", Select)
        s_sel = self.query_one("#scale-select", Select)
        if t_sel.value is Select.BLANK or s_sel.value is Select.BLANK:
            return

        ext = self.query_one("#extension-set", RadioSet).pressed_index
        inv = self.query_one("#inversion-set", RadioSet).pressed_index
        scale_info = self.theory.AVAILABLE_SCALES[s_sel.value]

        try:
            res = self.chord_gen.generate_scale_chords(t_sel.value, scale_info, ext, inv)
            self.current_chords, _, self.current_midi, _ = res

            tonic_idx = self.theory.note_to_midi(t_sel.value)
            self.scale_notes_pc = {
                (tonic_idx + d["root_interval"]) % 12 for d in scale_info["degrees"].values()
            }
            self.tonic_pc = tonic_idx % 12

            table = self.query_one("#chord-table", DataTable)
            table.clear()
            for deg, name in self.current_chords.items():
                table.add_row(deg, name, str(self.current_midi[deg]), key=deg)
            self.log_status(
                Translations.t(
                    "status_scale_loaded", tonic=t_sel.value, scale_name=scale_info["name"]
                ),
                "THEORY",
                icon=IconManager.get("book"),
            )
        except Exception as e:
            error_msg = f"Error: {e}"
            logging.error(f"Chord update failed: {e}\n{traceback.format_exc()}")
            self.log_status(
                f"[red]{error_msg}[/red]", "THEORY ERROR", icon=IconManager.get("error")
            )

    def update_jam_view(self) -> None:
        """Updates the fretboard in Jam Mode based on selected scale/tonic."""
        try:
            # Safety check: only update if jam view is active
            switcher = self.query_one(ContentSwitcher)
            if switcher.current != "jam-view":
                return

            t_sel = self.query_one("#jam-tonic-select", Select)
            l_view = self.query_one("#jam-scale-list", ListView)

            if t_sel.value is Select.BLANK:
                return

            highlighted = l_view.highlighted_child
            if highlighted is None:
                return

            scale_key = getattr(highlighted, "scale_key", "1")
            scale_info = self.theory.AVAILABLE_SCALES.get(
                scale_key, self.theory.AVAILABLE_SCALES["1"]
            )

            tonic_idx = self.theory.note_to_midi(t_sel.value)
            scale_notes_pc = {
                (tonic_idx + d["root_interval"]) % 12 for d in scale_info["degrees"].values()
            }

            fretboard = self.query_one("#jam-fretboard", FretboardWidget)
            fretboard.update_view(scale_notes_pc, [], tonic_idx % 12, fretboard.display_mode)

            # Log status only if something changed significantly (optional, but keep persistent)
            # self.log_status(...) removed from here to avoid flood, but ensured no clear()
        except Exception as e:
            logging.error(f"Jam update failed: {e}")


if __name__ == "__main__":
    ChorderizerApp().run()
