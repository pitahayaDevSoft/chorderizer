# User Guide

A step-by-step guide to mastering Chorderizer.

## 1. Quick Start

Run the application using:

```bash
chorderizer
```

Or from source:

```bash
python -m chorderizer.chorderizer
```

## 2. Theoretical Workflow

Chorderizer follows a logical music theory path:

### Step 1: Define Your Key

Select a **Tonic** (e.g., C, F#) and a **Scale Type** (e.g., Major, Harmonic Minor). This creates the harmonic foundation for all subsequent steps.

### Step 2: Configure Chord Voicing

Choose the **Extension Level** and **Inversion**:

- **Triads to 13ths**: Control the complexity and "flavor" of each degree.
- **Inversions**: Move the bass to the 3rd, 5th, or 7th to change the chord's texture and bass motion.

### Step 3: Explore & Filter

View the generated chords, note names, and MIDI values. Use the **Tablature Filter** to display guitar fingerings for specific chord types.

## 3. Creating MIDI Files

### Defining Progressions

You can export all diatonic chords sequentially or define a custom progression using Roman numerals:

- `I-V-vi-IV` (Classic Pop progression)
- `ii:2-V:2-I:4` (Jazz II-V-I with custom durations)

### MIDI Customization

- **BPM & Velocity**: Set the tempo and base dynamics.
- **Humanization**: Add randomization to the velocity to avoid a "robotic" sound.
- **Dual Tracks**: Add an automatic bassline instrument along with your chords.
- **Performance Effects**:
  - **Arpeggio**: Spread the notes across time (up, down, or up-down).
  - **Strum**: Add a millisecond delay between notes in a single block chord.

## 4. Advanced: Transposition

After generating a MIDI file, you can transpose your entire progression to a new key. The system will keep all your voicing and timing settings but move the notes to the target key.

---
> [!TIP]
> Use the "Humanization" feature with a range of +/- 5 for a subtle, professional feel.