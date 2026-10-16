---
name: add-drink-type
description: Add a new supported drink to BrewOps end to end, so it validates on the API, appears in the dashboard dropdowns, and counts in the stats. Use when someone asks to support a new drink (for example "add Flat White").
---

# Add a drink type to BrewOps

BrewOps is database-driven: the list of valid drinks lives in exactly one place,
and the API validation, the dashboard dropdowns, and the stats all read from it.
Adding a drink is a small change, but it must go in the right place and be applied
to the database, or it will silently fail to show up.

## Steps

1. Open `src/brewops/db/schema.py` and find the `DRINK_TYPES` list.
2. Add one tuple, `(name, label)`:
   - `name` is the machine-readable key: lowercase, underscores, no spaces (e.g. `flat_white`).
   - `label` is what people read in the UI (e.g. `Flat White`).
3. Apply the change to the database by reseeding:
   ```
   uv run seed
   ```
4. Verify it end to end — don't assume, check:
   - `uv run start`, then open http://localhost:8123
   - the new drink appears in the "Log a brew" drink dropdown
   - log a brew with it and confirm it shows up in the per-drink stats
5. Report what you changed and the evidence you saw (the drink in the dropdown and in stats).

## Gotchas

- Drinks are defined **only** in `DRINK_TYPES` in `src/brewops/db/schema.py`. Everything
  else (API validation, dropdowns, stats) reads from the database — never hardcode a
  drink anywhere else.
- The edit does nothing until you run `uv run seed`. That step is what writes it to the DB.
- `uv run seed` rebuilds the database from the sample CSVs in `data/inbox/`, so it also
  clears any brews you logged by hand. That's expected.
- `name` is the stable key stored on every brew (`brew_events.drink_type`); `label` is
  display-only. Never rename an existing `name` — it would orphan existing brew rows.

## Version

0.1.0
