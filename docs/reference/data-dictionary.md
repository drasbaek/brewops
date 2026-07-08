# Data dictionary

Every column, with intent. (For the DDL and constraints in table form, see the schema page.)

## `machines`
- `id` — small integer primary key that every event references; stable, never reused.
- `name` — human-facing name including location; UNIQUE, so no two machines share a name.
- `floor` — integer floor number, for grouping and display.
- `has_telemetry` — integer boolean: 1 for self-reporting machines, 0 for Old Faithful. Converted to
  a real boolean on the way out of the API.

## `drink_types`
- `id` — primary key and display ordering key.
- `name` — stable lower-case machine key used in every brew event and API request; UNIQUE; never
  meant to change, because history is recorded in terms of it.
- `label` — display string; may change freely because no event stores the label, only the name.

## `brew_events`
- `id` — autoincrement primary key.
- `machine_id` — FK into `machines`; cannot reference a nonexistent machine.
- `drink_type` — FK into `drink_types.name`; cannot reference an unknown drink.
- `timestamp` — the canonical naive-local-time string.
- `duration_s` — nullable real; seconds the brew took; always positive when present.
- `temp_c` — nullable real; brew temperature in Celsius.
- `source` — non-null, CHECK IN (`csv`, `manual`): whether telemetry or a human produced the row.

## `maintenance_events`
- `id` — autoincrement primary key.
- `machine_id` — FK into `machines`.
- `type` — non-null, CHECK IN (`descale`, `refill`, `repair`, `error`).
- `timestamp` — the canonical naive-local-time string.
- `note` — nullable free text.
- `error_code` — nullable short code; by convention present on `error` rows, absent otherwise.

## Referential integrity

Foreign keys are enforced at runtime (`PRAGMA foreign_keys = ON`), sitting underneath the
application-level validation as a final line of defense. The `source` and `type` CHECK constraints
likewise enforce the small known value sets in the schema, not just in code.
