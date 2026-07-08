# Validation & rejection rules

Both write paths enforce the same rules. Failure reporting differs: ingest skips-and-records
the row; the API returns HTTP 400.

| Rule | Ingest reason | API error |
|------|---------------|-----------|
| Machine must exist | `unknown machine_id <id>` | `400 unknown machine_id <id>` |
| `machine_id` integer (ingest) | `bad machine_id <value>` | — |
| Drink type must exist (brews) | `unknown drink <value>` | `400 unknown drink_type <value>` |
| Numeric fields parse (ingest brews) | `bad numeric fields duration_s=… temp_c=…` | — |
| Duration > 0 (ingest brews) | `non-positive duration_s <value>` | — |
| Maintenance type valid | `unknown maintenance type <value>` | `400 unknown maintenance type <value>` |
| Timestamp parses & not future | see [timestamps.md](../data-model/timestamps.md) | see [timestamps.md](../data-model/timestamps.md) |
| Unrecognized filename (ingest) | recorded in `skipped_files` | — |

Maintenance types: `descale`, `refill`, `repair`, `error`. Manual brews are always stored
with `source = 'manual'`.
