<!-- Copy this. Rename: <project>-build-sequence-<YYYY-MM-DD>.md. Delete comments as you go.
     STARTING SHAPE, NOT A REQUIRED FORM: add sections the project earns, drop ones that'd
     be empty. Keep the disciplines (verified-only ticks, paste-ready prompts, land durable);
     flex everything else. -->

<!-- OPTIONAL lifecycle frontmatter — only if a later stage (e.g. conductor)
     will consume this doc as its input. Delete if not needed:
---
type: run-list
status: live
consumed:
remnants:
--- -->

# <Project> — Build Sequence & Session Run-List

_Drafted <YYYY-MM-DD> by <owner>. Canonical scope: <thread/ticket ids>.
Contract/spec of record: <path or link>._

## Locked at kickoff
- **Extend-don't-rebuild:** <what exists that we're extending, not rebuilding.>
- **Repo home + where each session runs:** <repo(s); surface per session.>
- **Frozen / do-not-touch:** <interfaces, ports, services, files.>
- **Boundaries:** <hardware/data/business separations never to cross.>
- **Non-negotiable rules:** <privacy, security, safety rules for the whole build.>
- **Versioning + backup:** <git remote, backup coverage — baked in from session 1.>
<!-- OPTIONAL — only if this run-list was built from a design spec (stage 1→2 intake,
     see the skill's "Consuming a design spec" section). Delete if not applicable: -->
- **Do-not-drift (from the design spec's kills):** <approaches the spec explicitly
  ruled out — name them so a downstream session doesn't wander back into a killed
  approach it has no memory of.>

## Dependency graph
```
G0 ─┬─► A1 ─► A2 ─┐
    └─► B1 ───────┴─► INT ─► CLOSE
```

## Session table
<!-- Status: ✅ verified (+commit) / 🟡 in-progress / ⬜ not started /
     🟡 STAGED (pre-executor only: row has been dispatched/staged to a session but
     not yet confirmed in-progress — folds into plain 🟡 in-progress once a session,
     or an executor, is actually running the row; it is not a distinct executor
     state, so don't rely on it surviving a handoff to Stage 3).
     TICK ✅ ONLY ON VERIFIED COMPLETION — never off a session's own report.
     OPTIONAL executor-compatible extension (see "Optional: executor-compatible
     conventions" in the skill, and the shared annex `shared/pipeline-conventions.md`):
     the full glyph set is ⬜ todo / 🟡 claimed(run-id, timestamp)
     / ✅ verified / 🅿 parked / ⛔ failed-flagged; a row may also carry an optional
     [AUTO]/[PARK] write-class tag and an optional verify-probe note (declare it when
     known — see the skill). None of this executor-compatible layer is required.
     OPTIONAL per-row done-when / acceptance note: if this run-list was built from a
     design spec with an acceptance sketch, a row may carry a one-line "Done-when:"
     comment under its prompt (see Paste-ready prompts below) tracing back to that
     sketch instead of re-deriving verification at build time. -->
| # | Session | Type | Tier-role | Open in | Depends on / Status |
|---|---|---|---|---|---|
| **G0** | <bootstrap: repo + structure + contract copy> | <surface> | <mechanical/standard/judgment> | <repo> | ⬜ |
| **A1** | <first real work> | <surface> | <mechanical/standard/judgment> | <repo> | G0 |
| **A2** | <second step of chain A> | <surface> | <tier-role> | <repo> | A1 |
| **B1** | <parallel chain> | <surface> | <mechanical/standard/judgment> | <repo> | G0 |
| **INT** | <end-to-end integration + verify> | <surface> | <mechanical/standard/judgment> | <repo> | A_, B_ |
| **CLOSE** | <mark follow-ups, recap, fold to roadmap> `[PARK]` | <surface> | judgment | <hub> | INT |
<!-- CLOSE is pre-tagged [PARK] above: canonical writes (follow-up queues, recap,
     roadmap fold) are structurally judgment-owned under the house's state-surface
     ownership rule (`cfg:gov.state_ownership_rule`), never AUTO. Retag only if a
     specific build's CLOSE work is genuinely staging-ring only — delete the tag,
     don't just ignore it. -->

## Suggested crank order
`G0` → chains in parallel: **A** `A1 → A2` and **B** `B1` → `INT` → `CLOSE`.

## Paste-ready prompts
<!-- Each must let a FRESH session with no context do the work right: where to
     open, what to read first, exact task, guardrails. Header gets ✅ + commit
     when verified — an optional mirror only: the table's status cell is the
     SINGLE home of row status; ✅ marks on prompt headings are never
     authoritative. -->

### G0 — <bootstrap> (<type> · <tier-role> · <repo>)
```
<Pull/clone first; read the contract at <path>; deliverables; frozen interfaces
to leave alone; commit + push; what to report back.>
```
<!-- OPTIONAL — Done-when / probe (declare when known, see the skill):
     Done-when: <one-line acceptance condition, from the spec's acceptance sketch
     if this run-list has one>. Probe: <file-info check / grep marker / git log / port check>. -->

### A1 — <session> (<type> · <tier-role> · <repo>)
```
<Paste-ready prompt.>
```

### A2 — <second step of chain A> (<type> · <tier-role> · <repo>)
```
<Paste-ready prompt.>
```

## Work-context notes
> **<note>:** <the environment quirk + the workaround. One per line.>
<!-- OPTIONAL — unpriced risks/sacrifices the design spec named but didn't resolve
     (see the skill's "Consuming a design spec" section) land here too, one per line. -->

## Post-MVP operations
- **<auto-start / service>** — <status; install command; who runs it if privileged.>
- **<committed + pushed>** — <commit hash(es) + remote.>
- **<deploy to prod/next env>** — <status; gating decision owed; the command.>

## Return Board (optional — only if rows are stalled on operator input)
<!-- Aggregate stalled/parked asks as short cards: the ask · a minutes estimate ·
     what it unblocks. Delete this section entirely if nothing is stalled. -->
- **<ask>** — <~N min> — unblocks: <what>.

---

_Home: `<durable path — the project's durable staging folder (cfg:staging.durable_root), NOT temp/scratch>`. Update status cells +
prompts as sessions land; at the milestone, fold to roadmap and recap from this file._
