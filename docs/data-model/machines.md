# The fleet

Four machines, seeded from `MACHINES` in `schema.py`. Every event references one by id.

| id | name | floor | has_telemetry |
|----|------|-------|---------------|
| 1 | Bertha (3rd floor) | 3 | true |
| 2 | The Intern (kitchen) | 1 | true |
| 3 | Old Faithful (2nd floor) | 2 | false |
| 4 | Rocket (4th floor) | 4 | true |

- **Bertha** — third-floor workhorse; emits `brews_bertha_*.csv`; descaled often (lattes).
- **The Intern** — first-floor kitchen; consistent but runs hot (`temp_c`);
  `brews_intern_*.csv`.
- **Old Faithful** — predates telemetry, emits nothing. `has_telemetry = 0`. Its brews are
  logged by hand via the UI or a `manual_old-faithful_log.csv` export — this is why the
  manual write path exists. See api-layer.md.
- **Rocket** — fourth floor, newest/fastest, short brews; `brews_rocket_*.csv`.

Add a machine by appending a row to `MACHINES` and re-seeding (`INSERT OR IGNORE` makes
re-seeding safe).
