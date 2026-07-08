# The ingest pipeline

The automated write path. Lives in `src/brewops/ingest/`: `loader.py` (engine) and
`cli.py` (the `ingest` and `seed` entry points).

## What it does

1. Discovers CSV files in a folder (or takes a single file). Folders are processed in
   sorted order for determinism.
2. Classifies each file by filename prefix (see csv-formats.md):
   - `brews*` → brew events, `source = 'csv'`
   - `manual*` → brew events, `source = 'manual'` (Old Faithful paper-log exports)
   - `maintenance*` → maintenance events
   - anything else → skipped, recorded in `report.skipped_files`
3. Validates and inserts each row. Bad rows are skipped and recorded — the rest of the
   file still loads. See validation-rules.md.
4. Returns an `IngestReport`.

## The `IngestReport`

Dataclass with: `files`, `brews_loaded`, `maintenance_loaded`,
`rejected` (list of `(file, line, reason)`), and `skipped_files`. The CLI prints it; the
first 20 rejections are shown in full, the rest summarized as a count.

## The `now` parameter

`ingest_path`/`ingest_file` take a `now` datetime (defaults to `datetime.now()`) used to
reject future timestamps. It is injectable for deterministic tests. See
timestamps.md.

## Header line

The CSV header is line 1; data rows start at line 2. That is the line number you see in
rejection reports.
