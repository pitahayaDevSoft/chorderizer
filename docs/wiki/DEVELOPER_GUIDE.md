# Developer Guide

Documentation for setting up and contributing to the Chorderizer codebase.

## Development Setup

1. **Prerequisites**:
   - Python 3.8+
   - Pip (Python Package Index)

2. **Clone and Install**:

   ```bash
   git clone https://github.com/julesklord/Chorderizer.git
   cd Chorderizer
   pip install -e .
   ```

3. **Running in Development Mode**:
   To run the project while making changes without reinstalling:

   ```powershell
   $env:PYTHONPATH="src"
   py -m chorderizer.chorderizer
   ```

## Testing Suite

Chorderizer uses `pytest` for automated testing.

- **Running all tests**:

  ```bash
  pytest
  ```

- **Test Categories**:
  - `tests/test_theory.py`: Music theory math and parsing.
  - `tests/test_generators.py`: Chord and MIDI logic (uses mocks).
  - `tests/test_security.py`: Path sanitization and security checks.

## Quality Control

We use **Ruff** for linting and formatting to ensure a high-quality codebase.

- **Check for issues**:

  ```bash
  ruff check src/ tests/
  ```

- **Format code**:

  ```bash
  ruff format src/ tests/
  ```

## Contribution Workflow

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

> [!IMPORTANT]
> Always run the test suite and ensure no regressions before opening a Pull Request.
