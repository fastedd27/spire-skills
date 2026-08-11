---
name: design-swarm
description: "(v2026-08-06.1) Run a design swarm: a divergence-first DESIGN pass that fans independent lens agents over a hard problem, competes approaches under different axioms, kills the weak ones at a critique gate, and stops at a written design the operator ratified. Never builds. Trigger on: 'design swarm', 'swarm this design', 'run a design pass on', 'brainstorm swarm', 'swarm the design process', or any ask to design/architect something non-trivial where the operator wants competing options rather than one answer. Do NOT trigger for build/implementation work (that is run-list territory) or quick single-answer questions."
---

<!-- ENGINE FILE — one source, two cuts. Installation-specific values (path
     roots, hooks, governance rule names, reference docs) are referenced
     generically as `cfg:<key>` and resolved by the config layer:
     `config/house-config.md` (house cut) or `config/house-config.example.md`
     (public example). Shared pipeline vocabulary lives in
     `shared/pipeline-conventions.md`. -->

# Design Swarm — divergence-first design pass (stops at written design)

**What this is.** A staged design pass where the main chat stays orchestrator, never doer: independent agents work the problem through fixed lenses and competing axioms, return schema-capped digests only, and the operator holds the two gates. Terminal outcome is a written, defensible design spec landed at a durable host path. **This skill does not build.** Adapted from Ari Leavesley's `brainstorming-swarm` v1.0.0 (stage spine, lens set, gates) onto house machinery and house discipline — comparison record: `cfg:refs.swarm_comparison`.

## Non-negotiables (read before running)

1. **Orchestrator, not doer.** The conductor seat routes briefs out and synthesizes digests in. It does not do lens work inline. If you catch yourself writing a lens analysis in the main context, stop and dispatch it. (Exception: `serial_fallback` — one seat role-plays the legs sequentially under the same schemas and gates; announce the mode in the run record.)
2. **Digests only.** Workers return the named fields below, under the word caps. No raw dumps into the conductor seat. When dispatching via the Workflow/Agent tooling, pass the digest schema as the agent's `schema` so the cap is enforced by the harness, not by politeness. A dump-shaped return gets rejected once with the schema restated; a second failure escalates to the operator. (Schema caps, task widgets, and `phase()`/`log()` are optional conveniences of some runtimes; absent, use plain messages and keep the schemas as text discipline.)
3. **Operator holds the gates.** Gate A and Gate B are hard stops for a human decision (the ratify seam). Never auto-advance through a gate, including in unattended sessions — park at the gate and say what decision is owed.
4. **No Clean Evaluator.** Critique agents are a second read, not an oracle. Critique prices the options; it never picks the winner. The pick is Gate B, operator-only.
5. **Stop at written design.** No code, no file scaffolding, no "quick prototype." Build handoff goes through the `run-list` skill as a separate, operator-initiated act.
6. **Honest mode labels.** Every run declares its execution mode in the spec header: `dispatch` (independent agents actually ran), `serial_fallback` (one seat played the roles in sequence — schemas and gates still hold), or `partial` (name which stages were which). Serial is the floor, never the default; if the harness can fan out, fan out.
7. **Deliverables land durable.** The spec (and the run log if kept) is written via the sanctioned write toolchain (`cfg:write.toolchain`) to the owning project's durable staging path (`cfg:staging.durable_root`, or the project's sanctioned staging path) and file-info-verified before the run is called done. Chat cards are not filing.
8. **Never go dark.** Every fanned stage is observable while it runs — run folder + per-leg tasks + arrival heartbeats per the Observable Dispatch section below. A silent multi-minute fan-out is a defect, not patience.
9. **Gate brief is mechanically enforced.** A naked gate ask (bare widget, no readable brief) is BLOCKED by `hooks/gate_brief_guard.py`: the gate brief must be written to the run folder as the act right before the ask, and rendered in the conversation. Prose was skipped on a live run (2026-08-06); this is the backstop.

## Observable dispatch (liveness — added v2026-08-02.2)

The operator must be able to tell WORKING from STALLED at a glance, without interrupting the run.

- **Run folder first.** Before dispatching S1, create `<durable staging root per cfg:staging.durable_root>/swarm-runs/<YYYY-MM-DD>-<slug>/` and announce the path. Every worker's brief includes: *write your digest to `<run-folder>/<stage>-<leg>.md` as your final act, then return the same content as your reply.* The folder filling up IS the progress bar — and it's crash-safe (file-returns pattern, same rationale as staging results to files as you go: a dead context loses nothing already landed).
- **One task per leg.** At each fan-out, create a task per dispatched leg (e.g. `S1 failure lens`, `S1 precedent lens`) and mark each completed as its digest lands. The task widget then shows k/N movement in real time instead of one long-running stage row.
- **Arrival heartbeats.** As each digest returns, the conductor emits one line — `lens 3/6 landed: constraint — sharpest risk: <8-word gist>` — nothing more (no synthesis mid-stage). Same convention at S2 (approaches) and S3 (critiques).
- **Stall rule.** If a leg shows no file and no task movement for ~10 minutes past its siblings, say so explicitly, and offer the operator a re-dispatch of that leg alone. Never sit silent past a stall, and never silently re-run a leg either — the operator chooses.
- **Workflow-harness runs:** when dispatching via the Workflow tool, use `phase()` per stage and `log()` for the arrival heartbeats so the live progress tree carries the same signal; the run folder rule still applies (workers write files, not just structured returns).

## Stage script

### S0 — Frame (conductor, inline; the only inline stage)

- First: load your filled config (house-config.md — kept OUTSIDE the plugin directory, discovered per the README search order); missing file = every key at its omit-default. State which config resolved as the first line of skill output: `loaded config from <path>`, or `running on omit-defaults` when no file was found.
- State the goal in one sentence and the **hard locks** (constraints that survive no matter what: budget, hardware boundary, frozen contracts, deadlines).
- Bound the context: name the 3–7 sources that matter; do not load more.
- **Comparison Discipline pre-check:** before designing anything new, sweep for an existing surface that already does this (hidden-upgrade check). If the sweep finds a wash, say so and stop — the swarm is not a ritual.
- Output: a one-screen frame block (goal, locks, context list, why-new). **Always show the frame block to the operator before S1 dispatch** — this is a display step, not a third gate. **Hard-stop** (wait for explicit operator confirmation before dispatching S1) only when one or more hard locks were **INFERRED** by the conductor rather than stated by the operator; if every hard lock traces to an operator statement, show the block and proceed straight to S1. Lightweight form only — no full Gate 0, the gates stay exactly two (A and B).
- Create the run folder (Observable Dispatch) and announce its path before dispatching anything. Then write the marker `${CLAUDE_PROJECT_DIR}/.swarm-active.json` = `{"run_folder": "<absolute path to this run's folder>"}` — this arms the gate-brief guard for the run.

### S1 — Discovery (fan the lenses)

Dispatch one agent per lens, each blind to the others, each briefed with ONLY the frame block + its lens charter + the run-folder write instruction. The frame block lists the source NAMES; the precedent lens may additionally be granted read access to those named sources (grant pointers, not prose, so other lenses stay uncontaminated):

| Lens | Charter |
|---|---|
| failure | How does this go wrong? Failure modes, abuse cases, silent-degradation paths, the 2am version of the problem. |
| stakeholder | Who touches this and what does each actually need? Include the future-you who maintains it. |
| constraint | What is genuinely fixed vs assumed-fixed? Price every hard lock; flag fake constraints. |
| temporal | How does this age? 6 weeks, 6 months, 2 years. What decision made now is expensive to reverse? |
| experiential | What is it like to use/operate day-to-day? Friction, cognitive load, the boring Tuesday test. |
| precedent (anti-rebuild lens) | Anti-rebuild sweep: what in the existing stack/knowledge base already solves part of this? Name the artifact and the overlap %. |

**Discovery digest schema (per lens, hard caps):**
- `lens` (name) · `top_findings` (max 5, ≤25 words each) · `sharpest_risk` (≤40 words) · `question_for_operator` (0–1, ≤25 words) · `confidence` (high/med/low).

Conductor synthesizes the six digests into a half-page discovery summary. No new analysis in synthesis.

### Gate A — operator redirect (HARD STOP)

Present the discovery summary + any `question_for_operator` items **as a gate brief in the live conversation** (No Naked Gate — `shared/pipeline-conventions.md`): the summary and each open question rendered readably in the chat/code-window turn BEFORE the approve/redirect ask fires, never collapsed into bare widget option labels. Operator may: redirect (rerun specific lenses with a sharpened frame), add/kill lenses, amend hard locks, or approve. Do not proceed without an explicit approve. **Write this brief to `<run-folder>/gate-A-brief.md` as the act immediately before the ask** (the gate-brief guard blocks the `AskUserQuestion` otherwise), then render the same content in the conversation.

### S2 — Approaches (compete under different axioms)

Dispatch 3 agents (default; 2–4 by problem size), each given the frame + discovery summary + ONE axiom to design under, blind to the other approaches. Pick axioms that genuinely conflict, e.g.: simplest-thing-that-works · optimize-for-the-2-year-self · mechanize-every-invariant · operator-time-is-the-scarcest-resource · buy-don't-build. Tailor per problem. Run-folder + task-per-leg + heartbeat rules apply.

**Approach digest schema (per agent, hard caps):**
- `axiom` · `design_sketch` (≤200 words) · `what_it_sacrifices` (≤50 words) · `hard_lock_compliance` (per-lock: meets/bends/breaks) · `cost_estimate` (build effort + ongoing rent, coarse) · `first_thing_to_fail` (≤30 words).

### S3 — Critique (kill gate, No Clean Evaluator)

Dispatch one critic per approach (fresh agents, not the authors), charter: **try to kill it.** Attack hard-lock compliance, hidden coupling, maintenance rent, and the failure lens's findings. Also ask each critic: what is worth salvaging from this even if the whole dies? Run-folder + task-per-leg + heartbeat rules apply.

**Critique digest schema:** `target_axiom` · `verdict` (kill/keep/salvage) · `kill_reason` (≤50 words, empty if keep) · `salvage` (≤40 words) · `unpriced_risk` (≤30 words).

Conductor assembles the scoreboard: approaches ranked, kills marked with reasons, salvageable parts listed. Ranking = surviving-critique strength (kill/keep/salvage verdicts) plus stated operator weighting — deliberately not a numeric formula. Critique output prices options; it does not choose.

### Gate B — operator picks (HARD STOP, the ratify seam)

Present the scoreboard **as a gate brief in the live conversation** (No Naked Gate — `shared/pipeline-conventions.md`): before the pick is asked, render in the conversation what is being decided, each competing approach by *what it actually is + what it sacrifices + its kill/keep/salvage verdict* (never a bare codename), the ranked recommendation and why it leads, and what the choice makes expensive to reverse. Then ask the pick. Operator picks the winner, or names a hybrid (winner + salvaged parts). Record the chosen option AND a one-line why — this feeds the spec's "why it won" field. Do not proceed without the pick. **Write this scoreboard brief to `<run-folder>/gate-B-brief.md` as the act immediately before the ask** (the gate-brief guard blocks the `AskUserQuestion` otherwise), then render the same content in the conversation.

### S4/S5 — Spec + HALT

Write the design spec from the winning frame — frontmatter (title/project/date/type/status/mode/run_stages/related_ids/ratification) plus a fixed body order: goal + hard locks, chosen approach + why it won, what was killed and why, salvaged elements, design detail, acceptance sketch, known sacrifices, build handoff note.

> Deep material: references/swarm-templates.md (full copy-in spec skeleton)

`status` is the session-input lifecycle field (`live` while this spec is unconsumed input, `consumed` once a run-list session ingests it, with `consumed:`/`remnants:` filled in per the pipeline's session-input-lifecycle convention — see `shared/pipeline-conventions.md`). `ratification` is a separate field recording the Gate B outcome (the design is ratified, independent of whether anything has consumed it yet) — the two never collide: a spec can be ratified and still live, or ratified and consumed.

Land it durable (the owning project's durable staging path per `cfg:staging.durable_root`), file-info-verify, give the operator the host path. The run folder stays as the run's forensic trail (digests + scoreboard); note its path in the spec. Delete `${CLAUDE_PROJECT_DIR}/.swarm-active.json` so the gate-brief guard disarms. **Then halt.** If the operator says "now build it," that is a new act: invoke `run-list` with this spec as input.

## Fallback and scaling

- **No fan-out available** (mobile, degraded session): run `serial_fallback` — same stages, same schemas, same gates, one seat role-playing the legs honestly. Label it. Never claim peer critique that did not happen. Run folder + heartbeats still apply (write each role's digest as you finish it).
- **Small problems:** collapse to 3 lenses (failure, constraint, precedent) + 2 axioms + 1 critic. Say you collapsed it.
- **Follow-up hygiene:** if the design run produces deferred follow-ups, they go to the owning project's follow-up queue per house rules (`cfg:gov.followup_queue` — mint a work-item id only if you are the owning session; otherwise flag it for the owning project).

## Lineage & credits

- **Engine cut 2026-08-04**, derived one-to-one from the house skill v2026-08-04.3. One source, two cuts: house and public builds share this exact engine text and differ ONLY in the config layer. The full house version log (v2026-08-02.1 → v2026-08-04.3, with fold provenance) lives with the house-retained originals (`cfg:refs.version_logs`).
- **Credits:** adapted from **Ari Leavesley's `brainstorming-swarm` v1.0.0** (stage spine S0–S5, five lenses, two gates, mode labels, stop-at-design) onto house machinery: schema-enforced digests, the precedent lens, No-Clean-Evaluator critique, the ratify-seam Gate B, the durable-landing rule, and the run-list handoff. Observable Dispatch (run folders, task-per-leg, heartbeats, the stall rule, "never go dark") folded v2026-08-02.2 after the first live run.
