# Drink types

Seeded from `DRINK_TYPES` in `schema.py`. Each drink has a machine-readable `name` and a
human-readable `label`.

| name | label |
|------|-------|
| espresso | Espresso |
| lungo | Lungo |
| cappuccino | Cappuccino |
| latte | Latte |
| americano | Americano |
| hot_water | Hot water |

## name vs label

`name` is the stable machine key — it appears in CSVs, the database, and API requests, and
should never change. `label` is display-only and can be adjusted freely. Separating them
lets you rename a drink's display without rewriting historical data.

## Adding a drink

1. Add a `(name, label)` tuple to `DRINK_TYPES` in `schema.py`.
2. `uv run seed` so it lands in the `drink_types` table.
3. The API's `drink_type_exists` check and the dashboard dropdowns pick it up automatically.

There is a dedicated `add-drink-type` skill under `.claude/skills/` that does this end to end.
