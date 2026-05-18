# Decisions

This file records repository-level decisions that materially affect how Chorderizer is built and maintained.

## 2026-04-17 | Repository standard alignment

- Decision:
  Keep Chorderizer classified as a maintained project, not yet a certified reference repository.
- Why:
  The codebase is stable and tested, but the repository previously lacked explicit maintenance artifacts and had drift between runtime and architecture documentation.
- Alternatives rejected:
  - Leave the repo as-is and rely only on README + tests.
  - Treat the repo as fully certified without visible maintenance discipline.
- Result:
  Added repository-level maintenance documents and updated architecture/README to reflect the current Textual dashboard path.

## 2026-04-17 | CI workflow consolidation

- Decision:
  Keep a split CI model: compatibility matrix in `ci.yml`, quality/security gate in `python-ci.yml`, publishing in `python-publish.yml`, secrets scanning in `security.yml`.
- Why:
  The split makes responsibilities explicit and avoids duplicate “do everything” workflows.
- Alternatives rejected:
  - Multiple overlapping Python build workflows with unclear ownership.
  - A single all-in-one workflow mixing compatibility, linting, security, and publishing concerns.
