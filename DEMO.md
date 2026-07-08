# Live demo: progressive disclosure & `/context`

> Same task, same model, same repo — **only the documentation changes.** Watch the
> `/context` number, not the answer.

Two branches hold two versions of the docs:

| Branch | Shape | "Read the README" pulls in |
|--------|-------|----------------------------|
| `fat-readme` | one ~1,700-line `README.md`, everything inlined | **the whole file (~16k tokens)** |
| `progressive` | 39-line `README.md` map + `docs/` tree (4 subdirs, 18 pages) | **map + one page (~0.6k tokens)** |

`main` is the normal repo (neither version) — return here between runs.

## The question to paste (identical on both branches)

```
Using only the README and any page it points to — don't read the source code:
what timestamp formats does BrewOps accept on input, and what format does it
store? Two sentences is fine.
```

- Docs-only (no source) → a clean docs-vs-docs comparison.
- One narrow lookup → on `progressive` the map routes straight to
  `docs/data-model/timestamps.md` and stops (the docs don't cross-link, so nothing
  cascades). On `fat-readme`, "the README" *is* the whole 1,700-line file.

## Running it (use a FRESH Claude Code session per branch)

A warm cache from one run can colour the next, so start each branch clean.

1. `git checkout fat-readme` → open Claude Code → paste the question → let it answer →
   run **`/context`**. Note the Messages number.
2. `git checkout progressive` → **fresh** Claude Code session → paste the same question →
   answer → **`/context`**. Note the Messages number.
3. Compare. Same answer quality; the fat branch spent ~15–16k more tokens to get it.

Return with `git checkout main` when done.

## Why it works (the teaching point)

`README.md` is **not** auto-loaded into context the way `CLAUDE.md` is — the gap appears
because the agent *reads the file to answer the question*. On `fat-readme` that means the
entire manual floods the window; on `progressive` the agent reads a slim map and pulls in
only the one page the task needs. Write docs as a **map, not a dump**: the agent always
reads the index, the detail only when the task calls for it. (This is exactly what Skills
are built on.)

## If the gap ever looks small again

- The progressive agent read **more than one page** → the question was too broad, or a doc
  grew an outbound link. Keep the question narrow; keep `docs/` pages self-contained.
- The fat agent **grepped instead of reading the whole file** → phrase it as "read the
  README", and keep the file just under ~2,000 lines so one Read grabs all of it.
