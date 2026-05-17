# Contributing to Chorderizer

First off, thank you for considering contributing to Chorderizer! It's people like you that make Chorderizer such a great tool for the musical community.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). (Coming soon!)

## How Can I Contribute?

### Reporting Bugs

- Check the [Issue Tracker](https://github.com/TropicalDev/Chorderizer/issues) to see if the bug has already been reported.
- If not, create a new issue. Please include:
  - A clear, descriptive title.
  - Steps to reproduce the bug.
  - Expected vs. Actual behavior.
  - Your environment (OS, Python version).

### Suggesting Enhancements

- Open a new issue with the label `enhancement`.
- Describe the feature you'd like to see and why it would be useful.

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes (`pytest`).
5. Run the linter (`ruff check src/ tests/`) and formatter (`ruff format src/ tests/`).
6. Issue that pull request!

## Style Guide

- We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
- We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.
- Line length is capped at 100 characters.
- Use double quotes for strings.

## Development Environment

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

---

*Happy Coding!*
