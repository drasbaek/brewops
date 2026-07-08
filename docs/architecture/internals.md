# Internals: module-by-module

Every source module in `src/brewops/`, what it holds and why.

## `db/connection.py`

The smallest, most foundational module. Defines `DEFAULT_DB_FILENAME = "brewops.db"`. Exposes
`db_path()`, which returns `$BREWOPS_DB` if set else the default — the indirection that lets tests
and scratch runs target a throwaway file. Exposes `connect(path=None)`, which opens the connection,
sets `row_factory = sqlite3.Row` (rows act like dicts), sets `check_same_thread=False`, and runs
`PRAGMA foreign_keys = ON` — because SQLite leaves FK enforcement off by default and BrewOps wants
it on.

## `db/schema.py`

Owns the shape of the database and its reference data. `SCHEMA` is one multi-statement DDL string
creating four tables and three indexes, all `IF NOT EXISTS` so it is safe to re-run. `MACHINES` is
the canonical fleet (four tuples; Old Faithful's telemetry flag is the only false one). `DRINK_TYPES`
is the canonical menu (six name/label tuples). `init_db(conn)` runs the DDL then inserts reference
data with `INSERT OR IGNORE`, making it a no-op on an already-populated database — safe at every API
startup and every ingest. `reset_db(conn)` drops all four tables then calls `init_db`, backing the
destructive `seed`.

## `db/queries.py`

Every SQL statement in the project; the rule is that no SQL lives anywhere else, so the full database
surface is one file. `get_machines` (all, ordered, telemetry flag → bool), `get_machine` (one or
`None`), `get_drink_types`, `drink_type_exists` (bool, used by API brew validation), `insert_brew`
and `insert_maintenance` (parameterized INSERT, return new id), `get_stats` (total + per-drink LEFT
JOIN so zero-count drinks appear + per-day `DATE()` grouping), `get_machine_health` (machine +
brew count + last brew + most recent non-error maintenance + up to five recent errors). The split of
"last maintenance" from "recent errors" mirrors the product distinction between routine upkeep and
alarming failures.

## `ingest/loader.py`

The ingest engine. Module constants codify the file contract: `TIMESTAMP_FORMAT`, the
`MAINTENANCE_TYPES` set, and the expected `BREW_COLUMNS` / `MAINTENANCE_COLUMNS`. Defines the
`IngestReport` dataclass (accumulates a run's outcome), the private helpers `_parse_timestamp`,
`_known_machines`, `_known_drinks`, `_load_row`, and the public `ingest_file` / `ingest_path`.

## `ingest/cli.py`

The two console entry points plus shared reporting. `main` parses args and runs an additive ingest.
`seed` runs a destructive reset then ingests the default inbox, printing `[OK] database seeded.`.
`_print_report` is the shared pretty-printer (first 20 rejections in full, the rest summarized).
`main_entry` / `seed_entry` are the tiny wrappers named in `pyproject.toml` that `sys.exit` with the
integer return codes.

## `api/main.py`

The composition root — the one module importing from every layer, wiring the database and the
frontend behind HTTP. Holds the host/port constants, the accepted-format tuple, the `lifespan`
manager, the `app`, the `get_db` dependency, `parse_timestamp`, the `BrewIn`/`MaintenanceIn` models,
the six route handlers, the `StaticFiles` mount, and `run`.

## `frontend/`

Three static files, no Python, no server logic, no build step. `index.html` is the markup, `app.js`
fetches the read endpoints and wires the entry forms to the write endpoints, `style.css` styles it.
Served verbatim.
