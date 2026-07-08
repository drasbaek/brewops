# Timestamp handling

Timestamps cut across the ingest and API paths. This is the complete picture.

## Canonical storage format

Every timestamp in the database is a **naive local-time string**:

```
YYYY-MM-DD HH:MM:SS      e.g. 2026-07-08 09:41:17
```

No time zone, no `Z`, no offset, no fractional seconds. Used in
`brew_events.timestamp` and `maintenance_events.timestamp`. Every layer normalizes to this
before writing.

## Two paths, two parsers, one output

**Ingest path** — `loader.py`, `_parse_timestamp`. **Strict**: accepts only the canonical
format `%Y-%m-%d %H:%M:%S`. Anything else is rejected with
`unparsable timestamp <value> (expected YYYY-MM-DD HH:MM:SS)`. CSVs are machine-generated
(or careful paper-log exports), so strictness catches upstream corruption early.

**API path** — `api/main.py`, `parse_timestamp`. **Lenient**: tries these in order and the
first that parses wins:

1. `%Y-%m-%d %H:%M:%S` — the canonical log format
2. `%Y-%m-%dT%H:%M:%S` — ISO-ish, `T` separator, with seconds
3. `%Y-%m-%dT%H:%M` — ISO-ish, `T` separator, **no** seconds — what an HTML
   `<input type="datetime-local">` sends, i.e. the dashboard form

Whatever the input, output is normalized to `%Y-%m-%d %H:%M:%S`. If none parse, the API
returns `HTTP 400 unparsable timestamp <value>`.

Why the asymmetry: the API's client is a human in a browser (whose datetime picker omits
seconds), so it accepts that gracefully; the ingest path's clients are files, which should
already be well-formed.

## Future timestamps are rejected

Both paths reject timestamps after "now" — a machine cannot brew a coffee that has not
happened yet, so a future timestamp is certainly a data-entry or clock error.

- **Ingest**: `now` is threaded `ingest_path` → `ingest_file` → `_parse_timestamp`,
  defaulting to `datetime.now()`. Reason: `timestamp <value> is in the future`.
- **API**: `now` is `datetime.now()` at request time. Raises `HTTP 400 timestamp is in the
  future`.

## No time zones, on purpose

The machines, database, and humans are all in one place. Time zones would add real
complexity (conversion, DST edge cases) for zero benefit here.

## `DATE()` grouping

`/api/stats` groups per-day with SQLite's `DATE(timestamp)`, which reads the `YYYY-MM-DD`
prefix directly off the stored string — no conversion needed, because of the single
canonical format.

## Summary

| Aspect           | Ingest path                    | API path                                |
|------------------|--------------------------------|-----------------------------------------|
| Function         | `loader._parse_timestamp`      | `api/main.parse_timestamp`              |
| Accepts          | canonical only                 | canonical + `T`-with-secs + `T`-no-secs |
| Stores           | `YYYY-MM-DD HH:MM:SS`          | `YYYY-MM-DD HH:MM:SS`                   |
| Future timestamp | row rejected, ingest continues | HTTP 400                                |
| "now"            | injected, defaults to `now()`  | `datetime.now()` at request time        |
