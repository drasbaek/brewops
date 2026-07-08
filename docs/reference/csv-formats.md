# CSV formats

The ingest layer recognizes three file families by filename prefix. Header is line 1; data
starts at line 2. Timestamps must be canonical `YYYY-MM-DD HH:MM:SS` (see
timestamps.md).

## `brews_*.csv` — telemetry brews
Columns: `machine_id, drink, timestamp, duration_s, temp_c`
- `machine_id` — int, known machine
- `drink` — known drink `name`
- `duration_s` — float, must be > 0
- `temp_c` — float

Loaded with `source = 'csv'`.

## `manual_*.csv` — paper-log exports
Same columns as `brews_*.csv`. Exports of Old Faithful's paper log. Loaded with
`source = 'manual'`.

## `maintenance_*.csv` — maintenance & errors
Columns: `machine_id, type, timestamp, note, error_code`
- `type` — one of `descale`, `refill`, `repair`, `error`
- `note` — optional
- `error_code` — optional, usually on `error` rows

## Sample data
`data/inbox/` ships ~3 months across all machines: `brews_bertha_*`, `brews_intern_*`,
`brews_rocket_*`, `maintenance_*`, and `manual_old-faithful_log.csv`. Files whose names
match no prefix are skipped and reported.
