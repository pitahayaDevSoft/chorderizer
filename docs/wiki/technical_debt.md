# Technical Debt

This file tracks deferred work that is known, intentional, and visible.

## High

- Dual UI surface area remains in the repository.
  Why:
  Chorderizer currently supports both the classic prompt-driven flow and the Textual dashboard.
  Exit condition:
  Decide whether both modes are strategic and document the long-term support policy, or deprecate one path explicitly.

## Medium

- Repository documentation still depends on manual synchronization.
  Why:
  README, architecture docs, and changelog need to move together when behavior changes.
  Exit condition:
  Add a lightweight maintenance checklist to the development guide or PR process.

- Python support floor remains broad (`>=3.8`).
  Why:
  Wide compatibility is useful, but it increases CI surface area and maintenance burden.
  Exit condition:
  Reassess supported versions based on actual user need and dependency support.

## Low

- Demo assets are large and manually maintained.
  Why:
  `demo.gif` is useful for discoverability but expensive to update and easy to forget.
  Exit condition:
  Define a repeatable process for regenerating demo assets or replace with lighter media.
