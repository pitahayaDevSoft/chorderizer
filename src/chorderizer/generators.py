import copy
import logging
import os
import random
from typing import Any, Dict, List, Optional, Tuple

from colorama import Fore, Style
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

from .theory_utils import MusicTheory, MusicTheoryUtils


# -----------------------------------------------------------------------------
# Class ChordGenerator
# -----------------------------------------------------------------------------
class ChordGenerator:
    def __init__(self, theory: MusicTheory):
        self.theory = theory

    def generate_scale_chords(
        self,
        scale_tonic_str: str,
        scale_info: Dict[str, Any],
        extension_level: int = 2,
        inversion: int = 0,
    ) -> Tuple[Dict[str, str], Dict[str, List[str]], Dict[str, List[int]], Dict[str, str]]:
        # Initialize cache if it doesn't exist
        if not hasattr(self, "_chord_cache"):
            self._chord_cache = {}

        # Create a cache key using scale_info's name (dicts aren't hashable)
        scale_name = scale_info.get("name", "")
        cache_key = (scale_tonic_str, scale_name, extension_level, inversion)

        # Return cached result if available
        if cache_key in self._chord_cache:
            return copy.deepcopy(self._chord_cache[cache_key])

        generated_chords: Dict[str, str] = {}
        notes_per_chord_names: Dict[str, List[str]] = {}
        notes_per_chord_midi: Dict[str, List[int]] = {}
        generated_base_qualities: Dict[str, str] = {}

        try:
            scale_tonic_index = MusicTheoryUtils.get_note_index(scale_tonic_str)
        except ValueError as e:
            logging.error(f"Invalid scale tonic '{scale_tonic_str}': {e}")
            print(
                f"{Fore.RED}Error: Invalid scale tonic '{scale_tonic_str}'. Please provide a valid tonic.{Style.RESET_ALL}"
            )
            return {}, {}, {}, {}

        scale_degrees_info = scale_info["degrees"]
        use_flats = MusicTheoryUtils.should_use_flats(scale_tonic_str)

        for degree_roman, degree_definition in scale_degrees_info.items():
            chord_root_abs_idx = (scale_tonic_index + degree_definition["root_interval"]) % 12
            chord_root_name = MusicTheoryUtils.get_note_name(chord_root_abs_idx, use_flats)
            base_quality = degree_definition["base_quality"]
            degree_display_suffix = degree_definition["display_suffix"]
            chord_type_to_use = degree_definition[
                "full_quality"
            ]  # Default to full quality (e.g., 7ths)

            chord_type_to_use, degree_display_suffix = self._determine_chord_type_and_suffix(
                base_quality,
                chord_type_to_use,
                degree_display_suffix,
                extension_level,
            )

            # Get intervals for the determined chord type
            chord_intervals_relative = list(
                self.theory.CHORD_STRUCTURES.get(
                    chord_type_to_use,
                    self.theory.CHORD_STRUCTURES.get(base_quality, []),
                )
            )
            if not chord_intervals_relative:  # Fallback if type is unknown
                print(
                    f"{Fore.YELLOW}Warning: Chord structure for '{chord_type_to_use}' or '{base_quality}' not found. Skipping chord for degree {degree_roman}.{Style.RESET_ALL}"
                )
                continue

            final_chord_display_name = chord_root_name + degree_display_suffix

            # Apply inversion
            chord_intervals_relative = self._apply_inversion(
                list(chord_intervals_relative), inversion
            )

            # Generate MIDI notes for the chord
            current_midi_notes: List[int] = []
            unique_sorted_intervals = sorted(set(chord_intervals_relative))

            initial_octave_offset = self._determine_initial_octave_offset(
                unique_sorted_intervals, chord_root_abs_idx
            )

            current_midi_notes = self._generate_midi_notes_for_chord(
                unique_sorted_intervals, chord_root_abs_idx, initial_octave_offset
            )

            current_midi_notes = sorted(set(current_midi_notes))  # Final sort and unique
            current_chord_note_names = [
                MusicTheoryUtils.get_note_name(n, use_flats) for n in current_midi_notes
            ]

            generated_chords[degree_roman] = final_chord_display_name
            notes_per_chord_names[degree_roman] = current_chord_note_names
            notes_per_chord_midi[degree_roman] = current_midi_notes
            generated_base_qualities[degree_roman] = base_quality

        result = (
            generated_chords,
            notes_per_chord_names,
            notes_per_chord_midi,
            generated_base_qualities,
        )
        self._chord_cache[cache_key] = result
        # Return a deep copy to prevent callers from mutating the shared cache
        return copy.deepcopy(result)

    def _determine_chord_type_and_suffix(
        self,
        base_quality: str,
        chord_type_to_use: str,
        degree_display_suffix: str,
        extension_level: int,
    ) -> Tuple[str, str]:
        if extension_level == 0:  # Triads
            triad_map = {
                "major": "major",
                "minor": "minor",
                "diminished": "diminished",
                "augmented": "augmented",
            }
            chord_type_to_use = triad_map.get(base_quality, base_quality)
            degree_display_suffix = {
                "major": "",
                "minor": "m",
                "diminished": "dim",
                "augmented": "aug",
            }.get(base_quality, "")
        elif extension_level == 1:  # Sixths (or default 7ths if 6th doesn't fit well)
            if chord_type_to_use == "maj7":  # Typically Major scale I, IV
                chord_type_to_use = "major6"
                degree_display_suffix = "6"
            elif chord_type_to_use == "min7":  # Typically Major scale ii, iii, vi
                chord_type_to_use = "minor6"
                degree_display_suffix = "m6"
            # For other cases (e.g., V7, vii°), keep their 7th quality or base triad if 6th is odd
        elif extension_level >= 3:  # Ninths, Elevenths, Thirteenths
            extension_map_dict = {
                "dom7": {3: "dom9", 4: "dom11", 5: "dom13"},
                "maj7": {3: "maj9", 4: "maj11", 5: "maj13"},
                "min7": {3: "min9", 4: "min11", 5: "min13"},
                "halfdim7": {3: "halfdim9"},
                "minMaj7": {3: "minMaj9"},
                "dim7": {3: "dimM9"},
            }
            suffix_map_dict = {
                "dom9": "9",
                "dom11": "11",
                "dom13": "13",
                "maj9": "maj9",
                "maj11": "maj11",
                "maj13": "maj13",
                "min9": "m9",
                "min11": "m11",
                "min13": "m13",
                "halfdim9": "m9b5",
                "minMaj9": "m(maj9)",
                "dimM9": "dim(maj9)",
            }
            if (
                chord_type_to_use in extension_map_dict
                and extension_level in extension_map_dict[chord_type_to_use]
            ):
                new_type = extension_map_dict[chord_type_to_use][extension_level]
                if new_type in self.theory.CHORD_STRUCTURES:
                    chord_type_to_use = new_type
                    degree_display_suffix = suffix_map_dict.get(
                        chord_type_to_use, degree_display_suffix
                    )
        return chord_type_to_use, degree_display_suffix

    def _generate_midi_notes_for_chord(
        self,
        unique_sorted_intervals: List[int],
        chord_root_abs_idx: int,
        initial_octave_offset: int,
    ) -> List[int]:
        current_midi_notes: List[int] = []
        last_added_midi_note = -1

        for rel_interval in unique_sorted_intervals:
            interval_octave_offset = (
                rel_interval // 12
            ) * 12  # Octave from interval itself (e.g., M9 is R + 14 semitones)
            candidate_midi_note = (
                self.theory.MIDI_BASE_OCTAVE
                + initial_octave_offset
                + ((chord_root_abs_idx + rel_interval) % 12)
                + interval_octave_offset
            )

            # Ensure notes are generally ascending for a simple voicing
            while last_added_midi_note != -1 and candidate_midi_note <= last_added_midi_note:
                candidate_midi_note += 12

            # MIDI range adjustments (heuristic to keep notes within a playable/sensible range)
            if candidate_midi_note > 108:
                candidate_midi_note -= 12  # Too high, try octave lower
            if candidate_midi_note < 21:
                candidate_midi_note += 12  # Too low, try octave higher

            # For wider chords, try to keep upper notes from going excessively high if a lower octave is available
            if (
                len(unique_sorted_intervals) > 4
                and candidate_midi_note > self.theory.MIDI_BASE_OCTAVE + 24 + initial_octave_offset
            ):  # Roughly 2 octaves above C4
                if (candidate_midi_note - 12) > last_added_midi_note or last_added_midi_note == -1:
                    candidate_midi_note -= 12

            if 0 <= candidate_midi_note <= 127:  # Valid MIDI note
                current_midi_notes.append(candidate_midi_note)
                last_added_midi_note = candidate_midi_note

        return current_midi_notes

    def _determine_initial_octave_offset(
        self, unique_sorted_intervals: List[int], chord_root_abs_idx: int
    ) -> int:
        initial_octave_offset = 0
        if unique_sorted_intervals:
            # Estimate position of the first note if placed directly
            first_note_in_octave_relative = (chord_root_abs_idx + unique_sorted_intervals[0]) % 12
            tentative_first_midi_note = self.theory.MIDI_BASE_OCTAVE + first_note_in_octave_relative

            # If the first note is too low and it's a root/low interval, shift up
            if (
                tentative_first_midi_note < self.theory.MIDI_BASE_OCTAVE - 6
                and unique_sorted_intervals[0] >= 0
            ):
                initial_octave_offset = 12
            # If the first note is too high for a root/low interval, shift down (less common for root)
            elif (
                tentative_first_midi_note > self.theory.MIDI_BASE_OCTAVE + 6
                and unique_sorted_intervals[0] <= 7
            ):  # Heuristic
                initial_octave_offset = -12
        return initial_octave_offset

    def _apply_inversion(self, chord_intervals_relative: List[int], inversion: int) -> List[int]:
        if not (0 < inversion < len(chord_intervals_relative)):
            return chord_intervals_relative

        temp_intervals = list(chord_intervals_relative)  # Make a mutable copy
        for _ in range(inversion):
            if not temp_intervals:
                break
            bass_relative_interval = temp_intervals.pop(0)
            temp_intervals.append(bass_relative_interval + 12)  # Add to top, an octave higher
        return sorted(set(temp_intervals))  # Remove duplicates and sort


# -----------------------------------------------------------------------------
# Class TablatureGenerator
# -----------------------------------------------------------------------------
class TablatureGenerator:
    def __init__(self, theory: MusicTheory):
        self.theory = theory
        # Standard guitar tuning, MIDI notes
        self.GUITAR_OPEN_STRINGS_MIDI: Dict[str, int] = {
            "e1": 64,
            "B2": 59,
            "G3": 55,
            "D4": 50,
            "A5": 45,
            "E6": 40,
        }
        self.TAB_STRING_NAMES: List[str] = [
            "e1",
            "B2",
            "G3",
            "D4",
            "A5",
            "E6",
        ]  # High e to Low E

    def _assign_fret_to_string(
        self, chord_note_midi: int, open_string_midi: int, max_frets: int
    ) -> Optional[int]:
        """Helper to find fret for a note on a string."""
        if chord_note_midi >= open_string_midi:
            fret = chord_note_midi - open_string_midi
            if 0 <= fret <= max_frets:
                return fret
        return None

    def generate_simple_tab(
        self, chord_display_name: str, chord_midi_notes: List[int]
    ) -> List[str]:
        if not chord_midi_notes:
            return []
        # This is a very basic tablature generator, prioritizing lower frets and one note per string.
        frets_on_strings = dict.fromkeys(self.TAB_STRING_NAMES, "-")
        sorted_midi_notes = sorted(set(chord_midi_notes))  # Ascending MIDI notes
        notes_placed_in_tab = [False] * len(sorted_midi_notes)
        max_allowable_frets = 15  # Arbitrary limit for simplicity

        # Iterate from highest string (e1) to lowest (E6) to try and place notes
        for string_name in reversed(self.TAB_STRING_NAMES):  # e.g. E6, A5, D4, G3, B2, e1
            open_string_note_midi = self.GUITAR_OPEN_STRINGS_MIDI[string_name]
            # Try to place an unplaced chord note on this string
            for i, chord_note in enumerate(sorted_midi_notes):
                if notes_placed_in_tab[i]:
                    continue  # This note is already placed

                fret = self._assign_fret_to_string(
                    chord_note, open_string_note_midi, max_allowable_frets
                )
                if (
                    fret is not None and frets_on_strings[string_name] == "-"
                ):  # If string is available
                    frets_on_strings[string_name] = str(fret)
                    notes_placed_in_tab[i] = True
                    break  # Move to the next string once a note is placed on this one

        tab_lines: List[str] = [f"Chord: {chord_display_name} (simple tab)"]
        for string_name in self.TAB_STRING_NAMES:  # Display from e1 (high) to E6 (low)
            fret_display = frets_on_strings[string_name]
            tab_lines.append(f"{string_name.ljust(2)}|--{fret_display.rjust(2, '-')}--|")
        return tab_lines


# -----------------------------------------------------------------------------
# Class VoiceLeader
# -----------------------------------------------------------------------------
class VoiceLeader:
    """
    Implements a greedy Minimum Motion voice leading algorithm.

    For each note in the target chord, it finds the octave transposition that
    minimizes the total semitone movement from the previous chord. The bass
    note (index 0, lowest note) is anchored to preserve harmonic identity.

    MIDI range is clamped to [MIDI_MIN, MIDI_MAX] (C2 - C7) to keep
    voicings in a playable, musical register.
    """

    MIDI_MIN: int = 36  # C2
    MIDI_MAX: int = 96  # C7

    @staticmethod
    def apply(prev_notes: List[int], curr_notes: List[int]) -> List[int]:
        """
        Re-voices curr_notes to minimize semitone motion from prev_notes while
        ensuring smooth part-writing.

        Args:
            prev_notes: MIDI note numbers of the previous chord (sorted ascending).
            curr_notes: MIDI note numbers of the current chord (sorted ascending).

        Returns:
            A new list of MIDI note numbers for curr_notes, re-voiced for
            smooth voice leading.
        """
        if not prev_notes or not curr_notes:
            return list(curr_notes)

        # Allow handling of chords with different note counts (e.g. triad to 7th)
        # but avoid extreme differences that break the voice-leading model.
        if abs(len(prev_notes) - len(curr_notes)) > 2:
            return list(curr_notes)

        result: List[int] = []

        for i, note in enumerate(curr_notes):
            # Anchor the bass (lowest note)
            if i == 0:
                result.append(note)
                continue

            pitch_class = note % 12
            lower_bound = result[i - 1] + 1  # Ensure strictly ascending voices

            # Generate candidate octave transpositions within range and above previous voice
            candidates = [
                pitch_class + (octave * 12)
                for octave in range(1, 9)
                if max(VoiceLeader.MIDI_MIN, lower_bound)
                <= pitch_class + (octave * 12)
                <= VoiceLeader.MIDI_MAX
            ]

            if not candidates:
                # Fallback: force it above the previous note even if it exceeds MIDI_MAX slightly
                fallback = pitch_class + (6 * 12)  # Start at middle C range
                while fallback < lower_bound:
                    fallback += 12
                result.append(fallback)
                continue

            # Determine target reference note from previous chord
            if i < len(prev_notes):
                # Map to corresponding voice
                target = prev_notes[i]
            else:
                # Extension note: map to highest existing voice or just stay close to the rest
                target = prev_notes[-1]

            # Find the candidate that minimizes total motion, avoids parallel fifths/fourths/octaves,
            # and encourages common tone retention.
            def candidate_cost(c: int) -> float:
                cost = float(abs(c - target)) + 0.1 * float(abs(c - 60))

                # Common Tone Retention
                if c == target:
                    cost -= 2.0

                # Parallel Fifths/Fourths/Octaves Avoidance
                if i < len(prev_notes):
                    m_i = c - prev_notes[i]
                    for j in range(i):
                        if j < len(prev_notes):
                            prev_interval = (prev_notes[i] - prev_notes[j]) % 12
                            curr_interval = (c - result[j]) % 12
                            if prev_interval in (0, 5, 7) and curr_interval == prev_interval:
                                m_j = result[j] - prev_notes[j]
                                if (m_i > 0 and m_j > 0) or (m_i < 0 and m_j < 0):
                                    cost += 50.0
                return cost

            best = min(candidates, key=candidate_cost)
            result.append(best)

        # No need to re-sort as we ensured i > i-1 during generation
        return result


# -----------------------------------------------------------------------------
# Class MidiGenerator
# -----------------------------------------------------------------------------
class MidiGenerator:
    def __init__(self, theory: MusicTheory):
        self.theory = theory

    def _calculate_strum_delay_ticks(
        self, midi_options: Dict[str, Any], ticks_per_beat: int
    ) -> int:
        if midi_options.get("strum_delay_ms", 0) > 0:
            strum_delay_seconds = midi_options["strum_delay_ms"] / 1000.0
            strum_delay_beats = strum_delay_seconds * (midi_options.get("bpm", 120) / 60.0)
            return int(strum_delay_beats * ticks_per_beat)
        return 0

    def _setup_midi_tracks(
        self, midi_file: MidiFile, midi_options: Dict[str, Any]
    ) -> Tuple[MidiTrack, Optional[MidiTrack]]:
        chord_track = MidiTrack()
        midi_file.tracks.append(chord_track)
        chord_track.append(MetaMessage("track_name", name="Chords Track", time=0))
        chord_track.append(
            Message(
                "program_change",
                program=midi_options.get("chord_instrument", 0),
                channel=0,
                time=0,
            )
        )
        chord_track.append(
            MetaMessage("set_tempo", tempo=bpm2tempo(midi_options.get("bpm", 120)), time=0)
        )

        bass_track: Optional[MidiTrack] = None
        if midi_options.get("add_bass_track", False):
            bass_track = MidiTrack()
            midi_file.tracks.append(bass_track)
            bass_track.append(MetaMessage("track_name", name="Bass Track", time=0))
            bass_track.append(
                Message(
                    "program_change",
                    program=midi_options.get("bass_instrument", 33),
                    channel=1,
                    time=0,
                )
            )
            bass_track.append(
                MetaMessage("set_tempo", tempo=bpm2tempo(midi_options.get("bpm", 120)), time=0)
            )

        return chord_track, bass_track

    def _generate_bass_note(
        self,
        bass_track: MidiTrack,
        chord_midi_notes: List[int],
        chord_duration_ticks: int,
        midi_options: Dict[str, Any],
    ) -> None:
        bass_note_midi = min(chord_midi_notes)
        while bass_note_midi > self.theory.MIDI_BASE_OCTAVE - 12:
            bass_note_midi -= 12
        if bass_note_midi < 21:
            bass_note_midi += 12

        bass_velocity = max(0, min(127, midi_options.get("base_velocity", 70) + 10))
        bass_note_midi = max(0, min(127, bass_note_midi))

        bass_track.append(
            Message(
                "note_on",
                note=bass_note_midi,
                velocity=bass_velocity,
                channel=1,
                time=0,
            )
        )
        bass_track.append(
            Message(
                "note_off",
                note=bass_note_midi,
                velocity=0,
                channel=1,
                time=chord_duration_ticks,
            )
        )

    def _save_midi_file(self, midi_file: MidiFile, output_filename: str) -> None:
        try:
            output_directory = os.path.dirname(output_filename)
            if output_directory and not os.path.exists(output_directory):
                os.makedirs(output_directory, exist_ok=True)
                print(f"{Fore.GREEN}Directory '{output_directory}' created.{Style.RESET_ALL}")
            midi_file.save(output_filename)
            print(
                f"{Fore.GREEN}MIDI file '{output_filename}' generated successfully.{Style.RESET_ALL}"
            )
        except OSError as e:
            logging.error(f"Failed to save MIDI file '{output_filename}': {e}")
            print(
                f"{Fore.RED}Error saving MIDI file '{output_filename}'. Please check permissions and path validity.{Style.RESET_ALL}"
            )

    def generate_midi_file(
        self,
        chords_to_process: List[Dict[str, Any]],
        output_filename: str,
        midi_options: Dict[str, Any],
    ) -> None:
        ticks_per_beat = 480  # Standard resolution
        strum_delay_ticks = self._calculate_strum_delay_ticks(midi_options, ticks_per_beat)

        midi_file = MidiFile(ticks_per_beat=ticks_per_beat)
        chord_track, bass_track = self._setup_midi_tracks(midi_file, midi_options)

        arp_note_indiv_duration_ticks = 0
        if "arpeggio_note_duration_beats" in midi_options:
            arp_note_indiv_duration_ticks = int(
                midi_options["arpeggio_note_duration_beats"] * ticks_per_beat
            )

        use_voice_leading = midi_options.get("voice_leading", False)
        prev_chord_midi: Optional[List[int]] = None

        for chord_data in chords_to_process:
            chord_midi_notes = chord_data["midi_notes"]
            if not chord_midi_notes:
                continue

            if use_voice_leading and prev_chord_midi is not None:
                chord_midi_notes = VoiceLeader.apply(prev_chord_midi, chord_midi_notes)

            prev_chord_midi = list(chord_midi_notes)

            chord_duration_beats = chord_data["duration_beats"]
            chord_duration_ticks = int(chord_duration_beats * ticks_per_beat)

            if bass_track and midi_options.get("add_bass_track", False):
                self._generate_bass_note(
                    bass_track, chord_midi_notes, chord_duration_ticks, midi_options
                )

            if midi_options.get("arpeggio_style"):
                self._generate_arpeggio_track(
                    chord_track,
                    chord_midi_notes,
                    chord_duration_ticks,
                    midi_options,
                    arp_note_indiv_duration_ticks,
                )
            else:
                self._generate_block_track(
                    chord_track,
                    chord_midi_notes,
                    chord_duration_ticks,
                    midi_options,
                    strum_delay_ticks,
                )

        self._save_midi_file(midi_file, output_filename)

    def _generate_arpeggio_track(
        self,
        chord_track,
        chord_midi_notes,
        chord_duration_ticks,
        midi_options,
        arp_note_indiv_duration_ticks,
    ):
        arp_notes_sequence = list(chord_midi_notes)
        if midi_options.get("arpeggio_style") == "down":
            arp_notes_sequence.reverse()
        elif midi_options.get("arpeggio_style") == "updown":
            if len(arp_notes_sequence) > 1:
                arp_notes_sequence += arp_notes_sequence[len(arp_notes_sequence) - 2 :: -1]

        num_arp_notes = len(arp_notes_sequence)
        base_vel = midi_options.get("base_velocity", 70)
        vel_rand = midi_options.get("velocity_randomization_range", 0)
        vel_rand_min = -vel_rand // 2
        vel_rand_max = max(1, vel_rand // 2)

        if num_arp_notes > 0:
            for idx, note_val in enumerate(arp_notes_sequence):
                velocity = max(
                    0,
                    min(
                        127,
                        # trunk-ignore(ruff/S311)
                        base_vel + random.randint(vel_rand_min, vel_rand_max),  # nosec: S311  # noqa: S311
                    ),
                )

                chord_track.append(
                    Message("note_on", note=note_val, velocity=velocity, channel=0, time=0)
                )

                current_arp_note_actual_duration = arp_note_indiv_duration_ticks
                if idx == num_arp_notes - 1:
                    time_taken_by_prev_arp_notes = (
                        num_arp_notes - 1
                    ) * arp_note_indiv_duration_ticks
                    remaining_slot_time = chord_duration_ticks - time_taken_by_prev_arp_notes
                    current_arp_note_actual_duration = max(0, remaining_slot_time)

                chord_track.append(
                    Message(
                        "note_off",
                        note=note_val,
                        velocity=0,
                        channel=0,
                        time=current_arp_note_actual_duration,
                    )
                )

    def _generate_block_track(
        self,
        chord_track,
        chord_midi_notes,
        chord_duration_ticks,
        midi_options,
        strum_delay_ticks,
    ):
        time_offset_for_strum_completion = 0
        base_vel = midi_options.get("base_velocity", 70)
        vel_rand = midi_options.get("velocity_randomization_range", 0)
        vel_rand_min = -vel_rand // 2
        vel_rand_max = max(1, vel_rand // 2)

        for idx, note_val in enumerate(chord_midi_notes):
            velocity = max(
                0,
                min(
                    127,
                    # trunk-ignore(ruff/S311)
                    base_vel + random.randint(vel_rand_min, vel_rand_max),  # nosec: S311  # noqa: S311
                ),
            )

            delta_t_for_this_note_on = 0
            if idx > 0 and strum_delay_ticks > 0:
                delta_t_for_this_note_on = strum_delay_ticks
                time_offset_for_strum_completion += strum_delay_ticks

            note_val = max(0, min(127, note_val))
            chord_track.append(
                Message(
                    "note_on",
                    note=note_val,
                    velocity=velocity,
                    channel=0,
                    time=delta_t_for_this_note_on if idx > 0 else 0,
                )
            )

        duration_for_first_note_off = max(
            0, chord_duration_ticks - time_offset_for_strum_completion
        )

        for idx, note_val in enumerate(chord_midi_notes):
            chord_track.append(
                Message(
                    "note_off",
                    note=note_val,
                    velocity=0,
                    channel=0,
                    time=duration_for_first_note_off if idx == 0 else 0,
                )
            )
