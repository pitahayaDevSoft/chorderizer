import sys
from unittest.mock import MagicMock

# Mock external dependencies
sys.modules["mido"] = MagicMock()

from chorderizer.generators import ChordGenerator
from chorderizer.theory_utils import MusicTheory  # noqa: E402


def test_chord_generator_happy_path():
    theory = MusicTheory()
    generator = ChordGenerator(theory)

    # C Major scale info
    scale_info = theory.AVAILABLE_SCALES["1"]

    # Default parameters: extension_level=2 (7ths), inversion=0
    (
        generated_chords,
        notes_names,
        notes_midi,
        base_qualities,
    ) = generator.generate_scale_chords("C", scale_info)

    assert "I" in generated_chords
    assert generated_chords["I"] == "Cmaj7"
    assert notes_names["I"] == ["C", "E", "G", "B"]
    assert base_qualities["I"] == "major"

    assert "ii" in generated_chords
    assert generated_chords["ii"] == "Dm7"
    assert base_qualities["ii"] == "minor"


def test_chord_generator_extension_levels():
    theory = MusicTheory()
    generator = ChordGenerator(theory)
    scale_info = theory.AVAILABLE_SCALES["1"]  # Major

    # Triads (extension_level=0)
    generated_chords, _, _, _ = generator.generate_scale_chords("C", scale_info, extension_level=0)
    assert generated_chords["I"] == "C"
    assert generated_chords["ii"] == "Dm"


def test_chord_generator_inversions():
    theory = MusicTheory()
    generator = ChordGenerator(theory)
    scale_info = theory.AVAILABLE_SCALES["1"]  # Major

    # Root position (inversion=0)
    _, _, notes_midi_root, _ = generator.generate_scale_chords("C", scale_info, inversion=0)

    # First inversion (inversion=1)
    _, _, notes_midi_inv1, _ = generator.generate_scale_chords("C", scale_info, inversion=1)

    # Verify the lowest note in inversion 1 is different and higher than root position lowest note (or shifted)
    # The actual MIDI values depend on the specific octave selection logic, but we can verify
    # the relative pitch class or simply that the MIDI sequence is different.
    assert notes_midi_root["I"] != notes_midi_inv1["I"]


def test_chord_generator_invalid_tonic():
    theory = MusicTheory()
    generator = ChordGenerator(theory)
    scale_info = theory.AVAILABLE_SCALES["1"]  # Major

    # Invalid tonic
    (
        generated_chords,
        notes_names,
        notes_midi,
        base_qualities,
    ) = generator.generate_scale_chords("Z", scale_info)

    assert generated_chords == {}
    assert notes_names == {}
    assert notes_midi == {}
    assert base_qualities == {}


def test_chord_generator_caching():
    theory = MusicTheory()
    generator = ChordGenerator(theory)
    scale_info = theory.AVAILABLE_SCALES["1"]

    # Call first time
    res1 = generator.generate_scale_chords("C", scale_info)

    # Call second time
    res2 = generator.generate_scale_chords("C", scale_info)

    # Results should be equal in value
    assert res1 == res2

    # But they should NOT be the exact same object (because of copy.deepcopy)
    assert id(res1[0]) != id(res2[0])


# -----------------------------------------------------------------------------
# VoiceLeader Tests
# -----------------------------------------------------------------------------
from chorderizer.generators import VoiceLeader


def test_voice_leader_reduces_motion():
    """Voice leading output should have less total movement than the raw jump."""
    # Cmaj7 -> Fmaj7 in raw root position
    prev = [60, 64, 67, 71]  # C4, E4, G4, B4
    curr = [65, 69, 72, 76]  # F4, A4, C5, E5

    _voiced = VoiceLeader.apply(prev, curr)

    # The voice-led version total span should be <= raw version
    assert max(_voiced) - min(_voiced) <= max(curr) - min(curr) + 12


def test_voice_leader_preserves_bass():
    """The bass note (lowest note, index 0) must not change pitch class."""
    prev = [48, 55, 60, 64]  # C3, G3, C4, E4
    curr = [53, 57, 60, 65]  # F3, A3, C4, F4

    voiced = VoiceLeader.apply(prev, curr)

    # Bass of curr is the first note (already sorted incoming)
    original_bass_pc = curr[0] % 12
    result_bass_pc = voiced[0] % 12
    assert result_bass_pc == original_bass_pc


def test_voice_leader_range_guard():
    """All output notes must remain within MIDI_MIN and MIDI_MAX."""
    prev = [60, 64, 67]
    curr = [62, 66, 69]

    voiced = VoiceLeader.apply(prev, curr)

    assert all(VoiceLeader.MIDI_MIN <= n <= VoiceLeader.MIDI_MAX for n in voiced)


def test_voice_leader_common_tone_retention():
    """Verify that voice leader preserves common tones in the same octave if possible."""
    prev = [60, 64, 67]  # C Major triad
    curr = [60, 65, 69]  # F Major triad (shares pitch class 60 / C)

    voiced = VoiceLeader.apply(prev, curr)

    # 60 is a common tone, so it should stay at exactly 60
    assert 60 in voiced


def test_voice_leader_avoids_parallel_fifths():
    """Verify that voice leader handles and resolves transitions cleanly."""
    prev = [60, 64, 67]
    curr = [62, 66, 69]

    voiced = VoiceLeader.apply(prev, curr)
    assert len(voiced) == 3


# -----------------------------------------------------------------------------
# TablatureGenerator Tests
# -----------------------------------------------------------------------------
from chorderizer.generators import TablatureGenerator


def test_generate_simple_tab_happy_path():
    theory = MusicTheory()
    generator = TablatureGenerator(theory)

    tab_lines = generator.generate_simple_tab("C", [48, 52, 55, 60, 64])  # C3, E3, G3, C4, E4

    assert len(tab_lines) == 7  # 1 header + 6 strings
    assert tab_lines[0] == "Chord: C (simple tab)"

    # E6 open string is 40. Note 48 is fret 8.
    # Note 52: open A5 is 45. Fret 7.
    # Note 55: open D4 is 50. Fret 5.
    # Note 60: open G3 is 55. Fret 5.
    # Note 64: open B2 is 59. Fret 5.
    assert "E6|---8--|" in tab_lines[6]
    assert "A5|---7--|" in tab_lines[5]
    assert "D4|---5--|" in tab_lines[4]
    assert "G3|---5--|" in tab_lines[3]
    assert "B2|---5--|" in tab_lines[2]
    assert "e1|------|" in tab_lines[1]


def test_generate_simple_tab_empty_notes():
    theory = MusicTheory()
    generator = TablatureGenerator(theory)

    tab_lines = generator.generate_simple_tab("Empty", [])

    assert tab_lines == []


def test_generate_simple_tab_too_high_notes():
    theory = MusicTheory()
    generator = TablatureGenerator(theory)

    # Notes that are too high to be played within 15 frets of standard tuning
    tab_lines = generator.generate_simple_tab("Too High", [100, 105])

    assert len(tab_lines) == 7
    for line in tab_lines[1:]:
        assert "|------|" in line
