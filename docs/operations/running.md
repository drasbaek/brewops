# Running the app

```
uv sync
uv run seed
uv run start
```

Then open <http://localhost:8123>. Stop with `Ctrl+C`.

`uv run start` calls `brewops.api.main:run` → `uvicorn.run(app, host="127.0.0.1",
port=8123)`. On startup the `lifespan` hook initializes the database (creates tables, seeds
reference data). It then serves the JSON API under `/api/...` and the static dashboard
under `/`.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `winget install astral-sh.uv` (Windows),
  `brew install uv` (macOS), or see the uv docs.
- Or a GitHub Codespace / VS Code Dev Container — `.devcontainer/` sets it up.

## Workshop scripts

- `uv run scripts/setup_check.py` — verifies setup, prints your completion code (pre-work).
- `uv run scripts/lab_a_check.py` — the finish line for Lab A.
