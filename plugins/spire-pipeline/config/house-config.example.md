# House Config — pipeline skills config layer (EXAMPLE / PUBLIC CUT)

<!-- CONFIG LAYER — the swappable annex (same shape as Ari Evergreen Build's
     swappable domain layer). Copy this file to `house-config.md`, replace every
     example value with your own installation's value, and the three engine
     skills run against your environment unchanged. The engine files
     (skills/*/SKILL.md, the run-list template, shared/pipeline-conventions.md)
     reference every value below generically as `cfg:<key>` and never state an
     installation value themselves. Do NOT copy values from your config into an
     engine file; that forks the one-source guarantee. -->

How resolution works: wherever an engine file says `` `cfg:<key>` ``, a session
substitutes the value from your table. There is no templating engine — the
conductor reads this file once at skill load and applies the values as prose.
Config discovery search order (deterministic): (1) project root, (2) home
directory; first found wins — project beats home. A key with a documented
"Omit →" default (see the table below) uses that default when the key is
omitted from your config. Only a key with NO documented default, or an
unrecognized/malformed entry, is treated like an UNKNOWN row: deny-by-default
(park and ask), never guessed.

## Quickstart — the keys most installs actually set

You can run with NO config file at all: every key falls back to its "Omit →" default (scratch-dir staging, serial in-session dispatch, all canonical writes park, follow-ups numbered inside the run-list). It degrades to a safe solo mode.

To get a useful setup without reading the whole table, copy this file to `house-config.md` OUTSIDE the plugin folder (project root or home) and set just these three:

- `cfg:staging.durable_root` — where run-lists, specs, and keeper artifacts land and survive the session (e.g. `~/projects/<project>/`). Without it they go to `./pipeline-runs/`.
- `cfg:dispatch.mechanism` — point this at your subagent/Task tooling so the conductor can fan work out; omit for serial in-session (slower, same guarantees).
- `cfg:hooks.hash` — on Windows set `certutil -hashfile <path> SHA256`; on macOS/Linux/WSL the `sha256sum` default is fine.

Everything else below is safe to leave at its documented default until you have a reason to set it. The full table follows.

The three one-liners below do that copy for you, targeting your **home directory** (project root works too — swap the destination). Each is no-clobber: it refuses to touch an existing `house-config.md`, and what it produces is a **starting file** — copy this example, then edit it down to the three keys above (and whatever else you need from the table) per this Quickstart. It is never a finished config on its own.

macOS / Linux:

```bash
cp -n config/house-config.example.md ~/house-config.md
```

WSL:

```bash
cp -n config/house-config.example.md ~/house-config.md
```

Windows PowerShell:

```powershell
if (-not (Test-Path "$HOME\house-config.md")) { Copy-Item "config\house-config.example.md" "$HOME\house-config.md" }
```

Windows installs must also set `cfg:hooks.hash` to `certutil -hashfile <path> SHA256` — the `sha256sum` omit-default is not present on a stock Windows box.

**Already have a config?** Run `spire-pipeline:setup` in diff mode: it reports which keys are new or changed against your existing `house-config.md` and never writes anything itself.

**For an AI assistant running this Quickstart on someone's behalf:**
- Confirm the user's actual HOST operating system before picking a block — a cloud/container session often reports Linux even when the user's host is Windows, so don't infer OS from the execution environment.
- Never overwrite an existing `house-config.md`; the no-clobber guards above are load-bearing, not a suggestion to skip if a file is already there.
- Keys and their defaults come only from the table below — never invent, infer, or borrow a value from anywhere else.

## Config metadata

| key | what it is | example value |
|---|---|---|
| `cfg:config.version` | A semver version for this config file (starting `1.0`). Any edit to the config must bump this version. Per-run reports stamp this version AND the config's modification date together, so a stale hand-bumped version is visible against its date. Omit → "unversioned" plus the config file's modification date. | `1.0` or higher, e.g. `1.2` |

## Path roots (staging ring)

| key | what it is | example value |
|---|---|---|
| `cfg:staging.workdir` | The disposable per-session working directory (wiped between sessions; nothing durable lives here). Omit → a scratch subdirectory. | A scratch subdirectory (`./.pipeline-scratch/` or `/tmp/<run-id>/`) — explicitly NEVER the repository/working tree being built. |
| `cfg:staging.durable_root` | Per-project durable staging root — where run-lists, specs, swarm-run folders, and keeper artifacts land. Must survive the session. Omit → `./pipeline-runs/` in the project. | `~/projects/<project>/` |
| `cfg:shared.root` | A cross-project shared surface (shared scripts, pending skills, shared reference material). OUT of the staging ring: writes there PARK by default. Omit if your installation has no shared surface. | `~/projects/_shared/` |
| `cfg:shared.registry` | A shared registry/ledger file multiple sessions may touch — the canonical shared-surface-serialization case (conductor-applied edits only). Omit → none; the shared-surface-serialization rule still applies to any multi-writer file. | `~/projects/_shared/registry.md` |

## Write toolchain

| key | what it is | example value |
|---|---|---|
| `cfg:write.toolchain` | The sanctioned tools for durable writes, and the banned side channels. Omit → the session's built-in file tools. | "All durable writes via the project's approved filesystem tooling; never ad-hoc shell redirection into durable paths." (for a plain session: the built-in Write/Edit file tools). |

## Dispatch binding

| key | what it is | example value |
|---|---|---|
| `cfg:dispatch.mechanism` | The concrete mechanism tier-roles bind to. | "built-in subagent/Task tooling; omit → serial in-session fallback" |
| `cfg:dispatch.tier_mechanical` | The model/seat used for `mechanical` rows. Omit → all rows run at session default. | "fast/cheap model" |
| `cfg:dispatch.tier_standard` | The model/seat used for `standard` rows. Omit → all rows run at session default. | "default model" |
| `cfg:dispatch.tier_judgment` | The model/seat used for `judgment` rows. Omit → all rows run at session default. | "strongest available model" |
| `cfg:dispatch.checker_lineage` | Which model lineage runs decorrelated checks (the context-pack back-translation checker) (see references/checker-recipes.md). Omit → same-model, with a prominent correlation caveat recorded in the receipt. | "a different vendor's model via your own tooling" |

## Script + tool hooks

| key | what it is | example value |
|---|---|---|
| `cfg:hooks.wrap_sweep` | A script/check that verifies every keeper artifact sits at a durable path at wrap time. Omit → do the sweep manually. | `./scripts/wrap_sweep.py` (your own script if you have one — NOT shipped with this plugin) |
| `cfg:hooks.id_mint` | A script/process that reserves work-item ids so sessions never hand-mint colliding ids. Omit → park id minting to the operator. | `./scripts/mint_id.py` (your own script if you have one — NOT shipped with this plugin) |
| `cfg:hooks.notify` | Your existing operator-notification mechanism (push, chat webhook, email). The engine never invents a new one. Omit → none; parks surface in the return board only. | "the team's existing on-call/chat webhook" |
| `cfg:hooks.hash` | An existing host tool for computing the decide-once brief's SHA-256. Omit → `sha256sum` (present on macOS/Linux/WSL). **Windows note:** `sha256sum` is NOT on a stock Windows box, so the omit-default will fail there — set this key to `certutil -hashfile <path> SHA256`. | `sha256sum <path>` (any equivalent SHA-256 tool; `certutil -hashfile <path> SHA256` on Windows) |

## Governance (rule names + surfaces)

| key | what it is | example value |
|---|---|---|
| `cfg:gov.state_surfaces` | The state/coordination surfaces (hub ledger, session-context notes, session markers, follow-up queues) that belong to the owning session's wrap — executors and workers never write them. Omit → no separate state surface; the run-list is the only state. | "the project hub doc, session logs, and the follow-up queue" |
| `cfg:gov.state_ownership_rule` | The name of your rule that says state-surface writes belong to the owning session's wrap. Omit → the run-list is the only state surface. | "the wrap-owns-state rule" |
| `cfg:gov.canonical_surfaces` | Your canonical knowledge surfaces (knowledge-base notes, decision/lesson logs, index files, host config). Canonical writes always PARK in executor v1. Omit → every canonical-shaped write parks with no named surface to route to (deny-by-default still holds). | "the team wiki + decision log + host config" |
| `cfg:gov.recap_process` | The owning session's wrap/recap process that consumes the executor's candidate-lessons block. Omit → skip recap routing; parks stay on the return board. | "the end-of-session recap checklist" |
| `cfg:gov.followup_queue` | Where deferred follow-ups go, your work-item id format, and the frontmatter field name for related ids. Omit → number follow-ups FU-1, FU-2 inside the run-list. | "the project issue tracker; ids `PROJ-NNN`; frontmatter field `related_ids`" |
| `cfg:gov.write_gateway` | A future write-gateway for validated canonical intake (typed change packages). FUTURE TENSE ONLY until yours exists — until then, canonical writes park. Omit → no gateway; canonical writes always park. | "none yet — canonical writes always park" |
| `cfg:gov.project_manifest` | Each project's write-boundary manifest that a per-project row's worker brief carries. Omit → no per-project manifest; the run-list's own Locked-at-kickoff block is the row's write boundary. | "each repo's CONTRIBUTING/agent-rules file" |

## Reference docs (frozen pointers)

| key | what it is | example value |
|---|---|---|
| `cfg:refs.executor_spec` | Your ratified executor design spec of record, if you keep one. On conflict, spec wins over skill text. Omit → none — this skill text is the spec. | "none — the skill text is the spec" |
| `cfg:refs.swarm_comparison` | The lineage/comparison record for your design-swarm adaptation, if kept. Omit → none. | "none" |
| `cfg:refs.context_pack_acceptance` | The acceptance-test record for the context-pack contract (validated by the authors 2026-08-04; the conductor skill carries the record inline). Re-validate — and note it here — if you modify the contract. The test shape: build ~20 corrupted variants of real plan rows (negation flips, dropped exception clauses, altered IDs/values/paths), have the drafter build needle lists from the corrupted rows, then have an independent (ideally different-lineage) checker diff the restatements against the originals. Gate: ≥8/10 corruption types caught AND zero ID/value misses. Omit → inherit the authors' validation; this field tracks YOUR check after any contract modification. | "authors' re-gate PASSED 2026-08-04 (two external lineages, 10/10 each, zero ID/value misses); this field tracks YOUR check if you modify the contract |
| `cfg:refs.version_logs` | Where full skill version logs live for your installation. Omit → the repo's git history. | "the repo's git history" |
