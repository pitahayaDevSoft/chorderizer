# Project Memory: Chorderizer

## Status: Active Development
- **Current Goal:** Refine the Textual TUI and expand the core music theory logic.
- **Last Milestone:** Completed initial migration to the Textual framework for a reactive UI.

## Persistent Context
- **Stack:** Python 3.8+, Textual, mido, Ruff, pytest.
- **Core Files:** `src/chorderizer/theory_utils.py` (Theory engine), `src/chorderizer/tui_app.py` (TUI entry point), `src/chorderizer/generators.py` (MIDI engine).

## Active Tasks
- [ ] Expand the chord progression generation algorithms in `theory_utils.py`.
- [ ] Refine the UI layout and widgets in `tui_widgets.py`.
- [ ] Improve test coverage for the new MIDI generation features.

## Technical Debt
- Ensure all technical debt is tracked in `docs/wiki/technical_debt.md`.
- The classic CLI interface (`ui.py` / `chorderizer.py` root flow) may need deprecation or tight integration with the new TUI approach.

## Notes
- *2026-05-18:* Jules Dev Standard v1.0 applied. Root-level documentation and tracker files have been consolidated into `docs/wiki/`.