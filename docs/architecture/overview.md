# Architecture overview

BrewOps is a small layered app. Data flows in from CSV files and manual UI entry,
through validation into SQLite, and back out through a JSON API to a static dashboard.

```
CSV files (data/inbox)        human at the dashboard
        |                             |
     ingest layer               API layer (POST)
        |                             |
        +------ validate + insert ----+
                       |
                  database layer
                       |
                   brewops.db (SQLite)
                       |
                  API layer (GET) --> frontend
```

## The four layers

1. **Ingest** (`src/brewops/ingest/`) — reads CSVs, validates each row, inserts the good
   ones, reports the rest. See [ingest-pipeline.md](ingest-pipeline.md).
2. **Database** (`src/brewops/db/`) — schema, connection, and every SQL query. No SQL lives
   anywhere else. See [database.md](database.md).
3. **API** (`src/brewops/api/`) — FastAPI JSON endpoints + static frontend mount. See
   [api-layer.md](api-layer.md).
4. **Frontend** (`src/brewops/frontend/`) — static dashboard, no build step. See
   [frontend.md](frontend.md).

## Two write paths

Telemetry machines emit CSVs (ingest path). Old Faithful emits nothing, so humans log its
brews via the API (manual path). Both enforce the same
[validation rules](../reference/validation-rules.md); they differ only in how they report
failure — a bad CSV row is skipped and reported, a bad API request returns HTTP 400.

## Startup

The FastAPI `lifespan` hook opens a connection and calls `init_db` (creates tables, seeds
reference data, idempotent). Each request gets a fresh connection via the `get_db`
dependency; there is no pool.
