# The database layer

Lives in `src/brewops/db/`. **All SQL in the project lives here** — no SQL anywhere else.
Three modules: `connection.py`, `schema.py`, `queries.py`.

## `connection.py`

- DB file is `./brewops.db` by default, overridable via `BREWOPS_DB` (see
  [configuration.md](../operations/configuration.md)).
- Row factory is `sqlite3.Row` (rows act like dicts).
- `check_same_thread=False` (uvicorn may use the connection across threads).
- `PRAGMA foreign_keys = ON` on every connection — foreign keys are enforced.

## `schema.py`

- `SCHEMA` — the DDL (four tables, three indexes). See [schema.md](../data-model/schema.md).
- `MACHINES`, `DRINK_TYPES` — seeded reference data. See
  [machines.md](../data-model/machines.md) and [drink-types.md](../data-model/drink-types.md).
- `init_db(conn)` — create tables + insert reference data with `INSERT OR IGNORE`.
  Idempotent; called at API startup and by the CLI.
- `reset_db(conn)` — drop all tables and recreate. Used by `uv run seed`.

## `queries.py`

Every read/write query, one function each: `get_machines`, `get_machine`,
`get_drink_types`, `drink_type_exists`, `insert_brew`, `insert_maintenance`, `get_stats`,
`get_machine_health`. All use parameterized SQL. See
[api-endpoints.md](../reference/api-endpoints.md) for how they map onto HTTP.
