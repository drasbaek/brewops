# BrewOps — Project Memory

Telemetry app for the office coffee machines. Python with FastAPI, data in SQLite.

Run it with `uv run start` and open http://localhost:8123.

The code is in `src/brewops/`.

## Documentation map

The full project documentation lives in `docs/` — this file is only the map.
Open the **one** page that matches your task and read only that — each page is
self-contained. Do not crawl the whole tree.

### `docs/architecture/` — how the pieces fit
- `docs/architecture/overview.md` — the four layers and how data flows
- `docs/architecture/request-lifecycle.md` — cold start, per-request connections, guided tours of both write paths
- `docs/architecture/internals.md` — module-by-module deep dive of `src/brewops/`
- `docs/architecture/ingest-pipeline.md` — the CSV write path
- `docs/architecture/api-layer.md` — FastAPI app, routes, the manual write path
- `docs/architecture/database.md` — connection, schema module, queries
- `docs/architecture/design-decisions.md` — the ADRs behind the codebase
- `docs/architecture/frontend.md` — the no-build-step dashboard

### `docs/data-model/` — the domain
- `docs/data-model/schema.md` — the four tables and their constraints
- `docs/data-model/machines.md` — the fleet (incl. Old Faithful)
- `docs/data-model/drink-types.md` — supported drinks, name vs label
- `docs/data-model/timestamps.md` — timestamp formats, parsing, future-rejection

### `docs/operations/` — running it
- `docs/operations/running.md` — start the app
- `docs/operations/seeding-and-ingest.md` — `seed` vs `ingest`
- `docs/operations/configuration.md` — env vars, host/port
- `docs/operations/runbook.md` — step-by-step operational procedures
- `docs/operations/troubleshooting.md` — common problems

### `docs/reference/` — look-up tables
- `docs/reference/api-endpoints.md` — every endpoint, request/response
- `docs/reference/csv-formats.md` — the three CSV file families
- `docs/reference/validation-rules.md` — every rejection rule
- `docs/reference/data-dictionary.md` — every column, with intent
- `docs/reference/stats-and-health.md` — what the dashboard numbers mean
- `docs/reference/cli.md` — the console scripts
- `docs/reference/testing.md` — the pytest suite
- `docs/reference/faq.md` — frequently asked questions
- `docs/reference/glossary.md` — terms used across the docs
