# The API layer

A single FastAPI app in `src/brewops/api/main.py`. Serves the JSON API and mounts the
static frontend on the same port.

## Setup

- Host `127.0.0.1`, port `8123` (constants in `main.py`).
- `lifespan` initializes the DB at startup.
- `get_db` is a dependency yielding a per-request connection.
- The frontend dir is mounted at `/` with `html=True`, so `/` serves `index.html`.

## Endpoints

Full detail in api-endpoints.md.

| Method | Path                  | Purpose                        |
|--------|-----------------------|--------------------------------|
| GET    | `/api/stats`          | totals, per-drink, per-day     |
| GET    | `/api/machines`       | list machines                  |
| GET    | `/api/machines/{id}`  | one machine's health card      |
| GET    | `/api/drink-types`    | list drinks                    |
| POST   | `/api/brews`          | log a manual brew              |
| POST   | `/api/maintenance`    | log a maintenance event        |

## The manual write path

`POST /api/brews` and `POST /api/maintenance` are how humans record activity for machines
without telemetry (Old Faithful). Request bodies are the Pydantic models `BrewIn` and
`MaintenanceIn`. The API validates the machine, the drink type / maintenance type, and the
timestamp, then inserts. Manual brews always get `source = 'manual'`. Validation failures
raise `HTTPException(400, ...)`. See validation-rules.md
and timestamps.md.
