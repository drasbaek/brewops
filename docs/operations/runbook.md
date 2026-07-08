# Operational runbook

Step-by-step procedures for the situations that actually arise.

## Stand up a fresh instance
Clone the repo, `uv sync` to install deps into the managed environment, `uv run seed` to create and
populate the database from the sample inbox, `uv run start` to bring up the server on port 8123. Open
the dashboard to confirm stats and machine cards render.

## Load a new monthly export
Drop the CSV into `data/inbox/`, confirm its name begins with `brews`, `manual`, or `maintenance` so
it is recognized, and run `uv run ingest`. Read the report: confirm the file processed, note rows
loaded, scrutinize rejections. Ingest is additive, so ingest each new file exactly once — a second
run double-loads it.

## Recover from a bad load
Remove or fix the offending file in the inbox and run `uv run seed`, which drops everything and
rebuilds from the current inbox. This is destructive of any manually logged brews that live only in
the database and not in a CSV — export or re-enter those if they matter.

## Diagnose rejected rows
Every rejection names the file, the line number (header counted as line 1), and a specific reason.
Open the file, go to that line, compare against the CSV format and the validation rules. Most common
causes, roughly in order: non-canonical times, unknown drink names, unknown machine ids, non-positive
durations.

## Point at a scratch database
Set `BREWOPS_DB` to a throwaway path for any command, e.g. `BREWOPS_DB=/tmp/scratch.db uv run seed`
then `BREWOPS_DB=/tmp/scratch.db uv run start`, to experiment without touching the real `brewops.db`.

## Run the workshop checks
`uv run scripts/setup_check.py` verifies setup and prints a completion code (pre-work).
`uv run scripts/lab_a_check.py` is the finish line for Lab A.
