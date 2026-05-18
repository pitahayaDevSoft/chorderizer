"""
chorderizer.py — Main orchestration for Chorderizer
=====================================================
Coordinates the 4-phase workflow:
  Phase 1  ·  Scale Configuration
  Phase 2  ·  Chord Configuration
  Phase 3  ·  Results Display (table + guitar tabs)
  Phase 4  ·  MIDI Export (progression → options → file)

All user interaction is delegated to UIManager (ui.py).
All music theory is delegated to MusicTheory / MusicTheoryUtils.
All generation logic lives in generators.py.
"""

import argparse
import datetime
import logging
import os
import sys
from typing import Any, Dict, List

from .generators import ChordGenerator, MidiGenerator, TablatureGenerator
from .theory_utils import MusicTheory, MusicTheoryUtils
from .translations import Translations
from .ui import (
    UIManager,
    print_operation_cancelled,
    print_welcome_message,
    prompt_confirm,
    render_chord_table,
    render_error,
    render_guitar_tab,
    render_section,
    render_success,
    render_warn,
)

# ─── TUI Moderno ──────────────────────────────────────────────────────────────


def run_modern_tui():
    """Launch the reactive Textual dashboard."""
    try:
        from .tui_app import ChorderizerApp

        app = ChorderizerApp()
        app.run()
    except ImportError as e:
        render_error(f"Textual or a dependency is missing: {e}")
        render_warn("Falling back to basic CLI mode...")
        return False  # Signal to caller to use legacy mode
    except Exception as e:
        # Do not catch everything silently - show the error
        import traceback

        render_error(f"Failed to launch dashboard: {e}")
        print(traceback.format_exc())
        sys.exit(1)
    return True


# ─── File helpers ─────────────────────────────────────────────────────────────


def _midi_filename(
    tonic: str, scale_info: Dict[str, Any], base_dir: str, prefix: str = "prog_"
) -> str:
    """Build a safe MIDI filename from tonic + scale with timestamp to avoid collisions."""
    safe_tonic = tonic.replace(" ", "_")
    safe_scale = scale_info["name"].replace(" ", "_").replace("(", "").replace(")", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(base_dir, f"{prefix}{safe_tonic}_{safe_scale}_{timestamp}.mid")


# Backward-compat alias used by existing tests
_generate_midi_filename_helper = _midi_filename


def _sanitize_path(path_input: str, default: str, base_dir: str) -> str:
    """
    Safely join user-provided path with base_dir, preventing path traversal.
    Allows subdirectories within base_dir.
    Returns default if path_input is empty.
    """
    if not path_input:
        return default

    # Normalize the base directory path
    base_dir = os.path.abspath(base_dir)

    # Join and resolve the path
    full_path = os.path.abspath(os.path.join(base_dir, path_input))

    # Ensure the resolved path is within base_dir
    if not full_path.startswith(base_dir + os.sep) and full_path != base_dir:
        logging.warning(f"Path traversal detected for '{path_input}', using safe default")
        return default

    return full_path


# Backward-compat alias used by existing tests
_sanitize_midi_path = _sanitize_path


# ─── Chord display helpers ────────────────────────────────────────────────────


def _should_show_tab(filter_key: str, chord_name: str, base_quality: str) -> bool:
    """Return True if a guitar tab should be shown for this chord given the filter."""
    if filter_key == "1":
        return True
    if filter_key == "2" and base_quality == "minor":
        return True
    if filter_key == "3" and "7" in chord_name:
        return True
    if filter_key == "4" and "9" in chord_name:
        return True
    if filter_key == "5" and chord_name.endswith("6") and not chord_name.endswith("m7b6"):
        return True
    if filter_key == "6" and "11" in chord_name:
        return True
    if filter_key == "7" and "13" in chord_name:
        return True
    return False


# ─── Core workflow ────────────────────────────────────────────────────────────


def _phase3_display_results(
    ui: UIManager,
    tab_builder: TablatureGenerator,
    tonic: str,
    scale_info: Dict[str, Any],
    chord_names: Dict[str, str],
    note_names: Dict[str, List[str]],
    midi_notes: Dict[str, List[int]],
    base_qualities: Dict[str, str],
) -> None:
    """Phase 3 — Display chord table and optional guitar tabs."""
    render_section(Translations.t("legacy_phase3"))

    render_chord_table(
        chord_names, note_names, midi_notes, base_qualities, tonic, scale_info["name"]
    )

    tab_filter = ui.prompt_tablature_filter()

    for degree, chord_name in chord_names.items():
        qual = base_qualities.get(degree, "major")
        if _should_show_tab(tab_filter, chord_name, qual):
            midi = midi_notes.get(degree, [])
            if midi:
                tab_lines = tab_builder.generate_simple_tab(chord_name, midi)
                if tab_lines:
                    render_guitar_tab(chord_name, tab_lines)


def _phase4_midi_export(
    ui: UIManager,
    midi_builder: MidiGenerator,
    chord_builder: ChordGenerator,
    tonic: str,
    scale_info: Dict[str, Any],
    chord_names: Dict[str, str],
    midi_notes: Dict[str, List[int]],
    extension_level: int,
    inversion_idx: int,
    export_dir: str,
) -> None:
    """Phase 4 — Build progression, collect MIDI options, and export."""
    render_section(Translations.t("legacy_phase4"))

    # ── 4a: Build chord progression ──────────────────────────────────────────
    chords_for_midi: List[Dict[str, Any]] = []

    if prompt_confirm(Translations.t("legacy_confirm_custom"), default=False):
        raw_prog = ui.prompt_progression(chord_names)
        if raw_prog:
            for item_str in raw_prog.strip().upper().split("-"):
                item_str = item_str.strip()
                if not item_str:
                    continue
                degree, beats = item_str, 4.0
                if ":" in item_str:
                    parts = item_str.split(":", 1)
                    degree = parts[0].strip()
                    try:
                        beats = float(parts[1].strip())
                        if beats <= 0:
                            beats = 4.0
                    except ValueError:
                        render_warn(f"Invalid duration for '{degree}' — using 4.0 beats.")
                if degree in chord_names:
                    chords_for_midi.append(
                        {
                            "degree": degree,
                            "name": chord_names[degree],
                            "midi_notes": midi_notes[degree],
                            "duration_beats": beats,
                        }
                    )
                else:
                    render_warn(f"Degree '{degree}' not found — skipped.")
    else:
        # Use all diatonic chords sequentially
        for deg in scale_info["degrees"]:
            if deg in chord_names:
                chords_for_midi.append(
                    {
                        "degree": deg,
                        "name": chord_names[deg],
                        "midi_notes": midi_notes[deg],
                        "duration_beats": 2.0,
                    }
                )

    if not chords_for_midi:
        render_error("No chords available for MIDI export.")
        return

    # ── 4b: MIDI options ─────────────────────────────────────────────────────
    midi_opts = ui.get_midi_options()

    # ── 4c: Output filename ───────────────────────────────────────────────────
    suggested = _midi_filename(tonic, scale_info, export_dir)

    from .ui import prompt_text  # local import to avoid circular at module level

    raw_fname = prompt_text(
        "Output MIDI filename:",
        default=suggested,
        hint=f"Default: {suggested}",
    )
    out_path = _sanitize_path(raw_fname.strip(), suggested, export_dir)

    # Create output directory if needed
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    midi_builder.generate_midi_file(chords_for_midi, out_path, midi_opts)
    render_success(f"MIDI saved → {out_path}")

    # ── 4d: Optional transposition ────────────────────────────────────────────
    if prompt_confirm(Translations.t("legacy_confirm_trans")):
        render_section("Transposition")
        new_configs = ui.select_scale_config()
        if new_configs != (None, None):
            new_tonic, new_scale = new_configs
            transposed = MusicTheoryUtils.transpose_chords(chord_names, tonic, new_tonic)
            if transposed:
                render_section(f"Transposed to  {new_tonic}  ({new_scale['name']})")
                from .ui import _escape, _pp

                for deg, name in transposed.items():
                    _pp(f"  <key>{_escape(deg.ljust(8))}</key>  <value>{_escape(name)}</value>")
                print()

            if prompt_confirm(Translations.t("legacy_confirm_trans_midi")):
                trans_chord_data, _, trans_midi, _ = chord_builder.generate_scale_chords(
                    new_tonic, new_scale, extension_level, inversion_idx
                )
                if trans_chord_data:
                    trans_list = [
                        {
                            "degree": item["degree"],
                            "name": trans_chord_data[item["degree"]],
                            "midi_notes": trans_midi[item["degree"]],
                            "duration_beats": item["duration_beats"],
                        }
                        for item in chords_for_midi
                        if item["degree"] in trans_chord_data
                    ]
                    if trans_list:
                        sugg_trans = _midi_filename(
                            new_tonic, new_scale, export_dir, prefix="prog_TRANSP_"
                        )
                        trans_path = prompt_text(
                            "Transposed MIDI filename:",
                            default=sugg_trans,
                            hint=f"Default: {sugg_trans}",
                        )
                        trans_out = _sanitize_path(trans_path.strip(), sugg_trans, export_dir)
                        midi_builder.generate_midi_file(trans_list, trans_out, midi_opts)
                        render_success(f"Transposed MIDI saved → {trans_out}")


# ─── Main loop ────────────────────────────────────────────────────────────────


def process_single_run(
    ui: UIManager,
    chord_builder: ChordGenerator,
    tab_builder: TablatureGenerator,
    midi_builder: MidiGenerator,
    export_dir: str,
) -> bool:
    """
    Execute one full generation cycle.
    Returns True to loop again, False to exit.
    """
    # ── Phase 1: Scale ────────────────────────────────────────────────────────
    tonic, scale_info = ui.select_scale_config()
    if tonic is None or scale_info is None:
        return True  # cancelled — loop

    # ── Phase 2: Chord config ─────────────────────────────────────────────────
    chord_cfg = ui.select_chord_config()
    if chord_cfg == (None, None) or None in chord_cfg:
        return True  # cancelled — loop
    extension_level, inversion_idx = chord_cfg

    # ── Generate chords ───────────────────────────────────────────────────────
    chord_names, note_names, midi_notes, base_qualities = chord_builder.generate_scale_chords(
        tonic, scale_info, extension_level, inversion_idx
    )

    if not chord_names:
        render_error(f"Could not generate chords for  {tonic}.")
        return True

    # ── Phase 3: Display results ──────────────────────────────────────────────
    _phase3_display_results(
        ui,
        tab_builder,
        tonic,
        scale_info,
        chord_names,
        note_names,
        midi_notes,
        base_qualities,
    )

    # ── Phase 4: MIDI export ──────────────────────────────────────────────────
    if prompt_confirm(Translations.t("legacy_confirm_midi"), default=True):
        try:
            _phase4_midi_export(
                ui,
                midi_builder,
                chord_builder,
                tonic,
                scale_info,
                chord_names,
                midi_notes,
                extension_level,
                inversion_idx,
                export_dir,
            )
        except KeyboardInterrupt:
            print_operation_cancelled()

    return prompt_confirm(Translations.t("legacy_confirm_new"), default=False)


def main() -> None:
    """Application entry point."""
    parser = argparse.ArgumentParser(description="Chorderizer — Advanced Chord Generator")
    parser.add_argument("--version", action="version", version="Chorderizer 0.3.2")
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Run the sequential prompt-based UI instead of the dashboard",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable detailed logging output"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Run in debug mode with full tracebacks"
    )
    args = parser.parse_args()

    if args.verbose or args.debug:
        logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
        logging.info("Verbose mode enabled.")

    if not args.legacy:
        tui_started = run_modern_tui()
        if not tui_started:
            # Fallback to legacy mode if TUI failed
            render_warn("Starting legacy CLI mode...")
            args.legacy = True

    # Legacy Sequential Flow
    if args.legacy:
        theory = MusicTheory()
        ui = UIManager(theory)
        chord_builder = ChordGenerator(theory)
        tab_builder = TablatureGenerator(theory)
        midi_builder = MidiGenerator(theory)

        print_welcome_message()  # renders the banner

        export_dir = os.path.join(os.path.expanduser("~"), "chord_generator_midi_exports")

        try:
            while True:
                if not process_single_run(ui, chord_builder, tab_builder, midi_builder, export_dir):
                    from .ui import _pp

                    _pp(Translations.t("legacy_goodbye"))
                    break
        except KeyboardInterrupt:
            print_operation_cancelled()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_operation_cancelled()
        sys.exit(130)
    except Exception:
        logging.error("Unexpected error", exc_info=True)
        render_error("An unexpected error occurred. Check logs for details.")
        sys.exit(1)
