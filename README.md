Part of [The Spire Library](https://thespirelibrary.com/?utm_source=github&utm_medium=repo&utm_campaign=spire-skills#shipped) —
Charles Weeks's work on AI memory systems, retrieval, and local-first infrastructure.

---

# spire-skills

A **plugin marketplace** for Claude Code and Claude desktop (Cowork), published by [The Spire Library](https://thespirelibrary.com). Each plugin is a piece of working agent-orchestration machinery — cut from a live operator system, with the house-specific residue swapped out for a config layer you fill in yourself (or safe defaults you never have to touch).

This repo is the **directory**. It tells you what's here and how to install it. Each plugin then has its own README that tells you what it does and how to use it — start there once you've picked one.

## What's here

| Plugin | Version | What it is | Config? |
|--------|:---:|------------|:---:|
| **[spire-pipeline](plugins/spire-pipeline/)** | 0.5.2 | A three-stage build pipeline that takes a project from vague idea to executed, verified plan across as many Claude sessions as it takes: **design-swarm** (competing designs, critique gate) → **run-list** (one durable doc that plans and tracks the build) → **conductor** (tiered execution where every step is verified by a mechanical probe before it counts). Plus **setup**, a two-question onboarding helper. | Optional |
| **[model-vetting](plugins/model-vetting/)** | 0.1.0 | Two paired skills for looking at an AI model *before* you adopt it: **model-scorecard** (fast triage over the public HuggingFace API — no token, no download) and **model-eval** (a deep static read of models that ship custom code). Static only — never runs the artifact, never issues a clearance. | None |

*More on the way. Each new plugin lands as its own row here and its own folder under `plugins/`.*

## Install

**Claude Code (CLI):**

```
/plugin marketplace add fastedd27/spire-skills
/plugin install spire-pipeline@spire-skills
/plugin install model-vetting@spire-skills
```

Install only the plugins you want — they're independent.

**Claude desktop / Cowork (GUI):** Settings → Plugins → add the marketplace `fastedd27/spire-skills`, then install the plugins you want. Enable marketplace auto-sync to pick up new versions.

Once a plugin is installed, open its README (linked in the table above) to get started — that's where each plugin's own setup and usage lives.

### Updating

Auto-sync pulls new commits from the marketplace on its own, but an installed plugin only moves forward when you click **Update** on its plugin page (Settings → Plugins → *plugin name* — an "Update available" badge appears when the synced marketplace is ahead).

Installs are **per-surface** — if you work in both CLI and desktop, install in both. Skills and hooks load at session start, so **open a fresh session after installing or updating**; running sessions keep the old version.

## Design stance

These aren't prompt packs. Each plugin encodes an operating discipline — deny-by-default write safety, one-writer state, verification receipts, and honest failure surfaces (parked or unresolved work is spelled out in plain English, never buried). Where a plugin needs to know about your machine, it never hardcodes it: a swappable config layer binds the engine to your environment, and every config key documents what happens if you omit it, so a first run with zero configuration is always safe.

## Credits

Built on Claude (Anthropic) tooling. Where a plugin borrows external mechanism, it credits it in its own README and lineage files — e.g. spire-pipeline credits two mechanisms from [Ari Leavesley (MIT)](https://www.skool.com/cliefnotes).

## License

MIT — see [LICENSE](LICENSE).
