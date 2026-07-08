# Request lifecycle & guided tours

How a request actually travels through BrewOps, end to end, on both write paths.

## Cold start

`uv run start` resolves (via `pyproject.toml`) to `brewops.api.main:run`, a thin wrapper around
`uvicorn.run(app, host="127.0.0.1", port=8123)`. Uvicorn imports the module, which builds the
FastAPI `app` at import time and wires up the `lifespan` async context manager. The lifespan body
runs once as the server comes up: it opens a connection with the same `connect()` helper every
request uses, calls `init_db` to ensure the schema and reference data exist, then yields for the
life of the process. There is nothing after the yield — no global connection to close, no pool to
drain, no background task to cancel — because connections are per-request and short-lived.

The static frontend is mounted at `/` with `html=True`, so `/` returns `index.html`. The mount is
added **after** all `/api/...` routes, and FastAPI resolves routes in registration order, so the
explicit JSON routes win and the catch-all static mount handles only what is left. If you add a JSON
endpoint, add it before the mount.

## Per-request connection

A JSON request that needs the database resolves the `get_db` dependency: a generator that opens a
fresh connection, yields it to the handler, and closes it in a `finally` block — so the connection
is always closed, even on error. No pooling: local SQLite connections are cheap and the workload is
tiny. `check_same_thread=False` is set because uvicorn may run a handler on a different thread than
the one that created the connection object; since each connection is confined to one request and
never shared, this is safe.

## Guided tour: one manual brew (API path)

A human logs an espresso for Old Faithful in the dashboard. The browser's `datetime-local` control
produces `2026-07-08T09:41`. The JS posts `{"machine_id": 3, "drink_type": "espresso",
"timestamp": "2026-07-08T09:41", "duration_s": null, "temp_c": null}` to `POST /api/brews`.
FastAPI validates the body against the `BrewIn` model (bad types → 422 for free). The `log_brew`
handler then validates in order: `get_machine` (unknown → 400), `drink_type_exists` (unknown → 400),
then `parse_timestamp`. It calls `insert_brew(..., source="manual")` — every API brew is `manual` —
commits, and returns `{"id": <n>, "status": "logged"}`. The trip touched only the API and database
layers and left one `brew_events` row with `source = 'manual'`.

## Guided tour: one ingest run (CSV path)

`uv run ingest` (no args) resolves to `cli:main_entry` → `main(None)`. `argparse` defaults `path` to
`data/inbox`. If the path is missing it prints `[FAIL] path not found` and returns exit 1. Otherwise
it opens a connection, calls `init_db` (idempotent — ingest never drops), and calls `ingest_path`.
For a folder, `ingest_path` uses `sorted(path.glob("*.csv"))` for deterministic order, fixes a single
`now`, and threads one `IngestReport` and that `now` through every `ingest_file`. `ingest_file`
classifies by filename prefix, snapshots known machine ids and drink names once, then reads rows
starting the counter at 2 (the header is line 1). Each row goes to `_load_row`, which returns `None`
on success or a rejection reason string. The file commits once at the end. `main` then prints the
report (totals, first 20 rejections, skipped files) and returns exit 0.

## Why two write paths

Both paths enforce the same domain rules but are implemented separately on purpose: files may hold
thousands of rows where a few are bad (skip-and-report is correct), while the API serves one human
action with a person waiting (accept-or-reject-now is correct). Merging them would force one failure
model onto the other. The shared rules are documented centrally so they cannot drift.
