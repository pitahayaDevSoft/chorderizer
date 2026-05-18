<table border="0">
  <tr>
    <td valign="top">
      <h1>Chorderizer</h1>
      <p><strong>Advanced Chord Orchestration & MIDI Analysis Dashboard</strong><br/>
      <em>Terminal-native harmonic workstation for composers and producers.</em></p>
      <p>
        <a href="https://badge.fury.io/py/chorderizer"><img src="https://badge.fury.io/py/chorderizer.svg" alt="PyPI version"></a>
        <a href="LICENSE.md"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
        <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"></a>
        <a href="https://textual.textualize.io/"><img src="https://img.shields.io/badge/framework-Textual-0094d2.svg" alt="Framework: Textual"></a>
      </p>
    </td>
  </tr>
</table>

---

<p align="center">
  <img src="docs/wiki/assets/demo.gif" alt="Chorderizer Dashboard Overview" width="900" />
</p>

---

## Project Philosophy

The core objective of Chorderizer is to bridge the gap between abstract music theory and digital composition. By providing an interactive, low-latency TUI (Terminal User Interface) dashboard, the tool allows for rapid prototyping of harmonic progressions while maintaining strict adherence to diatonic principles and ergonomic voice leading.

## Supported Scope

Chorderizer is intentionally focused on:

- interactive harmonic exploration for composers and producers
- diatonic and modal chord generation
- MIDI export and quick tablature support
- terminal-first workflows powered by Textual

It does not currently aim to be:

- a full DAW replacement
- a general-purpose notation editor
- a complete guitar voicing engine for every tuning or fingering strategy
- a music theory engine for non-Western systems or arbitrary microtonal scales
- a plugin host or real-time MIDI router

## Core Capabilities

### Harmonic Engine & Theory Support

The underlying music theory engine has been expanded to support 11 distinct scales, covering the fundamental building blocks of Western and contemporary harmony:

- **Diatonic Standards**: Major (Ionian), Natural Minor (Aeolian).
- **Modal Harmony**: Full support for Greek Modes (Dorian, Phrygian, Lydian, Mixolydian, Locrian).
- **Advanced Tonality**: Harmonic Minor, Melodic Minor (Ascending).
- **Pentatonic Structures**: Major and Minor Pentatonic variations.

### Reactive TUI Dashboard

The v0.2.x release introduces a comprehensive dashboard built on the Textual framework, facilitating real-time visualization and interaction:

- **Piano Visualizer**: A 2-octave responsive keyboard rendering active MIDI notes with precision.
- **Guitar Fretboard**: A 12-fret interactive diapasón highlighting scale tonics and specific chord positions.
- **Guitar Tab Generator**: Automated conversion of MIDI chord voicings into playable tablature notation.
- **Diatonic Table**: Real-time calculation of chord names, degrees (Roman Numeral Analysis), and MIDI note arrays based on selected extensions.

### MIDI Export & Humanization

The MIDI engine (powered by mido) is designed to produce sequences that feel organic and professional:

- **Note Extensions**: Support for Triads, 6ths, 7ths, 9ths, 11ths, and 13ths.
- **Inversion Logic**: Precise control over 1st, 2nd, and 3rd inversions.
- **Humanization Engine**: Intelligent velocity randomization and micro-timing adjustments.
- **Automated Basslines**: Optional generation of root-based bass tracks for full harmonic context.

## Installation & Execution

### Prerequisites

- Python 3.8 or higher.
- Recommended: A terminal with support for true color and UTF-8 characters (e.g., Windows Terminal, iTerm2, Alacritty).

### Installation

The easiest way to install Chorderizer is via PyPI:

```bash
pip install chorderizer
```

### Development Setup (Source)

If you wish to contribute or run the latest development version:

```bash
# Clone the repository
git clone https://github.com/TropicalDev/chorderizer.git
cd chorderizer

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows

# Install the package
pip install .
```

For development:

```bash
pip install -e ".[dev]"
```

### Running the Workstation

To launch the interactive dashboard, execute the module directly:

```bash
python -m chorderizer.chorderizer
```

## Dashboard Interface Guide

The TUI is designed for keyboard-driven efficiency:

- **[A] Add Chord**: Commits the currently highlighted chord in the table to the progression list (Right Sidebar).
- **[X] Clear List**: Flushes the internal progression buffer.
- **[E] Export MIDI**: Serializes the current progression list into a standard MIDI file (SMF) in `~/chord_generator_midi_exports`.
- **[H] Manual**: Displays the comprehensive on-screen operation manual.
- **[Q] Terminate**: Safely closes the application.

## Technical Standards & Quality Assurance

The codebase adheres to PEP 8 standards and utilizes modern tooling to ensure stability and maintainability:

- **Linting & Formatting**: Managed via Ruff and Trunk for lightning-fast quality control.
- **Testing Suite**: Comprehensive unit tests managed via `pytest`, ensuring integrity of the theory engine and MIDI generation.
- **Architecture**: Modular design separating theory logic (`theory_utils.py`), MIDI generation (`generators.py`), the classic orchestration flow (`chorderizer.py` + `ui.py`), and the reactive Textual dashboard (`tui_app.py` + `tui_widgets.py`).

## Documentation

For a comprehensive technical breakdown, architectural ADRs, and operational guides, visit our official **[Wiki](docs/wiki/index.md)**.

*   **[Technical Architecture](docs/wiki/ARCHITECTURE.md)**
*   **[User Guide](docs/wiki/USER_GUIDE.md)**
*   **[Developer Guide](docs/wiki/DEVELOPER_GUIDE.md)**
*   **[Agent SOP](docs/AGENT.md)**

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

---

*Created with ❤️ by TropicalDev. Powered by Python, Textual, and Antigravity* 

