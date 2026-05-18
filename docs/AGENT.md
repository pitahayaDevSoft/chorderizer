# Agent SOP: Chorderizer Operations

## Operational Mandates
- **Testing:** All new theory logic or generators MUST be covered by pytest.
- **Linting:** Code must pass `ruff check` and `ruff format` before any commit. Max line length is 100 characters.
- **Modularity:** Do not mix TUI/Textual logic with core music theory logic.

## Core Workflows
1. **Adding a Theory Feature:**
   - Implement the logic in `src/chorderizer/theory_utils.py`.
   - Add unit tests in `tests/`.
   - Update `docs/wiki/API_REFERENCE.md`.
2. **Updating the TUI:**
   - Modify `src/chorderizer/tui_app.py` or `src/chorderizer/tui_widgets.py`.
   - Ensure the Textual layout remains responsive and handles async events correctly.
3. **MIDI Generation:**
   - Implement or modify classes in `src/chorderizer/generators.py`.
   - Verify output by generating sample `.mid` files and inspecting them.

## Documentation SOP
- Update `CHANGELOG.md` for every release or significant feature.
- Record architectural shifts in `docs/wiki/decisions.md`.
- Document technical debt in `docs/wiki/technical_debt.md` instead of scattering TODOs in the code.
- Keep `docs/MEMORY.md` updated with the latest project status.

## Related Docs
- [Project Identity](./IDENTITY.md)
- [Project Soul](./SOUL.md)
- [Wiki Index](./wiki/index.md)