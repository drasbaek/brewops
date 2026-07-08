# Seeding vs ingesting

Two ways to get data in. Both go through the same pipeline
(ingest-pipeline.md); they differ in whether they
wipe first.

## `uv run seed` — destructive reset

`brewops.ingest.cli:seed_entry` → `seed()`:

1. Checks `data/inbox/` exists (else fails — run from the repo root).
2. `reset_db` **drops all four tables** and recreates them.
3. Ingests everything in `data/inbox/`.
4. Prints the report and `[OK] database seeded.`

Use it to return to a known-good state.

## `uv run ingest <path>` — additive

`brewops.ingest.cli:main_entry` → `main()`:

- `<path>` is a file or a folder of CSVs; defaults to `data/inbox`.
- Does **not** drop anything — calls `init_db` (idempotent), then loads. Additive.
- Prints the report. Exit `1` if the path is missing, else `0`.

See cli.md and csv-formats.md.
