# Chorderizer User Guide

This guide provides a comprehensive walkthrough of the Chorderizer harmonic dashboard and its core operational cycles.

## 🚀 Quick Start

To launch the primary interactive dashboard, execute the module:

```bash
python -m chorderizer.chorderizer
```

## 1. Harmonic Configuration Cycle

The Chorderizer workflow is divided into four distinct phases, visualized in real-time through the dashboard.

### Phase 1: Scale Definition

Select your **Tonic** (e.g., C, F#) and **Scale Type**. Chorderizer supports 11+ scales, including full Greek Modal support.

* **Dorian, Phrygian, Lydian**: Instantly available from the Scale menu.
* **Visual Feedback**: The dashboard highlights all diatonic notes on the **Piano** and **Guitar** visualizers immediately.

### Phase 2: Chord Voicing

Customize the structure of your diatonic chords:

* **Extensions**: Choose between Triads, 6ths, 7ths, 9ths, 11ths, or 13ths.
* **Inversions**: Rotate the chord structure (Root, 1st, 2nd, or 3rd inversion).

## 2. Interactive Exploration

Use the central dashboard to audit your selection before exporting.

![Navigation Demo](assets/demo.gif)

* **Keyboard Navigation**: Use `Tab` and `Arrow Keys` to move between configuration menus and the chord table.
* **Visual Audit**: Highlighting a row in the **Chord Table** updates:
  * **Piano Board**: Shows the physical fingering of the chord.
  * **Guitar Fretboard**: Displays the specific fret positions.
  * **Guitar Tab**: Generates a quick-read ASCII tablature.

## 3. Progression & Export

Once you have identified the desired harmonies, you can build a composition.

### Building a Progression

1. Navigate to the **Chord Table**.
2. Press **`[A]`** to add the selected chord to the right sidebar (Progression Panel).
3. Repeat to build your sequence.

### MIDI Export

Press **`[E]`** to invoke the MIDI export engine. Chorderizer will:

1. Apply **Humanization** (micro-velocity randomization).
2. Optionally add an automated **Bass Track**.
3. Save the `.mid` file to `~/chord_generator_midi_exports`.

## 4. Advanced: Transposition

After an export, you can instantly shift the entire progression to a new tonic.

* **Maintain Voicings**: The system retains your extension and inversion settings.
* **Parallel Harmony**: Ideal for exploring how a progression feels in different tonal centers.

## 🎸 Jam Mode: Practice & Improvisation

Switch from composition focus to practice focus with a single keystroke.

### Entering Jam Mode

* Press **`[J]`** to toggle between **Compose Mode** and **Jam Mode**.
* In Jam Mode, the interface reorganizes to give the **Guitar Fretboard** full horizontal focus.

### Practice Submodes

Press **`[S]`** to toggle between visual submodes:
* **Simple**: Shows clean dots (●) for all scale notes.
* **Advanced**: Shows **Musical Degrees** (R, 2, b3, 3, etc.) relative to the selected tonic.

### Mood Presets & Expert Filtering

Use the **Moods** panel to quickly set the emotional tone:
* Selecting a mood (e.g., *Jazz, Dark, Epic*) instantly filters the scale list to show matching musical modes.
* Selecting **'No Presets'** restores the full list of available scales.

---
> [!NOTE]
> All MIDI exports are serialized with high-precision timing (ticks per beat) to ensure compatibility with all modern DAWs like Ableton Live, Logic Pro, and FL Studio.
