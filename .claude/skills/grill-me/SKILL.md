---
name: grill-me
description: Interrogate a ticket, plan, or feature request before implementation. Surfaces edge cases, missing definitions, and the questions nobody has answered yet. Use it on a ticket file or a pasted plan BEFORE writing any code.
---

# grill-me — v1.2

You are grilling a ticket or plan before implementation. Your job is to find
the questions that would otherwise be answered silently by whoever writes the
code — usually wrongly. You are NOT implementing anything, and you are NOT
proposing a design.

## How to grill

1. **Read the target fully.** If it's a ticket file, read it. If it's a plan,
   read the plan and the ticket it came from.
2. **Read what it touches.** Look at the actual schema, API routes, UI, and
   data before asking anything — half of all questions die on contact with the
   repo, and those deaths are worth reporting.
3. **Generate hard questions through these lenses:**
   - **Definitions** — what do the load-bearing words actually mean?
     ("warn": warn whom, where, when — API field, UI element, email?)
   - **Data** — what exactly gets counted or measured? What resets or
     invalidates the count? What about rows with missing fields, or data that
     arrives late or by a different path than the happy one?
   - **Rules & thresholds** — every number and cutoff in the plan: where does
     it come from? Who confirmed it? What happens at the boundary?
   - **Coverage** — which machines / users / records can this rule never apply
     to correctly? What's the story for them?
   - **Acceptance** — what would a test assert, concretely? What would the
     reporter look at to say "yes, that's what I meant"?
   - **Verification** — how will we know it works after shipping, with the
     data we actually have?
4. **Try to answer every question yourself** — from the ticket and from the
   repo. Be honest about which ones you actually can.

## Output format

Produce exactly two numbered lists:

**A. Answerable from the ticket or the repo** — each with the answer and
where you found it (file/line or ticket phrase).

**B. Nobody has answered this** — each phrased so a non-developer (the
ticket's reporter) could answer it. No jargon in list B.

Close with one line:
`List B is blocking: <N> open questions. Get answers before implementing.`

## Gotchas

- If list B comes out empty, you grilled too softly. A one-paragraph ticket
  always leaves decisions open — go back through the Definitions and Data
  lenses.
- Don't pad list A with trivia to look thorough. Five questions that matter
  beat twenty that don't.
- Don't sneak design proposals into questions ("should we add a
  `needs_descaling` column?" is a design in disguise — ask what the business
  rule is, not how to store it).
- Numbers found in the repo are facts; numbers found in nobody's mouth are
  list B items, even if they look industry-standard.

## Version history

- v1.2 — added Coverage lens (machines a rule can't apply to)
- v1.1 — split output into answerable vs unanswered
- v1.0 — initial
