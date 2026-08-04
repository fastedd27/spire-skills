# Decide-Once Brief Template — full Appendix

<!-- REFERENCE FILE — extracted verbatim from conductor/SKILL.md D3. Read this
     when actually instantiating a decide-once brief at intake; the core D3
     section covers the mechanics (two-tier structure, gate) without the
     copy-in template itself. -->

## Appendix — Decide-Once Brief template (v2 — two-tier structure, ratified 2026-08-04)

The conductor instantiates this at intake, next to the run-list, named `<run-list-stem>-brief-<YYYY-MM-DD>.md`. It is a session-input-lifecycle file: when the run consumes it, flip `status: consumed`, fill `consumed:`, and list `remnants:`.

````markdown
---
type: decide-once-brief
status: live
run_list: <path to the run-list this brief serves>
created: <YYYY-MM-DD>
consumed:
remnants:
---

# Decide-Once Brief — <run-list name>

Answer every ANSWER cell in ONE sitting. `physical` items are scheduled
(return-board card / calendar slot), not answered as text — their ANSWER cell
records the scheduled slot. `deferred-conditional` items appear ONLY where
every branch is enumerated below the row; anything open-ended was
pre-registered as a future park instead and is not in this table.

## Table A — fast lane (low-stakes, default shown)

Diagnosticity-scored below the Table B cutoff: a wrong default here costs
little. One glance, same-default acceptance. No cost-if-wrong column by
design. "default" in an ANSWER cell accepts the default.

| id | touch-kind | item | recommended default | ANSWER |
|----|------------|------|---------------------|--------|
| Q1 | fact-confirm | <the fact to confirm> | <believed value> | |
| Q2 | physical | <the operator action> | <proposed slot> | |

## Table B — must-read lane (cost-if-wrong precedes the default; hard cap ~7 rows)

Every row here scored as discriminating between materially different
downstream actions. The cost-if-wrong column comes BEFORE the default column
— read the risk before the relief. Each row requires a typed ANSWER: a short
factual consequence of the choice, not a bare default-accept. `why` is an
intake-drafted, operator-editable one-clause purpose annotation used for
mid-run contradiction detection. `voids-if / watch-for` is an optional 1–3
item enumerated invalidation list (structural triggers / judgment
trip-wires) — leave blank if none apply. Exceeding ~7 rows is a signal the
intake rubric is over-classifying risk, not a signal to add friction.

| id | touch-kind | item | cost-if-wrong | recommended default | why | voids-if / watch-for | ANSWER (typed consequence) |
|----|------------|------|----------------|---------------------|-----|----------------------|------------------------------|
| Q3 | decision | <the call to make> | <one line> | <default> | <serves purpose Z> | <optional list, or blank> | |
| Q4 | deferred-conditional | <if X then A; if Y then B — closed branch set listed here> | <one line> | <default branch> | <serves purpose Z> | <optional list, or blank> | |

## Discarded questions (diagnosticity triage log)

Every candidate question the intake pass generated but scored below the
diagnosticity cutoff for Table B/A inclusion, so a later miss traces to
"scored and cut" rather than "never asked."

| candidate question | diagnosticity score | why cut |
|---|---|---|
| <question text> | <score> | <one line> |

## Hash recording (the ratify gate)

After ALL ANSWER cells are filled: compute the SHA-256 of this file with the
configured hash tool (`cfg:hooks.hash` — an existing host tool such as
`sha256sum <path>`, or `certutil -hashfile <path> SHA256` on Windows; any
equivalent SHA-256 tool; no new scripts), then record in the run-list
frontmatter:

    brief: <path to this file>
    brief_hash: <first 12 hex chars>
    brief_answered: <YYYY-MM-DD>

No worker dispatch until these three lines exist. On resume, the conductor
RECOMPUTES the brief's hash and compares it to the recorded frontmatter value;
a mismatch = stale-brief park. If any brief answer is later
contradicted by an upstream finding, the affected lane parks as `stale brief` —
this file is never edited mid-run.
````

This file is the split-out template; the conductor core points here.
