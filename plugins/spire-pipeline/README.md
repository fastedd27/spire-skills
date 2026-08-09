# spire-pipeline

**Design it, plan it, build it — with receipts.** Three skills that take a project from vague idea to executed, verified plan across as many Claude sessions as it takes, without losing the plot between them — plus an optional `setup` helper that configures the whole thing in two questions.

Part of the spire-skills collection from The Spire Library (https://thespirelibrary.com).

## What this does, in plain English

- **`design-swarm`** — give it a hard problem and instead of one answer, it generates several competing approaches, each deliberately biased a different way, then attacks them all and hands you the survivors to choose from. Ends with a written design you signed off on. Never builds anything.
- **`run-list`** — turns that design into one planning document: the build broken into ordered work sessions, what depends on what, a ready-to-paste prompt for each, and live status per step. The document *is* the project state — any future session reads it cold and knows exactly where things stand.
- **`conductor`** — executes the plan like a foreman who never touches the tools: collects every decision you'd need to make up front in one sitting (then runs for hours without pinging you), farms each step out to worker agents, and refuses to mark anything done unless a mechanical check proves it happened. A worker saying "finished!" counts for nothing; a file existing with the right contents counts. Anything only you can do lands on a plain-English "here's what I need from you" board instead of the run stalling or the AI guessing.
- **`setup`** (optional) — first-run onboarding: detects what it can about your machine, asks two plain questions, and writes a minimal config. Already configured? It gives you a read-only report of your config against the current key table instead ("check my config"). It never overwrites anything, and you never need it — the pipeline runs fine with no config at all.

Works on anything with 3+ steps — code, documents, content, systems. All state lives in the documents themselves, so a closed laptop resumes exactly where it left off.

**Architecture note ("one engine, two cuts"):** each skill's text never hardcodes an environment — a swappable config layer binds it to yours (annex pattern, same shape as Ari Evergreen Build's swappable domain layer — see Credits & Lineage below, MIT). The authors run the same engine text with their own config; you run it with yours.

## Per-run report

The conductor emits a `<run-list-basename>.report.json` file sibling to the run-list after every summary checkpoint (both interim summaries and the final summary; interim reports are overwritten by the final). This file is machine-readable and carries its own `schema_version` (independent of the plugin's semantic version) together with the engine version and the config version stamped at run time. The full schema and version history are documented in `plugins/spire-pipeline/shared/run-report-schema.md`. Report files are canonical: any aggregation, indexing, or derived reporting layer is built atop them, never as an alternative source.

## Setup

1. Install from the marketplace: `/plugin marketplace add fastedd27/spire-skills` then `/plugin install spire-pipeline@spire-skills`. Or manually: place this folder where your Claude Code/Cowork plugins live. After installing, reload/restart the session so the new skills register.
2. Copy `config/house-config.example.md` to a `house-config.md` kept **OUTSIDE the plugin directory** — your project root or home directory — because the plugin folder is replaced on update and anything stored inside it is lost. For the fill procedure — which keys to set first, the no-clobber copy commands, what's safe to leave at default — follow the example file's own **Quickstart** section rather than filling the whole table by hand. **Config discovery search order (deterministic): (1) project root, (2) home directory; first found wins — project beats home.** The skills load the filled config from wherever that search finds it (each skill's bootstrap line loads it per this README search order); a missing file = every key at its omit-default. Only a key with NO documented default, or an unrecognized/malformed entry, is UNKNOWN = park-and-ask.

   Would rather not fill it by hand at all? `spire-pipeline:setup` is an opt-in convenience skill: it detects what it can, asks only what it can't, writes a minimal config, and never overwrites an existing one — or just follow the Quickstart; both end in the same file.
3. Invoke any stage by name: `design-swarm`, `run-list`, or `conductor` — or by the namespaced form (`spire-pipeline:design-swarm`, `spire-pipeline:run-list`, `spire-pipeline:conductor`). The onboarding helper is `setup` (`spire-pipeline:setup`) — explicit invocation only; `check my config` runs its read-only diff mode against an existing config.
4. Mechanical enforcement (the hooks) requires a working Python — the hook tries `python3`, `python`, then the Windows `py` launcher (the Store's fake python3 stub is detected and skipped); without it the pipeline degrades to the v0.1 prose-only write boundaries — see `hooks/README-hooks.md`.

```
plugin-src/
  hooks/hooks.json                      PreToolUse hook registration
  hooks/path_guard.py                   mechanical path-containment guard
  hooks/gate_brief_guard.py             gate-brief guard — denies a design-swarm
                                        gate ask without a fresh gate brief
                                        (mechanical No Naked Gate backstop)
  hooks/README-hooks.md                 hook behavior + grants file schema
  scripts/probe_runner.py               typed probe runner (closed vocabulary)
  scripts/claim_lock.py                 atomic run-claim lockfile
  skills/design-swarm/SKILL.md          engine (stage 1)
  skills/run-list/SKILL.md              engine (stage 2)
  skills/run-list/assets/template.md
  skills/conductor/SKILL.md             engine (stage 3)
  skills/setup/SKILL.md                 first-run onboarding helper (optional,
                                        explicit-invoke; diff mode on existing
                                        configs — never overwrites)
  shared/pipeline-conventions.md        cross-skill conventions annex (extracted
                                        from the executor's D10; all three
                                        skills point here)
  references/brief-templates.md         decide-once brief template (split-out)
  references/checker-recipes.md         decorrelated-checker recipes (cfg:dispatch.checker_lineage)
  references/instrumentation.md         falsification-test instrumentation notes
  references/lineage.md                 full engine-cut provenance + credits
  references/resume-walkdown.md         resume walkdown reconstruction ordering
  references/swarm-templates.md         design-swarm digest/schema templates
  config/house-config.md                NOT a file here — your filled copy lives OUTSIDE the plugin (Setup step 2); this folder is wiped on update
  config/house-config.example.md        sanitized example for public use
```

## Safety posture

v0.1's write boundaries, probe rules, and trust hierarchy were PROSE-ENFORCED only — interpreted by the executing model, not a sandbox. As of v0.2, a mechanical layer SHIPPED for two of those three: path containment (the PreToolUse guard, `hooks/path_guard.py`, checking every Write/Edit target against the predicted-and-granted staging ring) and probe execution (the typed runner, `scripts/probe_runner.py`, a closed vocabulary replacing free-text shell probes). The prose rules remain in force as the model-side layer underneath both — they are also the ONLY layer in effect when `python3` is not on PATH, since the hooks and scripts require it (see `hooks/README-hooks.md`). That means a misread rule is still a possible outcome, not an impossibility: run the pipeline against working sets you can cheaply restore — a git repo you can reset, a backed-up folder, a scratch copy — not against surfaces where a bad write is unrecoverable. (The pipeline is not code-specific: it builds whatever the run-list names — code, documents, configs, content. The recoverability rule is the same everywhere.) The trust hierarchy (worker-brief provenance suffixes) has no mechanical layer yet. A validating write gateway for canonical intake remains future work — see the WRITE PATH "Future body" in `skills/conductor/SKILL.md`.

**The one-source rule (binding).** The house cut and the public cut build from the SAME engine text. Engine files never state an installation-specific value — they reference named hooks as `` `cfg:<key>` ``, resolved by whichever config file ships in the `config/` slot (`house-config.md` for the house, a user's own copy of the example for everyone else). If an edit ever forces the engine text to diverge between cuts, that is a seam to stop and report, not to fork quietly.

**Config resolution.** No templating engine: the conductor reads the config once at skill load and applies values as prose. **Config discovery search order (deterministic): (1) project root, (2) home directory; first found wins — project beats home.** A key with a documented "Omit →" default uses that default when the key is omitted. Only a key with NO documented default, or an unrecognized/malformed entry, is UNKNOWN = deny-by-default (park and ask).

**Building the cuts.** Both cuts are the SAME shipped engine (`skills/` + `shared/` + the example config); they differ only in which filled `house-config.md` resolves at load time from OUTSIDE the plugin folder:
- House cut: the house's own `house-config.md`, kept at the house's config location outside the repo (a project root or home dir).
- Public cut: an adopter's copy of `config/house-config.example.md`, renamed to `house-config.md` and kept outside the plugin folder.

A real, filled `house-config.md` is never committed to the repo or shipped in the plugin — `config/` ships the example only (and a repo `.gitignore` guards `plugins/*/config/house-config.md` against an accidental commit).

**Sanitization invariant.** Engine files (`skills/`, `shared/`) and the example config carry no installation paths, no host-specific tool names, no internal project/ledger names, no personal names. Public lineage credits (Ari Evergreen Build, MIT) are kept — they are provenance, not residue. The context-pack contract carries its validation record inline — including the honest history of the first gate it failed.

## Credits & Lineage

This pipeline stands on two pieces of borrowed, credited mechanism — the context-pack contract (stage 3) and the brainstorming-swarm adaptation (stage 1). The first, the **context-pack contract** (worker-brief composition — needle taxonomy, provenance suffixes, placement/budget, pointer-vs-gist split, decorrelated back-translation check) used by stage 3, is credited to **Ari Evergreen's Build, MIT license** ([Ari's page — Clief Notes on Skool](https://www.skool.com/cliefnotes)). Its acceptance gate PASSED 2026-08-04 under two independent external model lineages (10/10 corruption types each, zero ID/value misses); the validation record, including the first gate it failed, is kept inline in the conductor skill.md` (D4) until an adopter's own decorrelated acceptance check clears the stated threshold — the banner is kept on purpose, not stripped for a clean release.

The second: Stage 1 (`design-swarm`) is adapted from **Ari Evergreen's `brainstorming-swarm` v1.0.0** ([skool.com/cliefnotes](https://www.skool.com/cliefnotes)) (stage spine, lens set, gates) onto this pipeline's own machinery — see the "Lineage & credits" section at the foot of `skills/design-swarm/SKILL.md` for the itemized carry-over.

Each engine skill in this package carries its own **Lineage & credits** section at its foot recording its house version history and any external provenance:
- `skills/design-swarm/SKILL.md` — brainstorming-swarm lineage + house version log pointer.
- `skills/run-list/SKILL.md` — house version log pointer.
- `skills/conductor/SKILL.md` — context-pack + tiering-rule credits + house version log pointer.
- `skills/setup/SKILL.md` — first cut 2026-08-06 from the onboarding design spec (designed and built with this pipeline's own three stages, dogfooded end-to-end).

Shared cross-skill vocabulary (touch-kinds, tier-role names, verdict grammar, status glyphs, provenance suffixes) is defined once in `shared/pipeline-conventions.md`, which all three skills point at rather than forking locally.

**Instrumentation note.** The falsification-test and vitals lines inside the skills are the authors' own evaluation instrumentation — adopters can ignore them freely.

**Versioning.** The plugin manifest (`.claude-plugin/plugin.json`) uses semver — see `CHANGELOG.md` for the release history. The conductor's own version log (`skills/conductor/SKILL.md`, foot of file) uses semver aligned with the plugin; the design-swarm, run-list, and setup version logs carry the date-based scheme (`vYYYY-MM-DD.N`).

Formerly published internally as build-run-list / run-list-executor.
