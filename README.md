# spire-skills

Skills and plugins from **The Wizard's Spire** — working agent-orchestration machinery, cut from a live operator system and published with the house residue swapped out for a config layer you fill in yourself.

## Install

**Claude Code (CLI):**

```
/plugin marketplace add fastedd27/spire-skills
/plugin install spire-pipeline@spire-skills
```

**Claude desktop / Cowork (GUI):** Settings → Plugins → add the marketplace `fastedd27/spire-skills`, then install **spire-pipeline**. Enable marketplace auto-sync to pick up new versions.

**Updating (desktop):** auto-sync pulls new commits from the marketplace on its own, but the installed plugin only moves forward when you click **Update** on its plugin page (Settings → Plugins → Spire pipeline — an "Update available" badge appears when the synced marketplace is ahead).

Installs are per-surface — if you work in both, install in both. Skills and hooks load at session start, so open a fresh session after installing or updating; running sessions keep the old version.

## Plugins

| Plugin | What it is |
|--------|------------|
| [spire-pipeline](plugins/spire-pipeline/) — v0.3.0 ([changelog](plugins/spire-pipeline/CHANGELOG.md)) | Three-stage build pipeline: **design-swarm** (divergence-first design pass — competing approaches, critique gate), **run-list** (one durable document that plans and tracks a multi-session build), **conductor** (tiered execution engine — every completed step verified by a mechanical probe before it counts; no self-certified done). Every run emits a machine-readable, version-stamped report (`<run-list-basename>.report.json`) at each run summary — schema in [run-report-schema.md](plugins/spire-pipeline/shared/run-report-schema.md). |

More on the way — a model-security vetting pair (scorecard + deep eval) is next.

## Design stance

These aren't prompt packs. Each skill encodes an operating discipline: deny-by-default write safety, one-writer state, verification receipts, and honest failure surfaces (parked work is spelled out in plain English, not buried). The engines never hardcode an environment — a swappable config layer (`config/house-config.example.md` in each plugin) binds them to yours, and every key documents what happens if you omit it.

## Credits

Built on Claude (Anthropic) tooling. The pipeline borrows two credited mechanisms from Ari Evergreen's Build (MIT): the context-pack contract (stage 3) and the brainstorming-swarm adaptation (stage 1): https://www.skool.com/cliefnotes. Full lineage in each plugin's README.

## License

MIT — see [LICENSE](LICENSE).
