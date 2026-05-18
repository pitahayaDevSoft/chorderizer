# Gemini CLI Rules

Specific instructions for the **Gemini CLI** agent in the Chorderizer repository.

## Working Context
- Project follows the Jules Dev Standard.
- Core language: Python 3.8+.
- UI framework: Textual.
- Music logic strictly decoupled from UI.

## Workflow
1. Research -> 2. Strategy -> 3. Execution (Plan-Act-Validate).
2. Validate logic using `pytest`.
3. Validate format using `ruff check` and `ruff format`.

## Constraints
- Never commit without running the test suite and Ruff.
- Maintain accurate musical terminology in code and docs.
- Update `docs/MEMORY.md` after significant logic or UI changes.
- Refer to `docs/AGENT.md` for specific operational SOPs.
- Ensure the TUI remains responsive; avoid blocking the main async loop.