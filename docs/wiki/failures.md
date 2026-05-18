# Failures

This file records failures, broken assumptions, and important corrections that should remain visible.

## 2026-04-17 | Documentation drift around the modern dashboard

- Failure:
  The repository documentation described the classic orchestration path but did not fully reflect the active Textual dashboard modules.
- Impact:
  A reader could understand the codebase incorrectly and underestimate the real UI surface area.
- Correction:
  Updated `Docs/ARCHITECTURE.md` and `README.md` to represent the current runtime shape.
- Lesson:
  In a dual-interface repository, architecture docs must be updated whenever either interaction path changes materially.
