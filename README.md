Part of [The Spire Library](https://thespirelibrary.com/?utm_source=github&utm_medium=repo&utm_campaign=spire-skills#shipped) —
Charles Weeks's work on AI memory systems, retrieval, and local-first infrastructure.

---

# spire-skills

Skills and plugins from **The Spire Library** (https://thespirelibrary.com) — working agent-orchestration machinery, cut from a live operator system and published with the house residue swapped out for a config layer you fill in yourself.

## Install

**Claude Code (CLI):**

```
/plugin marketplace add fastedd27/spire-skills
/plugin install spire-pipeline@spire-skills
/plugin install model-vetting@spire-skills
```

**Claude desktop / Cowork (GUI):** Settings → Plugins → add the marketplace `fastedd27/spire-skills`, then install **spire-pipeline** and/or **model-vetting**. Enable marketplace auto-sync to pick up new versions.

**Updating (desktop):** auto-sync pulls new commits from the marketplace on its own, but the installed plugin only moves forward when you click **Update** on its plugin page (Settings → Plugins → Spire pipeline — an "Update available" badge appears when the synced marketplace is ahead).

Installs are per-surface — if you work in both, install in both. Skills and hooks load at session start, so open a fresh session after installing or updating; running sessions keep the old version.

## First run (new here? start with this)

You can use the pipeline immediately with **zero configuration** — every config key has a documented safe default, and the skills say `running on omit-defaults` so you know that's what's happening. When you want your outputs landing somewhere durable of your choosing, either:

- **say `setup`** (the `spire-pipeline:setup` skill) — it detects what it can about your machine (OS, hash tool, whether the session can fan work out), asks just two plain questions (where should finished work live; config per-project or machine-wide), and writes a minimal `house-config.md` for you. It never overwrites an existing config — re-running it on a configured machine gives you a read-only report instead (`check my config`); **or**
- **do it by hand** — open the plugin's [`config/house-config.example.md`](plugins/spire-pipeline/config/house-config.example.md) and follow its Quickstart section (three keys, copy-paste commands per OS).

Either way the file lives **outside the plugin folder** (project root or home — the plugin folder is wiped on every update). Then just talk to it: "design swarm this…", "map out the sessions", "execute the run-list".

## Plugins

| Plugin | What it is |
|--------|------------|
| [spire-pipeline](plugins/spire-pipeline/) — v0.5.1 ([changelog](plugins/spire-pipeline/CHANGELOG.md)) | Three-stage build pipeline: **design-swarm** (divergence-first design pass — competing approaches, critique gate), **run-list** (one durable document that plans and tracks a multi-session build), **conductor** (tiered execution engine — every completed step verified by a mechanical probe before it counts; no self-certified done). Plus **setup**, an optional first-run helper that gets you from installed to configured in two questions. Every run emits a machine-readable, version-stamped report (`<run-list-basename>.report.json`) at each run summary — schema in [run-report-schema.md](plugins/spire-pipeline/shared/run-report-schema.md). |
| [model-vetting](plugins/model-vetting/) — v0.1.0 ([changelog](plugins/model-vetting/CHANGELOG.md)) | Two paired skills for looking at an AI model before you adopt it: **model-scorecard** (fast triage over the public HuggingFace API — no token, no download — returning a coarse `(format, loader)` risk tier and a plain-language card) and **model-eval** (the deep static read for models that ship custom code — deterministic collector, a behavioral claim written twice and checked against the code's actual call graph, generation-to-sink traces, and a report a non-developer can act on). Neither executes anything from the artifact and neither issues a clearance; a code-execution artifact seen static-only gets a **disclaimer of opinion**, not a rating. No config layer. |

More on the way.

## Design stance

These aren't prompt packs. Each skill encodes an operating discipline: deny-by-default write safety, one-writer state, verification receipts, and honest failure surfaces (parked work is spelled out in plain English, not buried). The engines never hardcode an environment — a swappable config layer (`config/house-config.example.md` in spire-pipeline) binds them to yours, and every key documents what happens if you omit it.

## Credits

Built on Claude (Anthropic) tooling. The pipeline borrows two credited mechanisms from Ari Evergreen's Build (MIT): the context-pack contract (stage 3) and the brainstorming-swarm adaptation (stage 1): https://www.skool.com/cliefnotes. Full lineage in each plugin's README.

## License

MIT — see [LICENSE](LICENSE).
