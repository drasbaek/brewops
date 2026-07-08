# Configuration

BrewOps is configured by convention. One knob:

| Variable | Default | Meaning |
|----------|---------|---------|
| `BREWOPS_DB` | `./brewops.db` | Path to the SQLite database file |

Point it at a throwaway file for experiments or tests:

```
BREWOPS_DB=/tmp/scratch.db uv run seed
```

Host (`127.0.0.1`) and port (`8123`) are constants in `src/brewops/api/main.py`, not env
vars by design. Change the constants if you need different values.
