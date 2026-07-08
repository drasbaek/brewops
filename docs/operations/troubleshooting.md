# Troubleshooting

**Port already in use.** Something else is on 8123. Stop it, or change `PORT` in
`api/main.py`.

**`seed` says `data/inbox not found`.** You are not in the repo root. `cd` there.

**Rows rejected on ingest.** Read the printed reasons — each names file, line, and cause.
Usual suspects: non-canonical timestamps, unknown drink/machine, non-positive duration. See
validation-rules.md.

**Timestamp rejected on ingest but accepted by the API.** Expected — ingest is strict,
the API is lenient. See timestamps.md.

**`timestamp is in the future`.** Both paths refuse future timestamps. Check the clock/date.
See timestamps.md.

**Foreign key error.** You referenced a machine id or drink name that is not seeded.
Re-seed or fix the reference data.

**Dashboard is blank.** The DB may be empty — run `uv run seed`. Otherwise check the browser
console and server log; the frontend fetches `/api/stats` et al.

**Where is the DB?** `./brewops.db`, or wherever `BREWOPS_DB` points.

**Reset everything.** `uv run seed` drops and rebuilds from `data/inbox/`.
