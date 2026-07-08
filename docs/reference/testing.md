# Testing

Run: `uv run pytest`. Tests live in `tests/`:

- `test_db.py` — schema, queries, reference data
- `test_ingest.py` — the ingest pipeline, incl. validation & rejection
- `test_api.py` — the HTTP endpoints (via the ASGI client in `tests/asgi_client.py`)
- `test_frontend.py` — the frontend is served and wired up

Tests run against a throwaway database via `BREWOPS_DB` (see
configuration.md). The ingest layer's injectable `now`
(see ingest-pipeline.md) makes future-timestamp tests
deterministic.
