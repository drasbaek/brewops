# Design decisions (ADRs)

Short records of the choices that shape the codebase.

**ADR-001 — Store times as naive local-time strings.** Accepted. The single-location domain makes
time zones pure overhead, and the fixed-width canonical shape sorts and groups as plain text.
(Full detail lives in the data-model timestamps page.)

**ADR-002 — Two separate write paths sharing documented rules.** Accepted. Files and browser
requests have different failure semantics; unifying the code would force one model onto the other.
The shared rules are documented centrally to prevent drift.

**ADR-003 — Per-request connections, no pool.** Accepted. Local SQLite connections are cheap and the
workload is tiny; a pool would add thread-safety questions for no benefit.

**ADR-004 — All SQL in `queries.py`.** Accepted. Centralizing the database surface makes data
interaction legible from one file and keeps handlers thin.

**ADR-005 — No frontend build step.** Accepted. Three static files served verbatim are legible to
anyone and will still run in years without a toolchain upgrade.

**ADR-006 — Reference data seeded from code with `INSERT OR IGNORE`.** Accepted. Makes
initialization idempotent and keeps the canonical fleet and menu in version control beside the schema.

**ADR-007 — Boring technology by default.** Accepted. Standard-library `sqlite3` and `csv`, FastAPI
used conventionally, no ORM, no bundler, no state library. The bar for any new dependency is a real
problem it solves.
