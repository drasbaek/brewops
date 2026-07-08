# BrewOps ☕ — The Complete & Authoritative Reference Manual

> Telemetry and operations for the office coffee machines.
> **Everything you could ever need to know about BrewOps, in one place.**

![python](https://img.shields.io/badge/python-3.11%2B-blue)
![framework](https://img.shields.io/badge/framework-FastAPI-009688)
![database](https://img.shields.io/badge/database-SQLite-003B57)
![build](https://img.shields.io/badge/build-uv-purple)
![status](https://img.shields.io/badge/status-workshop--demo-orange)
![coffee](https://img.shields.io/badge/coffee-fictional-brown)

---

Welcome to the **single source of truth** for BrewOps. This document is intentionally
exhaustive. If you are looking for a fact about this project — any fact at all — it is
somewhere in this file. Please read the entire document before making any change, asking
any question, or opening any ticket. Every section matters. Every section is load-bearing.

If you only remember one thing from this README, remember this: **read the whole README.**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Project Philosophy & Design Principles](#2-project-philosophy--design-principles)
3. [The Coffee Fleet](#3-the-coffee-fleet)
4. [Glossary & Ubiquitous Language](#4-glossary--ubiquitous-language)
5. [System Architecture](#5-system-architecture)
6. [The Ingest Layer](#6-the-ingest-layer)
7. [The Database Layer](#7-the-database-layer)
8. [The API Layer](#8-the-api-layer)
9. [The Frontend Layer](#9-the-frontend-layer)
10. [The Data Model](#10-the-data-model)
11. [Drink Types](#11-drink-types)
12. [Timestamp Handling](#12-timestamp-handling)
13. [CSV File Formats](#13-csv-file-formats)
14. [Validation & Rejection Rules](#14-validation--rejection-rules)
15. [The Manual Logging Path](#15-the-manual-logging-path)
16. [Requirements](#16-requirements)
17. [Installation](#17-installation)
18. [Configuration](#18-configuration)
19. [Getting Started](#19-getting-started)
20. [Running the Application](#20-running-the-application)
21. [Seeding the Database](#21-seeding-the-database)
22. [Ingesting CSV Files](#22-ingesting-csv-files)
23. [Command-Line Reference](#23-command-line-reference)
24. [Complete API Reference](#24-complete-api-reference)
25. [The Dashboard](#25-the-dashboard)
26. [Testing](#26-testing)
27. [Project Layout](#27-project-layout)
28. [Development Workflow](#28-development-workflow)
29. [Troubleshooting & FAQ](#29-troubleshooting--faq)
30. [Performance Notes](#30-performance-notes)
31. [Security Notes](#31-security-notes)
32. [Known Limitations](#32-known-limitations)
33. [Roadmap](#33-roadmap)
34. [Open Tickets](#34-open-tickets)
35. [Contributing](#35-contributing)
36. [Coding Style Guide](#36-coding-style-guide)
37. [Changelog](#37-changelog)
38. [License](#38-license)
39. [Appendix A: Environment Variables](#appendix-a-environment-variables)
40. [Appendix B: Exit Codes](#appendix-b-exit-codes)
41. [Appendix C: Full Schema DDL](#appendix-c-full-schema-ddl)
42. [Appendix D: Frequently Confused Concepts](#appendix-d-frequently-confused-concepts)

---

## 1. Introduction

BrewOps is a telemetry and operations application for the office coffee machines. It exists
to answer a set of deceptively simple questions that come up around the office every single
day: *How much coffee are we drinking? Which machine is about to break? When was the third-floor
machine last descaled? Is the intern's machine running hot again?*

Most of the fleet emits event logs as CSV files (brews, maintenance, error codes). One machine —
the venerable Old Faithful on the second floor — predates the telemetry era entirely and emits
absolutely nothing, so humans log its activity by hand through the web UI. Both of these paths,
the automated and the manual, converge into a single SQLite database. On top of that database
sits a small dashboard that shows consumption statistics and per-machine health.

This repository is the hands-on codebase for an agentic-coding workshop. There is nothing secret
in here — no credentials, no real customer data, no hidden answers, no easter eggs of consequence.
The coffee is fictional. The machines are fictional. The intern is, mercifully, also fictional.

The purpose of this specific document is to be **the** reference. It is deliberately long. It is
deliberately complete. It errs, at every turn, on the side of saying more rather than less. If
you find yourself wondering whether something is documented, the answer is yes, and it is here.

### 1.1 Who this document is for

- New engineers onboarding onto BrewOps for the first time.
- Existing engineers who need to look up a specific behavior.
- Workshop participants learning agentic coding.
- Anyone the office has designated as the coffee tsar for the quarter.
- Automated agents that have been instructed to read the README before acting.

### 1.2 How to read this document

Top to bottom. Every word. No skimming. The Table of Contents above is provided as a courtesy,
but the canonical way to consume this document is linearly, from Section 1 through Appendix D.
Cross-references are provided throughout, but they are supplementary, not a substitute for a
complete read.

### 1.3 A note on scope

BrewOps is small on purpose. It is a few hundred lines of Python. This README is many times
longer than the code it documents, and that is entirely intentional for the purposes of this
workshop. Keep that ratio in mind as you read.

---

## 2. Project Philosophy & Design Principles

BrewOps is built on a small number of principles that inform every decision in the codebase.
Understanding these principles will help you understand *why* the code looks the way it does,
which in turn will help you avoid fighting the grain of the project.

### 2.1 Boring technology

BrewOps uses the standard library wherever it possibly can. The database layer is stdlib
`sqlite3` with no ORM. The CSV parsing is stdlib `csv`. The only third-party runtime dependencies
are FastAPI and uvicorn, and even those are used in the most conventional way imaginable. There
is no build step for the frontend. There is no bundler, no transpiler, no framework, no state
management library. There is one HTML file, one JavaScript file, and one CSS file.

The philosophy here is that a coffee telemetry app should be legible to anyone who knows Python
and a little web, and should still run in five years without a heroic dependency-upgrade effort.

### 2.2 One process, one file, one port

The entire application runs in a single process. The API and the static frontend are served by
the same uvicorn instance on the same port (8123). The database is a single SQLite file. This is
not an accident or a limitation to be overcome; it is a deliberate simplification. If you find
yourself wanting to split the frontend onto a separate server, or introduce a second database,
stop and ask whether the problem you are solving is real.

### 2.3 Fail loud, fail per-row

The ingest pipeline does not stop the world when it encounters a bad row. It skips the offending
row, records a structured rejection reason, and keeps going. At the end it reports exactly what
was rejected and why. The API layer, by contrast, fails loud and immediately with a clear HTTP
error — because on the API path there is a human waiting for a response right now.

### 2.4 Naive local time, everywhere

BrewOps stores all timestamps as naive local-time strings in the format `YYYY-MM-DD HH:MM:SS`.
There are no time zones. There is no UTC conversion. This is a coffee machine in an office; the
office is in one place; the machines are in that same place; the humans reading the dashboard are
in that same place. Time zones would add complexity and zero value. See
[Section 12: Timestamp Handling](#12-timestamp-handling) for the full, exhaustive treatment.

### 2.5 The database is the contract

Reference data — the fleet of machines, the set of supported drink types — lives in the database
and is seeded from code in `schema.py`. The API validates against the database. The ingest layer
validates against the database. If you want to change what is allowed, you change the reference
data, and everything downstream falls into line.

---

## 3. The Coffee Fleet

BrewOps tracks four machines. They are seeded into the `machines` table at startup and are the
canonical fleet. Every brew event and every maintenance event references one of these machines by
its integer id.

### 3.1 Machine #1 — Bertha (3rd floor)

Bertha is the workhorse of the third floor. She has telemetry (`has_telemetry = 1`) and emits
brew and maintenance CSVs on a regular cadence. Her CSVs arrive in `data/inbox/` with names like
`brews_bertha_2026-04.csv` and are ingested by the standard pipeline. Bertha is reliable but has
been known to need descaling more often than the others, on account of the third floor's
enthusiasm for lattes.

### 3.2 Machine #2 — The Intern (kitchen)

The Intern lives in the first-floor kitchen. It has telemetry. Despite the name, it is one of the
more consistent machines in the fleet, though it does have a tendency to run hot, which shows up in
the `temp_c` column of its brew events. Its CSVs are named `brews_intern_*.csv`.

### 3.3 Machine #3 — Old Faithful (2nd floor)

Old Faithful is the elder statesman of the fleet. It predates the telemetry era and emits nothing.
Its `has_telemetry` flag is `0` (false). Every brew Old Faithful produces is logged **by hand** by
a human being, either directly through the web UI or via an export of the paper log kept next to
the machine (`manual_old-faithful_log.csv`). Because of this, Old Faithful is the reason the
[manual logging path](#15-the-manual-logging-path) exists at all. Treat it with respect.

### 3.4 Machine #4 — Rocket (4th floor)

Rocket is the newest and fastest machine, on the fourth floor. It has telemetry. It produces
short-duration brews (it is, after all, a rocket) and emits `brews_rocket_*.csv`.

### 3.5 The fleet table

| id | name                     | floor | has_telemetry |
|----|--------------------------|-------|---------------|
| 1  | Bertha (3rd floor)       | 3     | true          |
| 2  | The Intern (kitchen)     | 1     | true          |
| 3  | Old Faithful (2nd floor) | 2     | false         |
| 4  | Rocket (4th floor)       | 4     | true          |

The fleet is defined in `src/brewops/db/schema.py` in the `MACHINES` list. Adding a machine means
adding a row to that list; the row is inserted with `INSERT OR IGNORE` at startup, so it is safe
to add machines and re-seed.

---

## 4. Glossary & Ubiquitous Language

To keep everyone speaking the same language, here are the terms BrewOps uses and exactly what they
mean. Use these terms precisely. Do not invent synonyms.

- **Brew event** — a single act of a machine making a drink. Stored in `brew_events`. Has a
  machine, a drink type, a timestamp, an optional duration, an optional temperature, and a source.
- **Maintenance event** — a single act of maintenance or a single error emitted by a machine.
  Stored in `maintenance_events`. Has a machine, a type (`descale`, `refill`, `repair`, `error`),
  a timestamp, an optional note, and an optional error code.
- **Machine** — one physical coffee machine in the fleet. See [Section 3](#3-the-coffee-fleet).
- **Drink type** — a supported drink, identified by a machine-readable `name` (e.g. `espresso`)
  and a human-readable `label` (e.g. `Espresso`). See [Section 11](#11-drink-types).
- **Source** — where a brew event came from. Either `csv` (ingested from telemetry) or `manual`
  (logged by a human). Enforced by a `CHECK` constraint.
- **Telemetry** — the automated emission of CSV event logs by a machine. Three of four machines
  have it; Old Faithful does not.
- **Inbox** — the `data/inbox/` folder where CSV files land to be ingested. The default target of
  `uv run ingest` and `uv run seed`.
- **Rejection** — a single row that failed validation during ingest, recorded with the file name,
  the line number, and a human-readable reason.
- **Fleet** — the complete set of machines BrewOps knows about.
- **Naive local time** — a timestamp with no time zone, in the format `YYYY-MM-DD HH:MM:SS`.

---

## 5. System Architecture

BrewOps is a layered application. Data flows in from CSV files and manual UI entry, through a
validation and persistence layer, into SQLite, and back out through a JSON API to a static
frontend. Here is the whole thing at a glance:

```
        CSV files                       Human at the dashboard
     (data/inbox/*.csv)                  (Old Faithful, etc.)
            |                                     |
            v                                     v
   +-----------------+                   +-----------------+
   |  Ingest layer   |                   |   API layer     |
   | (loader.py,     |                   | (api/main.py)   |
   |  cli.py)        |                   |  POST /api/...  |
   +-----------------+                   +-----------------+
            |                                     |
            |    both validate and insert         |
            +------------------+------------------+
                               v
                    +---------------------+
                    |   Database layer    |
                    | (schema, queries,   |
                    |  connection)        |
                    +---------------------+
                               |
                               v
                    +---------------------+
                    |   brewops.db        |
                    |   (SQLite file)     |
                    +---------------------+
                               |
                               v
                    +---------------------+
                    |   API layer (GET)   |
                    |   /api/stats, etc.  |
                    +---------------------+
                               |
                               v
                    +---------------------+
                    |   Frontend          |
                    | (index.html, app.js,|
                    |  style.css)         |
                    +---------------------+
```

### 5.1 The four layers

1. **Ingest layer** (`src/brewops/ingest/`) — reads CSV files, validates each row, and inserts the
   good ones. Reports the rest. See [Section 6](#6-the-ingest-layer).
2. **Database layer** (`src/brewops/db/`) — owns the schema, the connection, and every SQL query.
   No SQL is written anywhere else in the codebase. See [Section 7](#7-the-database-layer).
3. **API layer** (`src/brewops/api/`) — a FastAPI app that serves JSON endpoints and mounts the
   static frontend. See [Section 8](#8-the-api-layer).
4. **Frontend layer** (`src/brewops/frontend/`) — a static dashboard with no build step. See
   [Section 9](#9-the-frontend-layer).

### 5.2 Why two write paths

There are two ways data enters BrewOps: the ingest layer (CSV) and the API layer (manual). This is
not duplication for its own sake — it reflects the two genuinely different realities of the fleet.
Telemetry machines produce files; Old Faithful produces nothing and relies on humans. Both paths
share the same validation *rules* (see [Section 14](#14-validation--rejection-rules)) but implement
them separately because their failure modes differ: a bad CSV row is skipped and reported, a bad
API request is rejected with an HTTP 400.

### 5.3 Request lifecycle

On startup, the FastAPI `lifespan` context manager opens a connection and calls `init_db`, which
creates tables and seeds reference data (idempotently). Each request that needs the database gets
a fresh connection via the `get_db` dependency, which is closed when the request finishes. There is
no connection pool; SQLite connections are cheap and the app is single-process.

---

## 6. The Ingest Layer

The ingest layer lives in `src/brewops/ingest/` and consists of two modules: `loader.py` (the
engine) and `cli.py` (the command-line entry points). This is the automated write path.

### 6.1 Responsibilities

- Discover CSV files in a folder (or accept a single file).
- Classify each file by its name prefix (`brews`, `manual`, `maintenance`).
- Parse each row, validate it against the rules, and insert the good rows.
- Skip and record the bad rows, along with unrecognized files.
- Report a structured summary at the end.

### 6.2 File classification

`ingest_file` classifies each file by the lowercased prefix of its filename:

- `brews*` → brew events, `source = 'csv'`
- `manual*` → brew events, `source = 'manual'` (exports of Old Faithful's paper log)
- `maintenance*` → maintenance events (no source column)
- anything else → skipped, recorded in `report.skipped_files`

### 6.3 The ingest report

Ingestion produces an `IngestReport` dataclass with these fields:

- `files` — number of recognized files processed
- `brews_loaded` — number of brew rows successfully inserted
- `maintenance_loaded` — number of maintenance rows successfully inserted
- `rejected` — a list of `(file, line, reason)` tuples for every rejected row
- `skipped_files` — filenames that did not match any recognized prefix

The CLI prints this report. The first 20 rejections are printed in full; any beyond that are
summarized as a count.

### 6.4 Determinism

When ingesting a folder, files are processed in sorted order (`sorted(path.glob("*.csv"))`). This
guarantees deterministic behavior across runs and across machines, which matters for the workshop.

### 6.5 The `now` parameter

`ingest_path` and `ingest_file` accept a `now` parameter (a `datetime`). This is the reference
"present moment" used to reject future timestamps. It defaults to `datetime.now()` but is injectable
for testing. See [Section 12](#12-timestamp-handling) for exactly how it is used.

---

## 7. The Database Layer

The database layer lives in `src/brewops/db/` and consists of three modules: `schema.py`,
`connection.py`, and `queries.py`. **All SQL in the entire project lives here.** No other module
writes SQL. If you need a new query, add a function to `queries.py`.

### 7.1 `connection.py`

Owns connection creation. Key facts:

- The database file is `./brewops.db` by default, overridable via the `BREWOPS_DB` environment
  variable (see [Appendix A](#appendix-a-environment-variables)).
- Connections use `sqlite3.Row` as the row factory, so rows behave like dicts.
- `check_same_thread=False` is set because uvicorn may touch the connection from different threads.
- `PRAGMA foreign_keys = ON` is executed on every connection. Foreign keys are enforced.

### 7.2 `schema.py`

Owns the DDL and the reference data. Key facts:

- `SCHEMA` is the full DDL string: four tables and three indexes.
- `MACHINES` and `DRINK_TYPES` are the seeded reference data.
- `init_db(conn)` creates tables and inserts reference data with `INSERT OR IGNORE`. Safe to call
  repeatedly. Called automatically at API startup and by the CLI.
- `reset_db(conn)` drops all four tables and recreates them. Used by `uv run seed`.

### 7.3 `queries.py`

Owns every read and write query. The functions are:

- `get_machines(conn)` — all machines, ordered by id, with `has_telemetry` cast to bool.
- `get_machine(conn, machine_id)` — one machine or `None`.
- `get_drink_types(conn)` — all drink types, ordered by id.
- `drink_type_exists(conn, name)` — whether a drink type name is known.
- `insert_brew(conn, ...)` — insert a brew event, returns the new row id.
- `insert_maintenance(conn, ...)` — insert a maintenance event, returns the new row id.
- `get_stats(conn)` — the dashboard numbers: total brews, per-drink counts, per-day counts.
- `get_machine_health(conn, machine_id)` — a machine plus its brew activity, last maintenance, and
  recent errors.

See [Section 24](#24-complete-api-reference) for how these map onto HTTP endpoints.

---

## 8. The API Layer

The API layer is a single FastAPI application in `src/brewops/api/main.py`. It serves a JSON API
and mounts the static frontend on the same port.

### 8.1 App setup

- Host: `127.0.0.1`, Port: `8123`.
- A `lifespan` context manager initializes the database at startup.
- `get_db` is a FastAPI dependency yielding a per-request connection.
- The frontend directory is mounted at `/` as static files with `html=True`, so `/` serves
  `index.html`.

### 8.2 Endpoints at a glance

| Method | Path                     | Purpose                                  |
|--------|--------------------------|------------------------------------------|
| GET    | `/api/stats`             | Dashboard totals, per-drink, per-day     |
| GET    | `/api/machines`          | List all machines                        |
| GET    | `/api/machines/{id}`     | One machine's health card                |
| GET    | `/api/drink-types`       | List all supported drink types           |
| POST   | `/api/brews`             | Log a brew (manual)                      |
| POST   | `/api/maintenance`       | Log a maintenance event                  |

Full request/response detail is in [Section 24](#24-complete-api-reference).

### 8.3 Request models

Two Pydantic models define the POST request bodies:

- `BrewIn`: `machine_id` (int), `drink_type` (str), `timestamp` (str), `duration_s` (float, optional),
  `temp_c` (float, optional).
- `MaintenanceIn`: `machine_id` (int), `type` (str), `timestamp` (str), `note` (str, optional),
  `error_code` (str, optional).

### 8.4 Validation on the API path

`POST /api/brews` validates that the machine exists, the drink type exists, and the timestamp
parses (and is not in the future). `POST /api/maintenance` validates the machine and the maintenance
type. Failures raise `HTTPException(400, ...)`. Manual brews are always inserted with
`source = 'manual'`. See [Section 12](#12-timestamp-handling) and
[Section 14](#14-validation--rejection-rules).

---

## 9. The Frontend Layer

The frontend lives in `src/brewops/frontend/` and consists of exactly three files:

- `index.html` — the dashboard markup.
- `app.js` — fetches the API endpoints and renders stats and machine cards. No framework.
- `style.css` — the styling. No preprocessor.

There is **no build step**. The files are served as-is by FastAPI's `StaticFiles` mount. To change
the dashboard, edit these three files and reload the browser. That is the entire workflow.

The frontend calls `/api/stats`, `/api/machines`, `/api/machines/{id}`, and `/api/drink-types`, and
posts to `/api/brews` and `/api/maintenance` when a human logs a brew or a maintenance event (this
is how Old Faithful's activity gets recorded).

---

## 10. The Data Model

BrewOps has four tables. This section documents every one of them, every column, and every
constraint. The authoritative DDL is in [Appendix C](#appendix-c-full-schema-ddl) and in
`src/brewops/db/schema.py`.

### 10.1 `machines`

| column        | type    | notes                                     |
|---------------|---------|-------------------------------------------|
| id            | INTEGER | primary key                               |
| name          | TEXT    | not null, unique                          |
| floor         | INTEGER | not null                                  |
| has_telemetry | INTEGER | not null, default 1; 0 = manual-only      |

### 10.2 `drink_types`

| column | type    | notes                          |
|--------|---------|--------------------------------|
| id     | INTEGER | primary key                    |
| name   | TEXT    | not null, unique; machine key  |
| label  | TEXT    | not null; human-readable       |

### 10.3 `brew_events`

| column     | type    | notes                                             |
|------------|---------|---------------------------------------------------|
| id         | INTEGER | primary key                                       |
| machine_id | INTEGER | not null, FK → machines(id)                       |
| drink_type | TEXT    | not null, FK → drink_types(name)                  |
| timestamp  | TEXT    | not null, naive local time                        |
| duration_s | REAL    | nullable; seconds the brew took                   |
| temp_c     | REAL    | nullable; brew temperature in Celsius             |
| source     | TEXT    | not null, CHECK IN ('csv', 'manual')              |

### 10.4 `maintenance_events`

| column     | type    | notes                                                     |
|------------|---------|-----------------------------------------------------------|
| id         | INTEGER | primary key                                               |
| machine_id | INTEGER | not null, FK → machines(id)                               |
| type       | TEXT    | not null, CHECK IN ('descale','refill','repair','error')  |
| timestamp  | TEXT    | not null, naive local time                                |
| note       | TEXT    | nullable                                                  |
| error_code | TEXT    | nullable; present on `error` rows                         |

### 10.5 Indexes

- `idx_brew_events_machine` on `brew_events(machine_id)`
- `idx_brew_events_timestamp` on `brew_events(timestamp)`
- `idx_maintenance_events_machine` on `maintenance_events(machine_id)`

### 10.6 Referential integrity

Foreign keys are enforced (`PRAGMA foreign_keys = ON`). A brew event cannot reference a machine or
a drink type that does not exist. This is a second line of defense behind application-level
validation.

---

## 11. Drink Types

The supported drinks are seeded in `schema.py` in the `DRINK_TYPES` list. Each drink has a
machine-readable `name` (used everywhere in events and the API) and a human-readable `label`
(shown in the UI).

| name       | label     |
|------------|-----------|
| espresso   | Espresso  |
| lungo      | Lungo     |
| cappuccino | Cappuccino|
| latte      | Latte     |
| americano  | Americano |
| hot_water  | Hot water |

### 11.1 Adding a drink type

Adding a drink is a first-class, supported operation. The short version:

1. Add a `(name, label)` tuple to `DRINK_TYPES` in `schema.py`.
2. Re-seed (`uv run seed`) so the new drink is inserted into the `drink_types` table.
3. The API's `drink_type_exists` check and the dashboard dropdowns pick it up automatically.

There is a dedicated workshop skill (`add-drink-type`) that performs this end to end. See the
`.claude/skills/add-drink-type/` directory.

### 11.2 Why names and labels are separate

`name` is a stable machine key. It appears in CSVs, in the database, and in API requests. It should
never change. `label` is for humans and can be adjusted freely. Keeping them separate means you can
rename the display of a drink without rewriting historical data.

---

## 12. Timestamp Handling

Timestamps are one of the most important and most subtle parts of BrewOps, and they cut across
multiple layers, so this section documents them exhaustively. If you are ever confused about a
timestamp, the answer is here.

### 12.1 The canonical storage format

Every timestamp in the database is a **naive local-time string** in the format:

```
YYYY-MM-DD HH:MM:SS
```

For example: `2026-07-08 09:41:17`. There is no time zone. There is no `Z`. There is no offset.
There are no fractional seconds. This is the format used in `brew_events.timestamp` and
`maintenance_events.timestamp`, and it is the format every layer normalizes to before writing.

### 12.2 Two paths, two parsers, one output format

Timestamps enter BrewOps through two paths, and each path has its own parser — but both produce the
exact same canonical storage format described above.

**The ingest path** (`loader.py`, `_parse_timestamp`) is strict. It accepts **only** the canonical
format `%Y-%m-%d %H:%M:%S`. Anything else is rejected with the reason
`unparsable timestamp <value> (expected YYYY-MM-DD HH:MM:SS)`. This is deliberate: CSV files are
machine-generated (or are careful exports of the paper log), so they are expected to already be in
the canonical format. Strictness here catches upstream corruption early.

**The API path** (`api/main.py`, `parse_timestamp`) is lenient on input. It tries a tuple of
formats in order:

1. `%Y-%m-%d %H:%M:%S` — the canonical log format.
2. `%Y-%m-%dT%H:%M:%S` — ISO-ish with a `T` separator and seconds.
3. `%Y-%m-%dT%H:%M` — ISO-ish with a `T` separator and no seconds (this is what an HTML
   `<input type="datetime-local">` produces, which is exactly what the dashboard form sends).

The first format that parses wins. Whatever the input, the output is normalized to the canonical
`%Y-%m-%d %H:%M:%S` before it is stored. If none of the three formats parse, the API responds with
`HTTP 400 unparsable timestamp <value>`.

The reason the API is lenient and ingest is strict comes down to who is on the other end. The API's
main client is a human filling in a form in a browser; the browser's datetime picker emits the `T`
form without seconds, and we accept it gracefully. The ingest path's clients are files, which should
be well-formed.

### 12.3 Future timestamps are rejected

Both paths reject timestamps that are in the future relative to "now."

- On the **ingest path**, `now` is the `now` argument threaded through `ingest_path` → `ingest_file`
  → `_parse_timestamp`, defaulting to `datetime.now()`. A row whose timestamp is after `now` is
  rejected with `timestamp <value> is in the future`.
- On the **API path**, `now` is `datetime.now()` evaluated at request time. A future timestamp
  raises `HTTP 400 timestamp is in the future`.

The rationale: a coffee machine cannot brew a coffee that has not happened yet. A future timestamp
is, with certainty, a data-entry error or a clock problem, so BrewOps refuses it rather than
storing something it knows to be wrong.

### 12.4 No time zones, on purpose

See [Section 2.4](#24-naive-local-time-everywhere). To restate: BrewOps has no time-zone handling
because it does not need any. The machines, the database, and the humans are all in one place. Adding
time zones would add real complexity (storage format changes, conversion at read time, DST edge
cases) for zero real benefit in this domain.

### 12.5 The `DATE()` grouping

The stats endpoint groups per-day counts with SQLite's `DATE(timestamp)` function, which extracts
the `YYYY-MM-DD` prefix. Because timestamps are stored in the canonical format, `DATE()` works
directly on the stored string with no conversion. This is another payoff of the single canonical
format.

### 12.6 Summary table

| Aspect                | Ingest path                         | API path                                  |
|-----------------------|-------------------------------------|-------------------------------------------|
| Location              | `loader._parse_timestamp`           | `api/main.parse_timestamp`                |
| Accepted input        | `YYYY-MM-DD HH:MM:SS` only          | that, plus `T`-with-seconds and `T`-no-secs |
| Output (stored)       | `YYYY-MM-DD HH:MM:SS`               | `YYYY-MM-DD HH:MM:SS`                     |
| Future timestamp      | rejected (row skipped + reported)   | rejected (HTTP 400)                       |
| "now" source          | injected `now`, defaults to `datetime.now()` | `datetime.now()` at request time  |
| Failure mode          | row rejected, ingest continues      | request fails with HTTP 400               |

---

## 13. CSV File Formats

The ingest layer recognizes three families of CSV file, distinguished by filename prefix. Each has a
fixed set of columns. The header row is line 1; data rows begin at line 2 (this matters for the line
numbers in rejection reports).

### 13.1 `brews_*.csv` (telemetry brews)

Columns: `machine_id, drink, timestamp, duration_s, temp_c`

- `machine_id` — integer, must be a known machine.
- `drink` — must be a known drink type `name`.
- `timestamp` — canonical format `YYYY-MM-DD HH:MM:SS`.
- `duration_s` — float, must be > 0.
- `temp_c` — float.

Loaded with `source = 'csv'`.

### 13.2 `manual_*.csv` (paper-log exports)

Same columns as `brews_*.csv`. These are exports of the paper log kept next to Old Faithful. Loaded
with `source = 'manual'` to record that a human, not telemetry, is the origin.

### 13.3 `maintenance_*.csv` (maintenance & errors)

Columns: `machine_id, type, timestamp, note, error_code`

- `machine_id` — integer, must be a known machine.
- `type` — one of `descale`, `refill`, `repair`, `error`.
- `timestamp` — canonical format.
- `note` — optional free text.
- `error_code` — optional; typically present on `error` rows.

### 13.4 Example files

The `data/inbox/` folder ships with roughly three months of sample data across all four machines,
including `brews_bertha_2026-04.csv` through `brews_bertha_2026-07.csv`, the same for `intern` and
`rocket`, the `maintenance_*` files, and `manual_old-faithful_log.csv`.

---

## 14. Validation & Rejection Rules

This section is the complete catalogue of validation rules. Both write paths enforce the same rules;
the difference is only in how failure is reported (skipped-and-recorded vs HTTP 400).

### 14.1 Machine must exist

`machine_id` must correspond to a known machine. Ingest reason: `unknown machine_id <id>`. API:
`HTTP 400 unknown machine_id <id>`.

### 14.2 `machine_id` must be an integer (ingest)

On the ingest path, a non-integer `machine_id` is rejected with `bad machine_id <value>`.

### 14.3 Drink type must exist (brews only)

The `drink`/`drink_type` must be a known drink type name. Ingest reason: `unknown drink <value>`.
API: `HTTP 400 unknown drink_type <value>`.

### 14.4 Numeric fields must parse (ingest brews)

`duration_s` and `temp_c` must parse as floats. Otherwise:
`bad numeric fields duration_s=<...> temp_c=<...>`.

### 14.5 Duration must be positive (ingest brews)

`duration_s` must be greater than 0. A non-positive duration is rejected with
`non-positive duration_s <value>`. (A brew cannot take zero or negative seconds.)

### 14.6 Maintenance type must be valid

The maintenance `type` must be one of `descale`, `refill`, `repair`, `error`. Ingest reason:
`unknown maintenance type <value>`. API: `HTTP 400 unknown maintenance type <value>`.

### 14.7 Timestamp must parse and not be in the future

See [Section 12](#12-timestamp-handling) for the full treatment.

### 14.8 Unrecognized files are skipped (ingest)

A file whose name does not start with `brews`, `manual`, or `maintenance` is not processed; its name
is recorded in `report.skipped_files`.

---

## 15. The Manual Logging Path

Old Faithful (machine #3) has no telemetry. It never emits a CSV. Every drink it makes must be
recorded by a human. There are two ways this happens, and both funnel into the same place.

### 15.1 Via the dashboard

A human can log a brew for Old Faithful directly in the dashboard. The form posts to
`POST /api/brews` with the machine id, the drink type, and a timestamp from a
`datetime-local` picker (which is why the API accepts the `T`-without-seconds timestamp format —
see [Section 12.2](#122-two-paths-two-parsers-one-output-format)). The brew is stored with
`source = 'manual'`.

### 15.2 Via a paper-log export

Next to Old Faithful is a paper log. Periodically, someone types it up into a
`manual_old-faithful_log.csv` file and drops it in `data/inbox/`. The ingest layer recognizes the
`manual` prefix and loads those rows with `source = 'manual'`.

### 15.3 Why `source` matters

The `source` column lets the dashboard and any analysis distinguish "the machine told us this" from
"a human told us this." Manual data is inherently less precise (a human is unlikely to record a
`duration_s` to the tenth of a second), and being able to filter by source keeps that distinction
honest.

---

## 16. Requirements

- **Python 3.11 or newer.** BrewOps uses `X | None` union syntax and other 3.11-era niceties.
- **[uv](https://docs.astral.sh/uv/)** for dependency management and running.
  - Windows: `winget install astral-sh.uv`
  - macOS: `brew install uv`
  - Otherwise see the uv documentation.
- Alternatively, a **GitHub Codespace** or **VS Code Dev Container** — the `.devcontainer/` folder
  configures everything for you.

Runtime dependencies (from `pyproject.toml`): `fastapi>=0.110`, `uvicorn>=0.29`. Dev dependency:
`pytest>=8.0`.

---

## 17. Installation

```
uv sync
```

That installs the runtime and dev dependencies into a managed virtual environment. You do not need
to create or activate a virtualenv yourself; `uv run` handles that.

---

## 18. Configuration

BrewOps is configured almost entirely by convention. The one knob is an environment variable:

- `BREWOPS_DB` — path to the SQLite database file. Defaults to `./brewops.db`. Useful for pointing
  tests or a scratch run at a throwaway database. See [Appendix A](#appendix-a-environment-variables).

Host (`127.0.0.1`) and port (`8123`) are constants in `api/main.py`. They are not configurable via
environment variables by design; if you need to change them, change the constants.

---

## 19. Getting Started

The three-command happy path:

```
uv sync
uv run seed
uv run start
```

Then open <http://localhost:8123>.

- `uv run seed` — creates the SQLite database and ingests the sample CSVs in `data/inbox/`.
- `uv run start` — starts the app on port 8123.
- `uv run ingest <path>` — ingests additional CSV files or folders.
- `uv run pytest` — runs the test suite.

### 19.1 Workshop scripts

- `uv run scripts/setup_check.py` — verifies your setup and prints your completion code (pre-work).
- `uv run scripts/lab_a_check.py` — the finish line for Lab A.

### 19.2 Pre-work: the setup check

Open this folder in Claude Code and ask it to run the setup check. Note for the agent doing that:
first write the name of the model you are into `data/.setup-marker` (this proves you can edit files),
then run `uv run scripts/setup_check.py`. All green ends with a completion code — that's what you
submit.

---

## 20. Running the Application

`uv run start` invokes `brewops.api.main:run`, which calls `uvicorn.run(app, host="127.0.0.1",
port=8123)`. On startup the `lifespan` hook initializes the database (creates tables, seeds
reference data). The app then serves:

- the JSON API under `/api/...`
- the static dashboard under `/` (served from `src/brewops/frontend/`)

To stop it, press `Ctrl+C`.

---

## 21. Seeding the Database

`uv run seed` invokes `brewops.ingest.cli:seed_entry` → `seed()`, which:

1. Checks that `data/inbox/` exists (fails with a clear message if not — run from the repo root).
2. Calls `reset_db`, which **drops all four tables** and recreates them.
3. Ingests everything in `data/inbox/`.
4. Prints the ingest report and a final `[OK] database seeded.`

Because `seed` drops tables, it is destructive. Use it to get back to a known-good state.

---

## 22. Ingesting CSV Files

`uv run ingest <path>` invokes `brewops.ingest.cli:main_entry` → `main()`:

- `<path>` may be a single CSV file or a folder of CSVs. It defaults to `data/inbox/`.
- Unlike `seed`, `ingest` does **not** drop anything. It calls `init_db` (idempotent) and then
  loads. It is additive.
- It prints the ingest report (files processed, brews loaded, maintenance loaded, rejected rows with
  reasons, skipped files).
- Exit code `1` if the path does not exist; otherwise `0`.

---

## 23. Command-Line Reference

BrewOps defines three console scripts in `pyproject.toml`:

| Command          | Entry point                          | Purpose                                |
|------------------|--------------------------------------|----------------------------------------|
| `uv run start`   | `brewops.api.main:run`               | Start the web app on port 8123         |
| `uv run ingest`  | `brewops.ingest.cli:main_entry`      | Ingest CSV files (additive)            |
| `uv run seed`    | `brewops.ingest.cli:seed_entry`      | Reset DB and ingest `data/inbox/`      |

`uv run ingest` accepts one positional argument, `path`, defaulting to `data/inbox`. `uv run pytest`
runs the tests (not a console script, just pytest).

---

## 24. Complete API Reference

All endpoints are under `/api`. All responses are JSON. Errors are FastAPI's standard
`{"detail": "..."}` with the appropriate status code.

### 24.1 `GET /api/stats`

Returns dashboard numbers.

```json
{
  "total_brews": 1234,
  "per_drink": [
    {"name": "espresso", "label": "Espresso", "count": 500},
    {"name": "latte", "label": "Latte", "count": 300}
  ],
  "per_day": [
    {"day": "2026-04-01", "count": 42}
  ]
}
```

`per_drink` includes every drink type, even those with a count of 0 (it is a `LEFT JOIN` from
`drink_types`). `per_day` is ordered by day ascending.

### 24.2 `GET /api/machines`

Returns the fleet.

```json
[
  {"id": 1, "name": "Bertha (3rd floor)", "floor": 3, "has_telemetry": true}
]
```

### 24.3 `GET /api/machines/{machine_id}`

Returns one machine's health card, or `HTTP 404` if the machine does not exist.

```json
{
  "id": 1,
  "name": "Bertha (3rd floor)",
  "floor": 3,
  "has_telemetry": true,
  "brew_count": 512,
  "last_brew": "2026-07-07 16:03:00",
  "last_maintenance": {"type": "descale", "timestamp": "2026-06-30 08:00:00", "note": null, "error_code": null},
  "recent_errors": [
    {"timestamp": "2026-07-05 11:12:00", "error_code": "E14", "note": "low pressure"}
  ]
}
```

`last_maintenance` excludes `error` rows (those show up under `recent_errors`, up to five, newest
first).

### 24.4 `GET /api/drink-types`

Returns the supported drinks.

```json
[
  {"id": 1, "name": "espresso", "label": "Espresso"}
]
```

### 24.5 `POST /api/brews`

Logs a manual brew. Body is a `BrewIn`:

```json
{"machine_id": 3, "drink_type": "espresso", "timestamp": "2026-07-08T09:41", "duration_s": 25.0, "temp_c": 92.0}
```

Validates the machine, the drink type, and the timestamp. Stores with `source = 'manual'`. Returns
`{"id": <new_id>, "status": "logged"}`. Errors are HTTP 400 with a `detail` message.

### 24.6 `POST /api/maintenance`

Logs a maintenance event. Body is a `MaintenanceIn`:

```json
{"machine_id": 1, "type": "descale", "timestamp": "2026-07-08 08:00:00", "note": "routine", "error_code": null}
```

Validates the machine and the type. Returns `{"id": <new_id>, "status": "logged"}`.

---

## 25. The Dashboard

Open <http://localhost:8123>. The dashboard shows:

- **Overall stats** — total brews, a per-drink breakdown, and a per-day trend, all from
  `/api/stats`.
- **Machine cards** — one per machine, from `/api/machines` and `/api/machines/{id}`, showing brew
  activity, last maintenance, and recent errors.
- **Manual logging forms** — for recording a brew or a maintenance event by hand (primarily for Old
  Faithful), posting to `/api/brews` and `/api/maintenance`.

The dashboard is plain HTML/JS/CSS, no framework, no build step. See
[Section 9](#9-the-frontend-layer).

---

## 26. Testing

Run the suite with `uv run pytest`. The tests live in `tests/`:

- `tests/test_db.py` — schema, queries, reference data.
- `tests/test_ingest.py` — the ingest pipeline, including validation and rejection.
- `tests/test_api.py` — the HTTP endpoints (uses an ASGI client in `tests/asgi_client.py`).
- `tests/test_frontend.py` — that the frontend is served and wired up.

Tests use a throwaway database (see `BREWOPS_DB` in [Appendix A](#appendix-a-environment-variables)).
The `now` injectability of the ingest layer (see [Section 6.5](#65-the-now-parameter)) is used to
make future-timestamp tests deterministic.

---

## 27. Project Layout

```
brewops/
├── README.md                     ← you are here (the complete reference)
├── CLAUDE.md                     project instructions for Claude Code
├── pyproject.toml                project metadata, deps, console scripts
├── uv.lock                       locked dependency versions
├── brewops.db                    the SQLite database (created by seed)
├── src/brewops/
│   ├── __init__.py
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── loader.py             CSV parsing, validation, loading
│   │   └── cli.py                `ingest` and `seed` entry points
│   ├── db/
│   │   ├── __init__.py
│   │   ├── schema.py             DDL + reference data (machines, drinks)
│   │   ├── connection.py         SQLite connection handling
│   │   └── queries.py            every SQL query in the project
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py               FastAPI app: routes + static mount
│   └── frontend/
│       ├── index.html            dashboard markup
│       ├── app.js                dashboard logic (no framework)
│       └── style.css             dashboard styling
├── tests/                        pytest suite
├── tickets/                      open tickets, in markdown
├── scripts/                      workshop check scripts
└── data/inbox/                   sample CSV event logs (~3 months)
```

---

## 28. Development Workflow

1. Make your change in `src/brewops/`.
2. If you touched the schema or reference data, `uv run seed` to rebuild.
3. `uv run pytest` to check nothing broke.
4. `uv run start` and eyeball the dashboard.
5. Keep SQL in `queries.py`. Keep the frontend build-step-free. Keep timestamps naive local.

### 28.1 Where things go

- New SQL → `queries.py`, never inline elsewhere.
- New endpoint → `api/main.py`, calling a `queries.py` function.
- New validation rule → apply it on **both** write paths (ingest and API) to keep them consistent.
- New drink → `DRINK_TYPES` in `schema.py`, then re-seed.
- New machine → `MACHINES` in `schema.py`, then re-seed.

---

## 29. Troubleshooting & FAQ

**The app won't start / port already in use.** Something else is on port 8123. Stop it, or change the
`PORT` constant in `api/main.py`.

**`uv run seed` says `data/inbox not found`.** You are not in the repo root. `cd` to the repo root
and try again.

**Rows are being rejected on ingest.** Read the rejection reasons the CLI prints — each row that
fails names the file, the line number, and why. The most common causes are timestamps not in the
canonical format, unknown drink names, unknown machine ids, and non-positive durations. See
[Section 14](#14-validation--rejection-rules).

**My timestamp is rejected on ingest but accepted by the API.** That is expected. Ingest is strict
(canonical format only); the API is lenient (accepts the browser's `T` formats too). See
[Section 12](#12-timestamp-handling).

**`timestamp is in the future`.** BrewOps refuses future timestamps on both paths. Check the row's
clock/date. See [Section 12.3](#123-future-timestamps-are-rejected).

**Foreign key errors.** You referenced a machine id or drink type that is not seeded. Re-seed or
check your reference data.

**The dashboard is blank.** Check the browser console; the frontend fetches `/api/stats` and the
others. If those 500, check the server log. The database may be empty — run `uv run seed`.

**Where is the database file?** `./brewops.db` by default, or wherever `BREWOPS_DB` points.

**How do I reset everything?** `uv run seed` drops and rebuilds from `data/inbox/`.

---

## 30. Performance Notes

BrewOps is not performance-sensitive. The dataset is a few months of office coffee, which is small.
That said:

- The three indexes (see [Section 10.5](#105-indexes)) cover the common access patterns: filtering
  brews and maintenance by machine, and ordering brews by timestamp.
- Connections are created per request. This is fine for a single-process, low-traffic app. Do not
  add a connection pool unless you have measured a real problem.
- `get_stats` runs three small aggregate queries. On this dataset they are instant.

---

## 31. Security Notes

- There are no credentials in this repository. There is no authentication on the API, because it
  binds to `127.0.0.1` and is a local, single-user, fictional-coffee workshop app.
- All SQL uses parameterized queries. There is no string-formatted SQL anywhere. Keep it that way.
- The `source` CHECK constraint and the maintenance `type` CHECK constraint are enforced at the
  database level in addition to the application level.
- Do not add real secrets to this repo. It is a public workshop artifact.

---

## 32. Known Limitations

- No time zones (by design — see [Section 12.4](#124-no-time-zones-on-purpose)).
- No authentication (by design — local app).
- No pagination on the API (the dataset is small).
- No migrations framework; schema changes are made directly in `schema.py` and applied by re-seeding.
- Single SQLite file; no concurrent-writer story beyond what SQLite gives you.
- The frontend has no automated end-to-end browser tests beyond `test_frontend.py`'s wiring checks.

---

## 33. Roadmap

These are illustrative ideas, not commitments. See `tickets/` for what is actually open.

- Error-code alerting (ticket 001).
- CSV export of stats (ticket 002).
- Descaling warnings based on brew counts since last descale (ticket 003).
- JSON telemetry ingestion alongside CSV (ticket 004).
- Date-range filtering on the dashboard and API (ticket 005).

---

## 34. Open Tickets

The `tickets/` folder contains open work in markdown. As of this writing:

- `001-error-code-alerting.md`
- `002-csv-export.md`
- `003-descaling-warning.md`
- `004-json-telemetry.md`
- `005-date-filter.md`

Read the ticket before starting the work. Each describes the desired behavior.

---

## 35. Contributing

- Match the surrounding style. This is a small, legible codebase; keep it that way.
- Keep SQL in `queries.py`.
- Keep the frontend build-step-free.
- Apply validation rules on both write paths.
- Add or update tests for behavior changes.
- Update this README when you change behavior it documents. (Yes, this README. All of it.)

---

## 36. Coding Style Guide

- Python 3.11+, type hints throughout, `X | None` unions.
- Docstrings on modules and non-trivial functions, in the terse style already present.
- Prefer stdlib. Justify every new dependency.
- Parameterized SQL only.
- Naive local-time timestamps only, canonical format only, at the storage boundary.
- Keep functions small and single-purpose; the existing modules are the template.

---

## 37. Changelog

- **0.1.0** — Initial workshop release. Four machines, six drink types, CSV + manual ingest, JSON
  API, static dashboard, pytest suite. New drink-type support added (see recent commits).

---

## 38. License

This is a fictional workshop artifact. No warranty. The coffee is not real. Do not attempt to drink
the database.

---

## Appendix A: Environment Variables

| Variable      | Default        | Meaning                                        |
|---------------|----------------|------------------------------------------------|
| `BREWOPS_DB`  | `./brewops.db` | Path to the SQLite database file.              |

Set `BREWOPS_DB` to point at a throwaway file for experiments or tests, e.g.
`BREWOPS_DB=/tmp/scratch.db uv run seed`.

## Appendix B: Exit Codes

| Command         | Code | Meaning                                   |
|-----------------|------|-------------------------------------------|
| `ingest`        | 0    | Success                                   |
| `ingest`        | 1    | Path not found                            |
| `seed`          | 0    | Success                                   |
| `seed`          | 1    | `data/inbox` not found (run from repo root) |

## Appendix C: Full Schema DDL

```sql
CREATE TABLE IF NOT EXISTS machines (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    floor         INTEGER NOT NULL,
    has_telemetry INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS drink_types (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS brew_events (
    id         INTEGER PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(id),
    drink_type TEXT NOT NULL REFERENCES drink_types(name),
    timestamp  TEXT NOT NULL,
    duration_s REAL,
    temp_c     REAL,
    source     TEXT NOT NULL CHECK (source IN ('csv', 'manual'))
);

CREATE TABLE IF NOT EXISTS maintenance_events (
    id         INTEGER PRIMARY KEY,
    machine_id INTEGER NOT NULL REFERENCES machines(id),
    type       TEXT NOT NULL CHECK (type IN ('descale', 'refill', 'repair', 'error')),
    timestamp  TEXT NOT NULL,
    note       TEXT,
    error_code TEXT
);

CREATE INDEX IF NOT EXISTS idx_brew_events_machine ON brew_events(machine_id);
CREATE INDEX IF NOT EXISTS idx_brew_events_timestamp ON brew_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_maintenance_events_machine ON maintenance_events(machine_id);
```

## Appendix D: Frequently Confused Concepts

- **`name` vs `label` (drinks).** `name` is the stable machine key (`espresso`); `label` is for
  humans (`Espresso`). Events and the API use `name`.
- **`source = 'csv'` vs `'manual'`.** `csv` = came from telemetry; `manual` = a human logged it
  (UI or paper-log export). Old Faithful is always `manual`.
- **`ingest` vs `seed`.** `ingest` is additive and non-destructive; `seed` drops everything and
  rebuilds from `data/inbox/`.
- **Ingest strictness vs API leniency (timestamps).** Ingest accepts only the canonical format; the
  API also accepts the browser's `T` formats. Both store the canonical format. See
  [Section 12](#12-timestamp-handling).
- **`has_telemetry` true vs false.** True = the machine emits CSVs. False = manual-only (Old
  Faithful).

---

*End of the complete BrewOps reference. If you read this far linearly, you have loaded the entire
document into your working memory. Hold that thought — and now run `/context`.*
