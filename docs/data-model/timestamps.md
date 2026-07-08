# Timestamp handling

Everything about timestamp formats, parsing, and rejection lives on this page. You do not
need any other doc to answer a timestamp question.

## Canonical storage format

Every timestamp in the database is a **naive local-time string**, always this exact format:

```
YYYY-MM-DD HH:MM:SS      e.g. 2026-07-08 09:41:17
```

No time zone, no `Z`, no offset, no fractional seconds. Used in both `brew_events.timestamp`
and `maintenance_events.timestamp`. Every path normalizes to this before writing.

## What each path accepts (input)

- **Ingest / CSV path** — **strict**: accepts **only** the canonical `YYYY-MM-DD HH:MM:SS`.
  Anything else is rejected (`unparsable timestamp <value>`).
- **API path** — **lenient**: accepts three formats, first match wins:
  1. `YYYY-MM-DD HH:MM:SS` (canonical)
  2. `YYYY-MM-DDTHH:MM:SS` (`T` separator, with seconds)
  3. `YYYY-MM-DDTHH:MM` (`T` separator, no seconds — what the browser's
     `datetime-local` picker sends)

Whatever the input, both paths **store the canonical `YYYY-MM-DD HH:MM:SS`**. The API is
lenient because its client is a human in a browser; ingest is strict because its clients are
machine-generated files.

## Future timestamps are rejected

Both paths reject any timestamp after "now" — a machine cannot brew a coffee that has not
happened yet. Ingest skips the row and reports `timestamp <value> is in the future`; the API
returns `HTTP 400 timestamp is in the future`.

## No time zones, on purpose

Machines, database, and humans are all in one place, so time zones would add complexity for
zero benefit.
