# Changelog — spire-pipeline

Release history for the plugin. Deeper engine detail (rule-level provenance, fold history) lives in each skill's own version log inside its `SKILL.md`.

## 0.4.0 (2026-08-05)

- **No Naked Gate — the gate brief.** New canonical rule in `shared/pipeline-conventions.md`: every operator-facing gate must render enough readable context IN THE LIVE CONVERSATION (chat or code-window turn, mobile included) for the operator to answer without guessing — decision, each option by what it is + its tradeoff (never a bare codename), recommendation + why, reversibility. Closes the maiden-run failure where gates surfaced bare option labels and forced a blind accept of the recommendation.
- `design-swarm` Gate A and Gate B now require the discovery summary / scoreboard to land as a gate brief in the conversation before the ask fires.
- `conductor` D3: the decide-once brief file stays the hash-ratified system of record, but its Table A/B content is now rendered into the conversation for answering (answerable on mobile with the file closed); `operator-decision` return-board cards carry the gate-brief shape.
- `run-list` return-board cards that ask the operator to choose carry the gate-brief shape.
- Skill version tags bumped: design-swarm `v2026-08-05.1`, run-list `v2026-08-05.1`, conductor `v2026-08-05.1`.

## 0.3.0 (2026-08-05)

- **Per-run report.** The conductor now emits `<run-list-basename>.report.json`, sibling to the run-list, at every summary (interim and final; the final overwrites the interim). Machine-readable and version-stamped: its own `schema_version` (1.0, independent of the plugin version) plus the engine version and config version.
- New `shared/run-report-schema.md`: full field reference and additive-evolution rules (additive-only within a major; readers ignore unknown fields; renames require a major bump).
- Park-reason vocabulary (six categories) added to `shared/pipeline-conventions.md`.
- Example report and a runnable acceptance fixture under `references/`.
- Config example gains `cfg:config.version` (bump on any edit; reports stamp version and date together so a stale version is visible).
- Tally-first rule: the prose RUN SUMMARY and vitals are rendered from the report object, never tallied twice.
- Semantics ruling: a final report with any parked rows is `parked`, never `completed`. (Caught by the acceptance fixture during this release's own build.)

## 0.2.1 (2026-08-05)

- Hook runtime fallback chain (`python3` then `python` then `py -3`), exec-probed so the Windows Store alias stub can't fake a working interpreter. No usable Python means the guard announces INACTIVE loudly and the prose rules carry enforcement.

## 0.2.0 (2026-08-04) — initial public release

- Mechanical enforcement layer: predicted write grants (`.pipeline-grants.json`) enforced by a PreToolUse path-guard hook; a closed-vocabulary typed probe runner (`file_exists` / `content_matches` / `commit_exists` / `http_status` / `fixture`); an atomic claim lock with stale-steal.
- Three skills shipped: `design-swarm` (divergence-first design pass), `run-list` (durable multi-session build planning), `conductor` (tiered execution, probe-verified ticks).
- Config-swappable: all installation-specific values resolve through `config/house-config.example.md`.

## 0.1.0 (house lineage, unpublished)

- Prose-only enforcement engine, cut one-to-one from the originating operator system's skills. Zero scripts by design; every later script was added only after a demonstrated failure earned it.
