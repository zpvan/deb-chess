# deb-chess — Fischer Chess Training Camp

[中文版](README_ZH.md)

[![CI](https://github.com/zpvan/deb-chess/actions/workflows/ci.yml/badge.svg)](https://github.com/zpvan/deb-chess/actions/workflows/ci.yml)

A chess-learning web app for kids, inspired by the teaching method of
*Bobby Fischer Teaches Chess*: look at the position, think for yourself,
check the answer — drill mate patterns until they become intuition.
(UI text is in Chinese.)

## Architecture

- **Backend (Python)** — FastAPI + python-chess: curriculum data, move
  validation, checkmate detection, bots, progress storage (SQLite)
- **Frontend (React 19 + Vite)** — thin presentation layer; all game
  logic goes through the `/api` REST endpoints

## Quick Start

```bash
./start.sh        # builds the frontend and starts the server
                  # → http://localhost:8000
```

With Docker (image includes Stockfish):

```bash
docker compose up --build   # → http://localhost:8000
```

Development mode (hot reload):

```bash
# terminal 1: backend
python3 -m venv .venv && .venv/bin/pip install -e 'backend[dev]'
cd backend && ../.venv/bin/uvicorn app.main:app --reload --port 8000

# terminal 2: frontend (/api is proxied to :8000)
npm install && npm run dev   # → http://localhost:3000
```

## Testing

```bash
cd backend && ../.venv/bin/pytest tests/ -v
```

The suite covers the bot logic, the lesson session state machine, the
progress rules, the REST API, and a full validation of every FEN and
answer move in the curriculum data.

## Curriculum Data

- Source of truth: `backend/data/curriculum.json`
  (5 chapters, 20 levels, 82 steps; lesson text in Chinese).
- After editing, run the validator — every FEN must be legal and every
  answer move must be playable:

  ```bash
  python3 backend/scripts/validate_curriculum.py
  ```

- Book page scans are **not** included (see `data/README.md`); the app
  does not need them.

## License & Copyright

- Code: **GPL-3.0** (see [LICENSE](LICENSE)), consistent with the GPL-3.0
  dependencies python-chess and Stockfish.
- *Bobby Fischer Teaches Chess* (book content and page images) is
  copyrighted by its publisher. This repository contains and distributes
  no book pages. Lesson text is original Chinese writing; the puzzles are
  classic checkmate patterns.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
