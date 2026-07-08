# Schema

Four tables, defined in `src/brewops/db/schema.py`. Foreign keys are enforced.

## `machines`
| column | type | notes |
|---|---|---|
| id | INTEGER | primary key |
| name | TEXT | not null, unique |
| floor | INTEGER | not null |
| has_telemetry | INTEGER | not null, default 1; 0 = manual-only |

## `drink_types`
| column | type | notes |
|---|---|---|
| id | INTEGER | primary key |
| name | TEXT | not null, unique; machine key |
| label | TEXT | not null; human-readable |

## `brew_events`
| column | type | notes |
|---|---|---|
| id | INTEGER | primary key |
| machine_id | INTEGER | not null, FK → machines(id) |
| drink_type | TEXT | not null, FK → drink_types(name) |
| timestamp | TEXT | not null, naive local time — see [timestamps.md](timestamps.md) |
| duration_s | REAL | nullable; seconds |
| temp_c | REAL | nullable; Celsius |
| source | TEXT | not null, CHECK IN ('csv','manual') |

## `maintenance_events`
| column | type | notes |
|---|---|---|
| id | INTEGER | primary key |
| machine_id | INTEGER | not null, FK → machines(id) |
| type | TEXT | not null, CHECK IN ('descale','refill','repair','error') |
| timestamp | TEXT | not null, naive local time |
| note | TEXT | nullable |
| error_code | TEXT | nullable; present on `error` rows |

## Indexes
- `idx_brew_events_machine` on `brew_events(machine_id)`
- `idx_brew_events_timestamp` on `brew_events(timestamp)`
- `idx_maintenance_events_machine` on `maintenance_events(machine_id)`
