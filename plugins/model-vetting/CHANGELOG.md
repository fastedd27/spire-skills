# Changelog — model-vetting

Release history for the plugin. Deeper detail on how a skill reasons lives in its own
`SKILL.md`; scoring behavior lives in `skills/model-eval/references/rubric.md`.

## 0.1.0 (2026-08-09) — initial public release

- **New plugin.** Packages two existing, working skills as a designed pair: fast triage
  first, deep static read only when triage says you need one.
- **`model-scorecard`** — zero-friction gut check for a public HuggingFace model repo.
  `curl` + `jq` against the public HF API only: no tokens, no accounts, no weight
  download. Detects weight format (safetensors / GGUF vs the pickle family), detects
  custom code on load (`custom_code` tag, `auto_map`, `modeling_*.py`), assigns a coarse
  `(format, loader)` tier — E / D / C, with unrecognized formats failing **up** to `C?` —
  and prints a plain-language card. Code-bearing models get a grep-level authority
  heads-up under an alarm budget, explicitly labeled as presence, not reachability.
- **`model-eval`** — the deep static pass for a model that ships custom code, in HF mode
  or against a model folder already on disk (`MAE_LOCAL_DIR`). Deterministic collector
  (`scripts/collect_signals.sh`, bash + curl + jq + python3 stdlib) emits typed JSON:
  tier, format, custom-code signals, a manifest seal, per-file AST danger sites tagged
  module vs function scope, tainted sinks, authority targets, obfuscation, and
  provenance. The skill then separates load-path from incidental files, authors the
  behavioral claim twice (once from full source, once ignoring all comments and prose)
  and treats divergence as a first-class finding, runs a deterministic contradiction
  check against the collector's ground truth, traces generation-to-sink reachability,
  and scores against `references/rubric.md`.
- **Honesty architecture, shipped as-is.** Three unfused tracks (Provenance / Artifact /
  Instruction) — never averaged into a single safety number. Tier ceilings and hard caps.
  Adverse inference for the uninspectable remainder. Audit-opinion top-line, including
  **disclaimer of opinion** for any code-execution-tier artifact seen static-only. A
  residue list — contradictions, opaque authority, unverified claims — hands the
  remaining work to a scoped human read.
- **Standing limits, stated in the skills themselves:** nothing from the artifact is ever
  executed; no output is a clearance; silence is not safety; agreement among mechanisms
  that all read the same source is not corroboration. Pickle-opcode scanning and
  provenance attestation are delegated to `modelscan` / `picklescan` and SLSA-style
  tooling rather than reimplemented.
- **Falsifiability floor.** `fixtures/run_fixtures.sh` generates a seeded corpus with
  known properties and asserts the collector fires on each — offline, no network.
- **Worked example.** `EXAMPLE-baidu-Unlimited-OCR.md` is a real end-to-end report in the
  required shape: plain-English decision on top, evidence beneath.
- **Public-cut deltas.** Three edits separate this cut from the house skill copies it was
  packaged from, all in service of shipping publicly. The worked example carries a
  re-verification stamp — its findings were confirmed still present at revision
  `07dea832` on 2026-08-09, and are labeled point-in-time. The rubric's Provenance track
  no longer credits a person by first name and now names the companion
  repo-scorecard/repo-eval pair as a separate toolset that isn't shipped here (both
  `SKILL.md` files reworded to match). And `scorecard.sh` labels non-safetensors weight
  formats individually: pickle-family and Keras `.h5` are both code-capable on load and
  say so, while Flax `.msgpack` is data-only and is now stated to sit at tier C by
  conservatism rather than by a detected code path. No tier changed.
- No config layer. Install and use.
