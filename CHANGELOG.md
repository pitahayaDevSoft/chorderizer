# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2026-05-22

### Added
- **Advanced Voice Leading Rules**: Enhanced the `VoiceLeader` algorithm to evaluate and support music theory rules.
  - **Common Tone Retention**: Grants a harmonic advantage (cost reduction) to voices that maintain the exact same MIDI pitch in transitions.
  - **Parallel Interval Avoidance**: Imposed heavy cost penalties on transitions that produce parallel perfect fifths, perfect fourths, or perfect octaves in relation to other parts.
- **Robust Unit Testing**: Added unit tests `test_voice_leader_common_tone_retention` and `test_voice_leader_avoids_parallel_fifths` to guarantee harmonic rule adherence.

### Fixed
- **Python 3.15 Deprecation Warning**: Replaced the deprecated `locale.getdefaultlocale()` with a robust Windows-compatible `locale.getlocale()` normalization routine in `translations.py`.

## [0.3.2] - 2026-05-17

### Added
- **Automated Publishing Pipeline**: Integrated GitHub Actions workflow (`python-publish.yml`) for automated package distribution to PyPI via Trusted Publishing.
- **Technical Wiki**: Initialized and consolidated a comprehensive project-wide documentation wiki located under `docs/wiki`.
- **Developer Guidelines**: Created developer guides, setup instructions, and workflows to streamline codebase onboarding.

### Changed
- **Project Metadata**: Updated project URLs and references in `pyproject.toml` to track `TropicalDevApps`.

## [0.3.1] - 2026-05-04

### Added

- **Persistent Configuration**: New `config.json` system to save user preferences (theme, mouse support, etc.) globally.
- **Theory-Driven Themes**: Custom palettes ('Chromatic-Pro', 'Harmonic-Gold', 'Dorian-Deep') mapped to musical concepts.
- **Theme Palette**: New modal selector with 'Live Preview' to test aesthetics on the fly before selecting.
- **Advanced UX**: Toggle for mouse support and improved keyboard-only navigation for server/legacy environments.

### Fixed

- **Command Palette Stability**: Fully migrated to the latest Textual Provider API, resolving framework compatibility issues.
- **Performance**: Optimized Fretboard rendering and eliminated redundant theory lookups in hot paths.
- **Error Transparency**: Disabled silent legacy fallback to provide clear tracebacks for easier debugging.

## [0.3.0] - 2026-05-04

### Added

- UX tooltips to interactive dashboard elements.
- Empty state message to progression list when empty.
- **.editorconfig**: Standardized editor settings for consistency across environments.
- **CONTRIBUTING.md**: Guidelines for community contributions.

### Fixed

- Stack trace leakage vulnerability during TUI initialization gracefully handled with logs.

### Professional Cleanup

- Sanitized `.gitignore` to preserve essential `.github`, `.editorconfig`, and `.specsmd` files.
- Removed legacy clutter: `test_file.txt`, `prs.json`, and unused `safe_midi_exports/` directory.
- Organized documentation: moved security and quality audits to `Docs/audits/`.
- Standardized codebase formatting using `ruff format`.
- Relaxed `dev` dependencies in `pyproject.toml` to support modern Python environments.

## [0.2.7] - 2026-05-03

### Added

- **AGENTS.md**: Compact instruction file for AI agents with repo-specific guidance
- **File logging**: TUI exceptions now logged to `~/chorderizer.log` with full tracebacks
- **Timestamped MIDI filenames**: Prevent collisions with `YYYYMMDD_HHMMSS` format

### Changed

- **Textual fallback**: Failed TUI import now falls back to legacy CLI mode instead of exiting
- **Path sanitization**: `_sanitize_path()` allows subdirectories within base_dir while blocking traversal
- **Logging config**: Moved from class definition time to `__init__()` with `force=True`

### Fixed

- **Import placement**: Moved `datetime` import from function scope to module-level
- **Side effects**: Removed directory creation from `_sanitize_path()`, added to caller
- **Code review**: Applied fixes from automated review (logging timing, structure, tests)

### Closed

- **PR #67**: Dependency update (textual) - no longer needed
- **PR #68**: Palette empty state - no longer needed

## [0.2.5] - 2026-04-17

### Added

- Created professional goodbye message on TUI exit.

### Changed

- **Trunk Standardization**: Moved `trunk.yaml` to the root directory for standard compliance.
- **Repository Sanitization**: Simplified `.gitignore` by grouping `.trunk/` internal files and removing redundant rules.
- **Documentation**: Finalized **Project Wiki** integration and cross-linked all technical documents.

## [0.2.4] - 2026-04-16

<!-- trunk-ignore(markdownlint/MD024) -->
### Changed

- **Global Search & Replace**: Exhaustive standardization of all internal logic keys and UI strings to English (e.g., `grado` -> `degree`, `nombre` -> `name`).
- **User Guide**: Rewrote documentation to include VHS-generated `demo.gif` and detailed 4-phase workflow.
- **WIKI**: Initialized the project-wide documentation wiki index.

## [0.2.3] - 2026-04-16

### Fixed

- **Dependency Stabilization**: Pinned `textual`, `rich`, and `pytest` to stable major version ranges to prevent breaking API changes from automated updates.
- **CI/CD Reliability**: Resolved build failures in GitHub Actions caused by major version jumps in core dependencies.

## [0.2.2] - 2026-04-16

<!-- trunk-ignore(markdownlint/MD024) -->
### Added

- **Premium TUI Dashboard**: Integrated a reactive dashboard using the Textual framework.
- **Visualizers**: 2-octave Piano board and 12-fret Guitar Fretboard widgets with real-time updates.
- **Guitar Tab Engine**: Automatic ASCII tablature generation for any chord voicing.
- **Transparency Support**: Configured TUI CSS to allow terminal-inherited background colors.

### Changed

- **Performance**: Optimized rendering of block characters for better recording compatibility (`vhs`).

## [0.2.0] - 2026-04-10

### Added

- **Core Harmonic Engine**: Support for 11+ scales including Greek Modes and Pentatonic variations.
- **MIDI Serialization**: Professional MIDI file generation with humanization, arpeggio styles, and automated bass tracks.

## [1.2.0] - 2026-03-29

_(Legacy Branch)_

### Added

- Unit tests for theory logic and MIDI range validation [0, 127].
- `colorama` integration for Windows terminal support.

<!-- trunk-ignore(markdownlint/MD024) -->
### Changed

- Migrated build system to `pyproject.toml` (PEP 621).

## [1.0.1] - 2025-03-01

- **Initial Release**: Basic scale generation and MIDI export.
