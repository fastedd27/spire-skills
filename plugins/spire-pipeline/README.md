# spire-pipeline

**Design it, plan it, build it — with receipts.** Four skills that take a project from a vague idea to an executed, verified plan across as many Claude sessions as it takes, without losing the plot between them.

Part of the [spire-skills](../../README.md) collection from [The Spire Library](https://thespirelibrary.com).

## What it does, in plain English

- **`design-swarm`** — give it a hard problem and, instead of one answer, it generates several competing approaches, each deliberately biased a different way, then attacks them all and hands you the survivors to choose from. Ends with a written design you signed off on. Never builds anything.
- **`run-list`** — turns that design into one planning document: the build broken into ordered work sessions, what depends on what, a ready-to-paste prompt for each, and live status per step. The document *is* the project state — any future session reads it cold and knows exactly where things stand.
- **`conductor`** — executes the plan like a foreman who never touches the tools. It collects every decision you'd need to make up front in one sitting (then runs for hours without pinging you), farms each step out to worker agents, and refuses to mark anything done unless a mechanical check proves it happened. A worker saying "finished!" counts for nothing; a file existing with the right contents counts. Anything only you can do lands on a plain-English "here's what I need from you" board instead of the run stalling or the AI guessing.
- **`setup`** *(optional)* — first-run onboarding: detects what it can about your machine, asks two plain questions, and writes a minimal config. You never need it — the pipeline runs fine with no config at all.

Works on anything with 3+ steps — code, documents, content, systems. All state lives in the documents themselves, so a closed laptop resumes exactly where it left off.

## First run — start here

**You can use the pipeline immediately, with zero configuration.** Every config key has a documented safe default, and each skill prints `running on omit-defaults` as its first line so you always know when that's what's happening. Just talk to it:

- *"design swarm this problem…"* → runs `design-swarm`
- *"map out the sessions for this build"* → runs `run-list`
- *"execute the run-list"* → runs `conductor`

**When you want finished work landing somewhere durable of your own choosing,** give it a config. Two ways, same result:

1. **Say `setup`** (the `spire-pipeline:setup` skill). It detects what it can about your machine (OS, hash tool, whether the session can fan work out), asks just two plain questions — *where should finished work live?* and *config per-project or machine-wide?* — and writes a minimal `house-config.md` for you. It never overwrites an existing config; re-run it on a configured machine (or say `check my config`) and it gives you a read-only report instead.
2. **Do it by hand** — copy [`config/house-config.example.md`](config/house-config.example.md) and follow its **Quickstart** section (three keys, copy-paste commands per OS).

Either way, the config file lives **outside the plugin folder** (your project root or home directory) — the plugin folder is wiped on every update, so anything stored inside it is lost.

> **Where config is found (deterministic):** (1) project root, then (2) home directory — first found wins, so a project config beats a home one. A missing file means every key runs at its documented default. Only a key with *no* default, or a malformed entry, is treated as unknown and triggers park-and-ask.

## Install & update

From the marketplace:

```
/plugin marketplace add fastedd27/spire-skills
/plugin install spire-pipeline@spire-skills
```

Then **open a fresh session** so the skills and hooks register. See the [collection README](../../README.md#install) for desktop/GUI install and update mechanics.

**Mechanical enforcement (the hooks) needs a working Python.** The hook tries `python3`, `python`, then the Windows `py` launcher (the Microsoft Store's fake `python3` stub is detected and skipped). Without Python, the pipeline degrades to prose-only write boundaries — see [`hooks/README-hooks.md`](hooks/README-hooks.md).

## Invoking the skills

Invoke any stage by name — `design-swarm`, `run-list`, `conductor`, `setup` — or by the namespaced form (`spire-pipeline:design-swarm`, etc.). `setup` is explicit-invocation only; `check my config` runs its read-only diff mode against an existing config.

---

## Under the hood

Everything below is reference material — you don't need it to use the pipeline.

### Per-run report

The conductor emits a `<run-list-basename>.report.json` file next to the run-list after every summary checkpoint (interim summaries and the final; interim reports are overwritten by the final). It's machine-readable and carries its own `schema_version` (independent of the plugin's semantic version) plus the engine version and the config version stamped at run time. Full schema and version history: [`shared/run-report-schema.md`](shared/run-report-schema.md). These report files are canonical — any aggregation or derived reporting is built on top of them, never as an alternative source.

### Safety posture

Run the pipeline against working sets you can cheaply restore — a git repo you can reset, a backed-up folder, a scratch copy — **not** against surfaces where a bad write is unrecoverable. This holds for any output type: the pipeline builds whatever the run-list names (code, documents, configs, content), and the recoverability rule is the same everywhere.

Why the caution is still warranted even with the hooks in place: as of v0.2 a mechanical layer ships for two of the three original prose-only boundaries —

- **Path containment** — the PreToolUse guard (`hooks/path_guard.py`) checks every Write/Edit target against the predicted-and-granted staging ring.
- **Probe execution** — the typed runner (`scripts/probe_runner.py`), a closed vocabulary that replaces free-text shell probes.

The prose rules remain in force as the model-side layer underneath both — and they are the *only* layer in effect when `python3` isn't on PATH, since the hooks and scripts require it. So a misread rule is a possible outcome, not an impossibility. The third boundary — the trust hierarchy (worker-brief provenance suffixes) — has no mechanical layer yet, and a validating write gateway for canonical intake remains future work (see the WRITE PATH "Future body" in `skills/conductor/SKILL.md`).

### One engine, two cuts

Each skill's text never hardcodes an environment. A swappable config layer binds it to yours (the annex pattern — same shape as Ari Evergreen Build's swappable domain layer). The house cut and the public cut build from the **same engine text**; they differ only in which filled `house-config.md` resolves at load time from outside the plugin folder:

- **House cut** — the house's own `house-config.md`, kept at its config location outside the repo.
- **Public cut** — an adopter's copy of `config/house-config.example.md`, renamed to `house-config.md` and kept outside the plugin folder.

A real, filled `house-config.md` is never committed or shipped — `config/` ships the example only, and the repo `.gitignore` guards against an accidental commit. Engine files reference config values as `` `cfg:<key>` `` and never state an installation-specific value; if an edit ever forces the engine text to diverge between cuts, that's a seam to stop and report, not to fork quietly. Engine files and the example config carry no installation paths, host-specific tool names, internal project names, or personal names.

### File tree

```
spire-pipeline/
  hooks/hooks.json                 PreToolUse hook registration
  hooks/path_guard.py              mechanical path-containment guard
  hooks/gate_brief_guard.py        gate-brief guard — denies a design-swarm gate
                                   ask without a fresh gate brief
  hooks/README-hooks.md            hook behavior + grants file schema
  scripts/probe_runner.py          typed probe runner (closed vocabulary)
  scripts/claim_lock.py            atomic run-claim lockfile
  skills/design-swarm/SKILL.md     engine (stage 1)
  skills/run-list/SKILL.md         engine (stage 2)
  skills/run-list/assets/template.md
  skills/conductor/SKILL.md        engine (stage 3)
  skills/setup/SKILL.md            first-run onboarding helper (optional)
  shared/pipeline-conventions.md   cross-skill conventions annex
  shared/run-report-schema.md      per-run report schema + version history
  references/                      brief templates, checker recipes, lineage, etc.
  config/house-config.example.md   sanitized example — copy it OUTSIDE the plugin
```

`config/house-config.md` is **not** a file here — your filled copy lives outside the plugin (see First run), because this folder is wiped on update.

### Credits & lineage

This pipeline stands on two pieces of borrowed, credited mechanism, both from [Ari Evergreen's Build (MIT)](https://www.skool.com/cliefnotes):

- **The context-pack contract** (stage 3 / conductor) — worker-brief composition: needle taxonomy, provenance suffixes, placement/budget, pointer-vs-gist split, decorrelated back-translation check. Its acceptance gate PASSED 2026-08-04 under two independent external model lineages (10/10 corruption types each, zero ID/value misses); the validation record, including the first gate it failed, is kept inline in the conductor's `SKILL.md`.
- **The brainstorming-swarm adaptation** (stage 1 / design-swarm) — adapted from Ari Evergreen's `brainstorming-swarm` v1.0.0 (stage spine, lens set, gates) onto this pipeline's own machinery.

Each engine skill carries its own **Lineage & credits** section at the foot of its `SKILL.md`. Shared cross-skill vocabulary (touch-kinds, tier-role names, verdict grammar, status glyphs, provenance suffixes) is defined once in `shared/pipeline-conventions.md`. The falsification-test and vitals lines inside the skills are the authors' own evaluation instrumentation — adopters can ignore them freely.

### Versioning

The plugin manifest (`.claude-plugin/plugin.json`) uses semver — see [`CHANGELOG.md`](CHANGELOG.md) for release history. The conductor's version log is semver-aligned with the plugin; the design-swarm, run-list, and setup logs use a date-based scheme (`vYYYY-MM-DD.N`).

*Formerly published internally as build-run-list / run-list-executor.*
