# Stats & machine health semantics

The exact meaning of the numbers the dashboard shows, from `queries.get_stats` and
`queries.get_machine_health`.

## `get_stats` — the dashboard totals

Returns three things:

- **`total_brews`** — a plain count of every row in `brew_events`, regardless of source.
- **`per_drink`** — a breakdown built with a `LEFT JOIN` **from** `drink_types` **to** `brew_events`,
  grouped by drink. The direction matters: because it starts from the full menu, every drink appears,
  including ones with a count of zero. Ordered by the drink's id so the menu order is stable.
- **`per_day`** — a time series grouped by `DATE(timestamp)`, ordered ascending. `DATE()` simply
  takes the first ten characters of the stored time, which works with no conversion because every
  stored time is in the canonical fixed-width shape.

## `get_machine_health` — one machine's card

Returns the machine's own fields plus:

- **`brew_count`** and **`last_brew`** — a count of the machine's coffees and the time of its most
  recent one.
- **`last_maintenance`** — the single most recent maintenance event **excluding** errors (i.e. the
  most recent `descale` / `refill` / `repair`), or `null` if there is none. Routine upkeep, not
  alarms.
- **`recent_errors`** — up to five most recent `error` rows, newest first, each with its time, error
  code, and note.

Requesting a machine id that does not exist returns `null` from the query, which the API surfaces as
`HTTP 404`. The deliberate separation of routine maintenance from errors reflects how a person reads
the card: "when was this last serviced?" is a different question from "what has been going wrong?"
