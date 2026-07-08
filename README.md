# BrewOps ☕

Telemetry and operations for the office coffee machines. Python, FastAPI, SQLite.
The full docs live in `docs/` — this file is the map. **Read only the page you need.**

```
uv sync && uv run seed && uv run start   # then open http://localhost:8123
```

## Documentation map

Open the **one** page that matches your task and read only that — each page is
self-contained. Do not crawl the whole tree.

### `docs/architecture/` — how the pieces fit
- [overview.md](docs/architecture/overview.md) — the four layers and how data flows
- [request-lifecycle.md](docs/architecture/request-lifecycle.md) — cold start, per-request connections, guided tours of both write paths
- [internals.md](docs/architecture/internals.md) — module-by-module deep dive of `src/brewops/`
- [ingest-pipeline.md](docs/architecture/ingest-pipeline.md) — the CSV write path
- [api-layer.md](docs/architecture/api-layer.md) — FastAPI app, routes, the manual write path
- [database.md](docs/architecture/database.md) — connection, schema module, queries
- [design-decisions.md](docs/architecture/design-decisions.md) — the ADRs behind the codebase
- [frontend.md](docs/architecture/frontend.md) — the no-build-step dashboard

### `docs/data-model/` — the domain
- [schema.md](docs/data-model/schema.md) — the four tables and their constraints
- [machines.md](docs/data-model/machines.md) — the fleet (incl. Old Faithful)
- [drink-types.md](docs/data-model/drink-types.md) — supported drinks, name vs label
- [timestamps.md](docs/data-model/timestamps.md) — timestamp formats, parsing, future-rejection

### `docs/operations/` — running it
- [running.md](docs/operations/running.md) — start the app
- [seeding-and-ingest.md](docs/operations/seeding-and-ingest.md) — `seed` vs `ingest`
- [configuration.md](docs/operations/configuration.md) — env vars, host/port
- [runbook.md](docs/operations/runbook.md) — step-by-step operational procedures
- [troubleshooting.md](docs/operations/troubleshooting.md) — common problems

### `docs/reference/` — look-up tables
- [api-endpoints.md](docs/reference/api-endpoints.md) — every endpoint, request/response
- [csv-formats.md](docs/reference/csv-formats.md) — the three CSV file families
- [validation-rules.md](docs/reference/validation-rules.md) — every rejection rule
- [data-dictionary.md](docs/reference/data-dictionary.md) — every column, with intent
- [stats-and-health.md](docs/reference/stats-and-health.md) — what the dashboard numbers mean
- [cli.md](docs/reference/cli.md) — the console scripts
- [testing.md](docs/reference/testing.md) — the pytest suite
- [faq.md](docs/reference/faq.md) — frequently asked questions
- [glossary.md](docs/reference/glossary.md) — terms used across the docs
