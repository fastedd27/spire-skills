---
name: run-list
description: >-
  (v2026-08-05.1) Plan and drive a multi-session build with a single durable run-list (a "build
  scope checklist" / "build sequence" / "session plan"). Use this WHENEVER a
  build is big enough to span several dependent work sessions and/or more than
  one repo or surface — the moment you'd otherwise start firing off sessions
  ad hoc. Trigger on: "run-list", "build sequence", "session plan", "map out
  the sessions", "break this build into sessions", "how should we sequence
  this", "plan the build", "build scope checklist", or any point where the user
  is about to kick off a large build across work sessions and
  needs the sessions ordered, prompted, and tracked. Also reach for it mid-build
  to log verified completions, capture ops/deploy state, and keep the doc
  posting-ready. Don't wait for the exact word "run-list" — if the work is
  clearly a multi-step build that will outlive one sitting, this is the tool.
---

<!--
  ENGINE FILE — one source, two cuts. Installation-specific values (path roots,
  hooks, governance rule names, reference docs) are referenced generically as
  `cfg:<key>` and resolved by the config layer: `config/house-config.md` (house
  cut) or `config/house-config.example.md` (public example). Shared pipeline
  vocabulary lives in `shared/pipeline-conventions.md`. The copy-in template
  lives at `assets/template.md` beside this file.
  Refresh trigger: change to the run-list disciplines, the section shape, or the
  house patterns it references.
-->

# Build Run-List

## What this is, and why it works

A build run-list is **one durable markdown file** that plans, drives, and logs a
multi-session build. You write it once at kickoff and maintain it as sessions
land. It is the single source of truth for "what are we building, in what order,
and where does each piece stand."

The reason to spend the upfront effort: this one file does four jobs at once.

1. **It plans** — a dependency graph + an ordered session table means you never
   have to re-derive "what's next" or "what's this waiting on."
2. **It drives** — each session carries a *paste-ready prompt*, so a fresh
   work session self-orients from the file instead of you re-explaining
   the seam every time.
3. **It logs** — verified-completion ticks + commit hashes turn the plan into a
   build log as you go, with zero extra writing.
4. **It becomes the artifact** — a finished run-list is clean raw material for a
   session recap *and* a build-in-public post. One writer, many surfaces.

That last point is the whole bet: instead of a plan doc, a progress tracker, a
log, and a write-up as four separate artifacts that drift apart, you keep one
that is always current because you're editing it anyway.

## When to reach for it

Use a run-list when a build is **large enough to outlive one sitting** — roughly:

- more than ~3 dependent sessions, **and/or**
- more than one repo or surface involved (e.g. a backend service + a frontend
  that consume a shared contract).

For a one-session change, skip it — a run-list would be ceremony. The signal is
*dependency and duration*: if you'll need to remember "session B is blocked on
A's commit" across a break, the file earns its keep.

**Before you build the run-list, check what already exists.** The most expensive
mistake in a multi-session build is standing up a new surface when an existing
one could be extended. Spend the first pass asking: is there already a service,
a channel, a component, a contract I should extend rather than rebuild? Fold the
answer into the "locked at kickoff" section so every downstream session inherits
it. (If the project has a formal comparison step, run it here.)

## Let the shape flex with the build

The meta-rule: **the disciplines below are the invariants; the shape is not.**
They hold whatever you're building. Everything else — the sections, the columns,
the graph, the number of chains — is scaffolding. Treat the template as a
starting shape to adapt, never a form to fill. A small single-repo build might be
just a table and five prompts; a cross-team migration might need extra columns or
a per-surface split. Add what the project earns, drop what it doesn't, reorder to
match how the work flows. Infer the shape from the build; don't force the build
into the shape. A run-list padded with ceremony is worse than a lean one — and a
shape that fights the work just gets abandoned. Keep the invariants, flex the rest.

## The disciplines that make it trustworthy (the invariants)

These are the parts people skip, and skipping them is what turns a run-list into
fiction. They hold regardless of the build's shape — they matter more than the
formatting.

**Tick only VERIFIED completions.** A session reporting "done, pushed" is a
claim, not proof — build sessions routinely narrate work that didn't fully land
(a commit that never happened, a file left untracked, a metric that was actually
from a different run). Do not flip a row to done off a report. Flip it when the
owner confirms it, or when you've independently verified it (the commit exists,
the port is listening, the test passed). Until then it's in-progress. A row ticked without a probe
receipt reads as a CLAIM to a later executor session, which may spot-probe it
(see the conductor skill). This one
rule is the difference between a log you can trust and one you can't.

**Every session gets a paste-ready prompt.** The prompt should let a brand-new
session — with none of this conversation's context — do the work correctly.
State where to open it, what to read first (the contract / spec), the exact task,
and the guardrails (what NOT to touch). If you find yourself about to re-explain
the same seam to a second session, that explanation belongs in the prompt.

**Land it durable.** The run-list is worthless if it dies with the session that
made it. Write it to a location that survives — the project's durable folder
(`cfg:staging.durable_root`), not a scratch/temp area that gets wiped. Update it
*in that location* as you go.

**Split a session when its scope shifts** rather than silently redefining it. If
"wire the tools" turns out to be two jobs, make it two rows with two prompts.
Rewriting a row's meaning but leaving its old prompt is how a session ends up
doing the wrong thing.

**Capture operations, not just features.** A build isn't done when the feature
works once — it's done when it survives a reboot, is committed and pushed, and is
deployed where it needs to be. Keep a "post-MVP operations" section for exactly
this (auto-start, backup coverage, prod deploy) so the last mile is tracked.

## Consuming a design spec (stage 1→2 intake)

When this run-list is being built from a design-swarm output (a ratified design
spec — stage 1 of design-swarm → run-list → conductor), the intake
mapping is fixed. Don't re-derive it per build:

- **Hard locks** (the spec's non-negotiables) → copied **verbatim** into
  Locked at kickoff.
- **The kills** (approaches the spec explicitly ruled out) → a **mandatory
  do-not-drift line** in Locked at kickoff, naming what was killed and why. A
  fresh build session has no memory of the design pass and can wander straight
  back into a killed approach if the kill lives only in a spec footnote instead
  of a standing instruction carried into this file.
- **Unpriced risks / sacrifices** the spec named but didn't resolve → work-context
  notes, so a downstream session sees the tradeoff instead of re-discovering it
  mid-build.
- **Salvaged elements** (pieces the spec kept from prior art or a partial build)
  → candidate rows, not a narrative aside.
- **The spec's acceptance sketch** ("how we'll know it works," when the spec has
  one) → per-row done-when / probe notes — see the probe-note upgrade below, so
  verification traces back to the design pass instead of being re-invented at
  build time.
- **Flip the spec's own lifecycle frontmatter** (`live` → `consumed`) once its
  content has been folded into this run-list, naming this run-list as the
  consumer. This is a separate flip from the run-list's own lifecycle — see
  "Optional lifecycle frontmatter" below for who owns that one.

This section is a mapping, not new machinery — every item on the right side of
the arrows above is a place this skill already writes to. It also stays out of
executor-internal territory on purpose: whatever provenance or verification
apparatus a later executor stage runs on top of a finished run-list is that
stage's own contract, not something to import into a spec-intake pass here.

## How to build one

First: load your filled config (house-config.md — kept OUTSIDE the plugin
directory, discovered per the README search order); missing file = every key
at its omit-default. State which config resolved as the first line of skill output: `loaded config from <path>`, or `running on omit-defaults` when no file was found.

Copy the template (`assets/template.md`, beside this file) and fill it in,
in this order. Constraints first (they bound everything), then structure, then
prompts.

1. **Lock the kickoff constraints** — frozen interfaces, hardware/data
   boundaries, privacy rules, repo homes + where each session runs, the
   extend-don't-rebuild decisions from your comparison pass, and (if this run-list
   is built from a design spec) the hard locks and do-not-drift kills carried
   over per "Consuming a design spec" above.
2. **Draw the dependency graph** — a tiny ASCII graph of which sessions depend on
   which and where parallel chains join.
3. **Fill the session table** — one row per session: id, one-line description,
   type (tool/surface), tier-role, where to open, combined depends-on / status cell.
4. **Write a paste-ready prompt per session.**
5. **Add work-context notes** — the environment quirks that will bite (no mic on
   a host, a slow filesystem, a remote operator, a transport that mangles chars).
6. **Add the durable-home footer.**

## Maintaining it during the build

As sessions land: update the status cell (verified / in-progress / staged),
record the commit hash, and note any tail or gotcha. When a session flags
something cross-cutting (a contract change, a new dependency, another project
affected), mark it clearly so it routes to the right owner.

## Closing out

At the milestone, the run-list is your recap source: decisions made, what
completed with proof, what's deferred, the operations state. Fold the outcome
into wherever the project tracks roadmap/next-actions, and run a recap from it.

If job #4 above ("it becomes the artifact") applies to this build, route the
finished run-list toward wherever the project tracks build-in-public / publishing
output before archiving it — a finished run-list that never reaches a reader
stayed a private log, not the artifact it could have been.

**Recap-time hygiene.** If this run-list was built from a design spec, glance
once at recap time for skill-vs-spec drift: has anything in this skill's own
text quietly diverged from what the spec locked, with no addendum recording the
change? On conflict the spec still wins — this line just makes sure someone
actually looks instead of assuming alignment.

## Optional: executor-compatible conventions (Stage 3 handoff)

Everything in this section is OPTIONAL unless marked otherwise. A run-list that
never meets an executor stays fully valid without any of it — the flex-shape
mandate above still holds: these are additions a later stage can consume when
present, never new required ceremony for the run-list on its own. The shared
vocabulary itself (glyphs, tags, grammars, lifecycle frontmatter) is defined
once for the whole pipeline in `shared/pipeline-conventions.md` — this section
describes how a run-list uses it.

**Full status-glyph set.** The base three (✅ verified / 🟡 in-progress / ⬜ not
started) extend to the full executor-compatible set when a row needs it:

    ⬜ todo · 🟡 claimed(run-id, timestamp) · ✅ verified · 🅿 parked · ⛔ failed-flagged

Use 🅿 for a row that's stalled on something outside the session's power to
resolve (an operator decision, a canonical write, a physical action) and ⛔ for
a row that failed and needs a flag. Both are optional additions to the base
three — a run-list with no parks or failures never needs them.

**Optional per-row tags.** Add either or both as a bracketed tag beside a row
when it helps a later executor session classify the row without re-deriving it:

- **write-class** — `[AUTO]` (read/analysis/compute, or writes confined to the
  staging ring) or `[PARK]` (canonical/host/physical/judgment writes). Leave it
  off and an executor treats the row as UNKNOWN = PARK by default — the tag is
  a hint, never a requirement. Note: CLOSE-type rows (recap/follow-up-queue/
  roadmap) are structurally PARK by default — see the template's pre-tagged
  CLOSE row.
- **tier-role** — `mechanical` / `standard` / `judgment`, naming how much
  judgment the row's work needs (never a model name). This is the session
  table's own tier-role column, not just an optional tag — see the template.

**Verify-probe note — declare when known.** For a row where a mechanical check
can confirm the work landed, note the probe next to the row (a file-info check
on the output · grep for a marker string · `git log` commit-exists · a port/HTTP
check) as soon as you know what it is — at kickoff if the spec's acceptance
sketch already names it (see "Consuming a design spec" above), or the moment it
becomes knowable during the build. This is no longer purely optional: leaving it
blank because nobody thought about verification yet is the failure mode this
upgrade closes. Leaving it blank because the row genuinely has no mechanical
check available is still fine. **Stage 3 executes probes through the
conductor's typed probe runner — a closed vocabulary (`file_exists` /
`content_matches` / `commit_exists` / `http_status` / `fixture`,
`scripts/probe_runner.py`) — so declare probes in one of those forms; a
declared probe outside this vocabulary is UNKNOWN = PARK at execution time.**
Pair it with two optional one-line conventions if
the build wants machine-checkable proof instead of a narrated report:

- `[<row-id>-VERDICT] <claimed outcome in one sentence>` — the worker's own
  claim, always a claim, never itself a tick (the "tick only VERIFIED
  completions" invariant above still governs — a verdict alone never flips a
  row).
- a one-line verification receipt appended once the probe has actually been
  run and passed.

**RETURN BOARD (optional section stub).** For a build where in-progress rows
routinely stall on operator input, add a `## Return Board` section that
aggregates those asks as short cards — each ≤3 plain-English lines: the ask,
a minutes estimate, and what answering it unblocks — topped by a short resume
brief. Skip this section entirely on a build with no stalls to aggregate. Any card that asks the operator to CHOOSE between options carries the gate-brief shape (No Naked Gate — `shared/pipeline-conventions.md`): each option named by what it is plus its tradeoff, a recommendation, and reversibility, surfaced in the conversation rather than pointing at a file.

**Optional lifecycle frontmatter.** A run-list that will be consumed by a later
stage can carry session-input-lifecycle frontmatter at its top: `type:
run-list`, `status: live|consumed`, `consumed:` (date + what consumed it),
`remnants:` (forwarding ledger, or "none"). Skip it on a run-list that's just
for you. When this run-list does reach an executor, the executor owns flipping
this field's `live` → `consumed`, in the same act as writing its RUN SUMMARY —
this skill only offers the field; it never flips its own lifecycle mid-build.

**Stage 3: handing to the executor.** When a finished (or in-progress) run-list
needs to actually be *run* — dispatched, verified row by row, checkpointed and
handed back clean — that is a separate skill, `conductor`, consuming
this document as its input. None of the above is required to reach that stage;
it simply reads more of the run-list's built-in signal when it's there. Full
contract: the executor design spec of record (`cfg:refs.executor_spec`).

## Lineage

- **Engine cut 2026-08-04**, derived one-to-one from the house skill
  v2026-08-04.2. One source, two cuts: house and public builds share this exact
  engine text and differ ONLY in the config layer. The full house version log
  (v2026-08-02.1 → v2026-08-04.2, with fold provenance) lives with the
  house-retained originals (`cfg:refs.version_logs`).
