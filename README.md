# spire-skills

Skills and plugins from **The Wizard's Spire** — working agent-orchestration machinery, cut from a live operator system and published with the house residue swapped out for a config layer you fill in yourself.

## Install

```
/plugin marketplace add fastedd27/spire-skills
/plugin install spire-pipeline@spire-skills
```

## Plugins

| Plugin | What it is |
|--------|------------|
| [spire-pipeline](plugins/spire-pipeline/) | Three-stage build pipeline: **design-swarm** (divergence-first design pass — competing approaches, critique gate), **run-list** (one durable document that plans and tracks a multi-session build), **conductor** (tiered execution engine — every completed step verified by a mechanical probe before it counts; no self-certified done). |

More on the way — a model-security vetting pair (scorecard + deep eval) is next.

## Design stance

These aren't prompt packs. Each skill encodes an operating discipline: deny-by-default write safety, one-writer state, verification receipts, and honest failure surfaces (parked work is spelled out in plain English, not buried). The engines never hardcode an environment — a swappable config layer (`config/house-config.example.md` in each plugin) binds them to yours, and every key documents what happens if you omit it.

## Credits

Built on Claude (Anthropic) tooling. The pipeline borrows two credited mechanisms from Ari Evergreen's Build (MIT): the context-pack contract (stage 3) and the brainstorming-swarm adaptation (stage 1): https://www.skool.com/cliefnotes. Full lineage in each plugin's README.

## License

MIT — see [LICENSE](LICENSE).
