# API Reference

Detailed documentation of Chorderizer's core classes and methods.

## `theory_utils` Module

### `MusicTheoryUtils`

Static utility class for music theory calculations.

- **`get_note_index(note_name: str) -> int`**
  Converts a note name (e.g., "C#", "Db") to its chromatic index (0-11).
- **`get_note_name(note_index: int, use_flats: bool) -> str`**
  Converts an index back to a string representation.
- **`transpose_chords(chords: Dict, original_tonic: str, new_tonic: str) -> Dict`**
  Handles the transposition of a dictionary of chord strings between two keys.

---

## `generators` Module

### `ChordGenerator`

Handles the generation of chord notes for a given scale.

- **`generate_scale_chords(...)`**
  - **Inputs**: `scale_tonic`, `scale_info`, `extension_level`, `inversion`.
  - **Returns**: A tuple containing `(chord_names, note_names, midi_notes, base_qualities)`.
  - **Note**: Results are cached internally to optimize performance during transposition.

### `MidiGenerator`

Controls interaction with the MIDI filesystem and `mido` library.

- **`generate_midi_file(chords_to_process, output_filename, midi_options)`**
  Main entry point for MIDI creation.
- **`_generate_arpeggio_track(...)`**
  Private method to populate a track with arpeggiated sequences.
- **`_generate_block_track(...)`**
  Private method for block chords with optional strum delay.

### `VoiceLeader`

Static utility class for smooth chord transitions.

- **`apply(prev_notes: List[int], curr_notes: List[int]) -> List[int]`**
  Re-voices `curr_notes` to minimize motion from `prev_notes`, anchoring the bass.

---

## `ui` Module

### `UIManager`

Manages terminal user interaction.

- **`select_tonic_and_scale() -> Tuple`**
  Interactive prompt for key selection.
- **`get_advanced_midi_options() -> Dict`**
  Terminal form for BPM, instruments, and effect configuration.
