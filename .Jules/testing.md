# Testing Learnings

- When writing tests for functions that involve specific data configurations (like guitar string tunings mapping to specific MIDI notes), explicitly define the expected mapping in the test comments. This makes it easier to verify correctness during test creation and maintenance (e.g., E6 open string is 40. Note 48 is fret 8).
- For functions that process lists and have short-circuit logic for empty lists (like `if not midi_notes: return []`), always verify that the function implementation actually matches the prompt's implied logic. If there's a discrepancy (like the prompt stating the code has an early return, but the actual file doesn't), fix the underlying code first to make it match the correct intended logic before asserting against it in tests.
