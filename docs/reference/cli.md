# CLI reference

Three console scripts, defined in `pyproject.toml`:

| Command | Entry point | Purpose |
|---------|-------------|---------|
| `uv run start` | `brewops.api.main:run` | Start the web app on port 8123 |
| `uv run ingest [path]` | `brewops.ingest.cli:main_entry` | Ingest CSVs (additive) |
| `uv run seed` | `brewops.ingest.cli:seed_entry` | Reset DB, ingest `data/inbox/` |

`uv run ingest` takes one optional positional `path` (file or folder), default `data/inbox`.
`uv run pytest` runs the tests (plain pytest, not a console script).

See seeding-and-ingest.md for the difference between
`seed` and `ingest`, and testing.md for the suite.

## Exit codes

| Command | Code | Meaning |
|---------|------|---------|
| ingest | 0 / 1 | success / path not found |
| seed | 0 / 1 | success / `data/inbox` not found (run from repo root) |
