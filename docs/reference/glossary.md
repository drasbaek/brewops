# Glossary

- **Additive ingest** — an ingest run that inserts new rows without removing existing ones; the
  behavior of `uv run ingest`.
- **Brew event** — one act of a machine making a drink; a row in `brew_events`.
- **Canonical timestamp** — the fixed `YYYY-MM-DD HH:MM:SS` naive-local-time shape every stored time
  is normalized to.
- **Composition root** — `api/main.py`, the one module that wires the database layer and the frontend
  together behind HTTP.
- **Destructive reset** — dropping all tables and rebuilding them; the behavior of `uv run seed`.
- **Drink type** — a supported drink, a `name`/`label` pair.
- **Fleet** — the complete set of machines BrewOps knows about.
- **Idempotent initialization** — `init_db`, safe to run any number of times (`IF NOT EXISTS`,
  `INSERT OR IGNORE`).
- **Inbox** — the `data/inbox/` folder scanned by ingest.
- **Lenient parser** — the API's timestamp parser, which accepts three input formats.
- **Maintenance event** — one act of servicing or one error; a row in `maintenance_events`.
- **Manual path** — the human write path (dashboard form or `manual_*.csv` export); stored with
  `source = 'manual'`.
- **Naive local time** — a time with no zone, describing the one building's wall clock.
- **Provenance** — the `source` column, recording whether a brew came from telemetry or a human.
- **Rejection** — a single row skipped during ingest, recorded with file, line, and reason.
- **Strict parser** — the ingest timestamp parser, which accepts only the canonical shape.
- **Telemetry** — automated CSV emission by a machine; three of four machines have it.
