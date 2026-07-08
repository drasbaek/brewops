# The frontend

`src/brewops/frontend/` — three files, **no build step**:

- `index.html` — dashboard markup
- `app.js` — fetches the API and renders stats + machine cards (no framework)
- `style.css` — styling (no preprocessor)

Served as-is by FastAPI's `StaticFiles` mount at `/`. To change the dashboard, edit these
files and reload the browser.

## What it calls

Reads: `/api/stats`, `/api/machines`, `/api/machines/{id}`, `/api/drink-types`.
Writes: `POST /api/brews` and `POST /api/maintenance` — the forms a human uses to log
activity for Old Faithful (which has no telemetry). See
[api-layer.md](api-layer.md).
