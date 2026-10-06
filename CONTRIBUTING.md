# Contributing to deb-chess

Thanks for your interest! This document explains how to set up the project
and what we expect in a pull request.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -e 'backend[dev]'
npm install
```

Run everything before submitting:

```bash
cd backend && ../.venv/bin/pytest tests/ -v   # backend tests
cd .. && npm run build                        # frontend type-check + build
```

Both must pass. CI runs the same checks on every PR.

## Curriculum changes

- Edit `backend/data/curriculum.py` only (there is no other source).
- Every change must pass `python3 backend/scripts/validate_curriculum.py`
  — it checks every FEN and every answer move with python-chess.
- Never reintroduce book page scans or other copyrighted material
  (see `data/README.md`).

## Code style

- Backend: plain type-annotated Python, pydantic models for payloads,
  TDD with pytest (write the failing test first).
- Frontend: keep it a thin presentation layer — no chess rules in the
  browser, all game logic belongs in the backend.
- Commits: small, imperative subject lines
  (e.g. `feat: add mate-in-two step type`).

## Pull requests

1. Fork and create a branch from `main`.
2. Keep the PR focused on one change.
3. Fill in the PR template and make sure CI is green.
