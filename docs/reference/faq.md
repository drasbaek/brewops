# Extended FAQ

**Why no login?** The app binds to localhost and is a single-user, fictional-coffee workshop
artifact. Auth would be pure ceremony.

**Why SQLite, not Postgres?** Tiny dataset, single process, one file is the least-effort thing that
fully works. Boring technology is a design principle.

**Why is all the SQL in one file?** So the whole database surface can be read in one place. Need a
new query? Add a function to `queries.py`; never inline SQL in a handler or the loader.

**Why are duration and temperature optional?** Manual entries (especially Old Faithful) often lack
them — a human recording a cup after the fact rarely has a stopwatch reading. Telemetry rows usually
include them.

**Why does `per_drink` include drinks with zero brews?** It is a LEFT JOIN from `drink_types`, so the
dashboard shows the whole menu including drinks nobody ordered recently, rather than silently
omitting them.

**Why does the health card separate last maintenance from recent errors?** A routine descale and an
error code are different things to a person reading the card. Errors surface as a short recent list;
last routine maintenance surfaces as a single event, explicitly excluding error rows.

**Can I change the port?** Yes — edit the `PORT` constant in `api/main.py`. It is intentionally not
an environment variable.

**Can I add a machine or drink?** Yes. Add a row to `MACHINES` or a tuple to `DRINK_TYPES` in
`schema.py`, then re-seed. There is a dedicated `add-drink-type` skill for the drink case.

**Why did my future-dated test row get rejected?** Both write paths refuse times after "now". In a
test, inject a fixed `now` via the ingest layer's `now` parameter to control the threshold.

**Where does manual data come from?** Either the dashboard's log-brew form (→ API) or a `manual_*.csv`
export of Old Faithful's paper log (→ ingest). Both are stored with `source = 'manual'`.

**How do I reset everything?** `uv run seed` drops all tables and rebuilds from `data/inbox/`. It is
destructive of any brew that lives only in the database and not in a CSV.

**Why is ingest additive?** So loading a new monthly export doesn't disturb existing rows. The flip
side: importing the same file twice double-loads it, so ingest each new file exactly once.
