# API endpoints

All under `/api`, all JSON. Errors are `{"detail": "..."}` with an HTTP status.

## `GET /api/stats`
```json
{
  "total_brews": 1234,
  "per_drink": [{"name": "espresso", "label": "Espresso", "count": 500}],
  "per_day": [{"day": "2026-04-01", "count": 42}]
}
```
`per_drink` is a LEFT JOIN from `drink_types`, so zero-count drinks appear. `per_day` is
ordered ascending (grouped via `DATE(timestamp)` — see
timestamps.md).

## `GET /api/machines`
```json
[{"id": 1, "name": "Bertha (3rd floor)", "floor": 3, "has_telemetry": true}]
```

## `GET /api/machines/{id}`
Machine health card, or `HTTP 404` if unknown.
```json
{
  "id": 1, "name": "Bertha (3rd floor)", "floor": 3, "has_telemetry": true,
  "brew_count": 512, "last_brew": "2026-07-07 16:03:00",
  "last_maintenance": {"type": "descale", "timestamp": "2026-06-30 08:00:00", "note": null, "error_code": null},
  "recent_errors": [{"timestamp": "2026-07-05 11:12:00", "error_code": "E14", "note": "low pressure"}]
}
```
`last_maintenance` excludes `error` rows; those appear in `recent_errors` (up to 5, newest first).

## `GET /api/drink-types`
```json
[{"id": 1, "name": "espresso", "label": "Espresso"}]
```

## `POST /api/brews`
Body `BrewIn`: `machine_id`, `drink_type`, `timestamp`, `duration_s?`, `temp_c?`.
Validates machine, drink type, timestamp. Stores `source = 'manual'`. Returns
`{"id": <n>, "status": "logged"}`.

## `POST /api/maintenance`
Body `MaintenanceIn`: `machine_id`, `type`, `timestamp`, `note?`, `error_code?`.
Validates machine and type. Returns `{"id": <n>, "status": "logged"}`.

Validation detail: validation-rules.md.
