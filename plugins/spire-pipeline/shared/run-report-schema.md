# Run Report Schema — v1.0

<!-- ENGINE FILE — canonical schema reference for the per-run report the
     conductor emits at every D9 summary (final RUN SUMMARY and INTERIM RUN
     SUMMARY). This file documents the shape; it is not itself a validator —
     no script ships against it (see Evolution rules and the non-goals below).
     Field names and categories are generic and installation-agnostic; no
     house jargon, no internal ids, no host-specific paths appear here or in
     any emitted report. -->

## File contract

- Filename: `<run-list-basename>.report.json`, written as a sibling of the run-list (same directory).
- Keying: keyed to run-list identity — stable across resumes. Never keyed by run-id (resumes mint new run-ids, which would fork the report into orphans).
- Re-scan discovery: any future consumer walks `**/*.report.json`.
- Lifecycle: an INTERIM report is overwritten in place by the FINAL report for the same run-list. Only the latest state per run survives — accepted, not an oversight.
- Emission order: the conductor computes one tally object, writes the JSON file first, then renders the prose RUN SUMMARY / vitals from that same object (single-tally mechanism — the JSON is never a re-derivation of the prose).

## Schema v1.0

The report's own `schema_version` versions independently of the engine's semver (`plugin.json`'s `version`). This is the full shape, verbatim:

```json
{
  "schema_version": "1.0",
  "run": {
    "date": "<ISO-8601 UTC>",
    "project": "<free slug>",
    "task": "<one-line>",
    "mode": "work|code",
    "engine_version": "<from .claude-plugin/plugin.json>",
    "house_config_version": "<from config version field>",
    "house_config_date": "<from config>",
    "run_list": "<path>",
    "run_status": "completed|parked|interim"
  },
  "volume": {
    "rows_total": 0, "rows_ticked": 0, "rows_parked": 0,
    "park_reasons": { "canonical-surface": 0, "physical-action": 0, "unknown-blocker": 0, "dependency": 0, "operator-decision": 0, "other": 0 },
    "park_notes": ["required when other > 0"]
  },
  "cost": {
    "dispatches_by_tier": { "mechanical": 0, "standard": 0, "judgment": 0 },
    "tokens_by_tier": { "mechanical": 0, "standard": 0, "judgment": 0, "basis": "estimate|metered" },
    "wall_clock_minutes": 0
  },
  "vitals": {
    "retries": 0, "tier_escalations": 0, "rows_per_hour": 0,
    "catch_ratio": { "enumerated_trigger_parks": 0, "judgment_parks": 0 },
    "needle_leak_rate": null
  },
  "oversight": {
    "operator_touches": 0,
    "caught_problems": { "parks_saving_work": 0, "probe_failures_fired": 0 }
  }
}
```

## Field reference

### Top level

| field | description |
|---|---|
| `schema_version` | The report schema's own semver (starts `"1.0"`); independent of the engine's `plugin.json` version. |
| `run` | Identity of the run: what ran, when, on which engine and config. |
| `volume` | How much of the run-list moved: row counts and categorized park reasons. |
| `cost` | What the run spent: dispatches and tokens per tier, plus wall-clock time. |
| `vitals` | Derived health numbers for the run, superset of anything a prose summary states. |
| `oversight` | How much the operator had to touch, paired with whether that touch caught anything real. |

### `run`

| field | description |
|---|---|
| `date` | Run timestamp, ISO-8601 UTC. |
| `project` | Free-text project slug the run-list belongs to. |
| `task` | One-line description of what the run-list was building. |
| `mode` | Which conductor mode ran: `work` or `code`. |
| `engine_version` | The pipeline engine version, read from `.claude-plugin/plugin.json`. |
| `house_config_version` | The resolved config's own version field. |
| `house_config_date` | The resolved config's own date, stamped together with `house_config_version` so a stale hand-bumped version is visible against its date. |
| `run_list` | Path to the run-list document this report was emitted for. |
| `run_status` | `completed` = a FINAL report where `rows_parked` is 0. `parked` = a FINAL report where `rows_parked` > 0 — a fully-visited run that ends with any parked rows is `parked`, never `completed`. `interim` = any non-final summary (mid-run park/pause); overwritten by the final. |

### `volume`

| field | description |
|---|---|
| `rows_total` | Total rows in the run-list. |
| `rows_ticked` | Rows that reached verified-done. |
| `rows_parked` | Rows parked to the return board instead of ticking. |
| `park_reasons` | Object with one integer count per park-reason category (see the vocabulary in `shared/pipeline-conventions.md`); counts must sum to `rows_parked`. |
| `park_notes` | Array of free-text notes; required (non-empty) whenever `park_reasons.other > 0`, explaining what "other" covered. |

### `cost`

| field | description |
|---|---|
| `dispatches_by_tier` | Count of row dispatches per tier-role (`mechanical`, `standard`, `judgment`). |
| `tokens_by_tier` | Token counts per tier-role, plus the mandatory `basis` field. |
| `tokens_by_tier.basis` | `estimate` or `metered` — mandatory on every report; an estimated figure must never be presented as if it were metered. |
| `wall_clock_minutes` | Total run duration in minutes. |

### `vitals`

| field | description |
|---|---|
| `retries` | Count of row retries across the run. |
| `tier_escalations` | Count of rows that escalated from a lower tier to a higher one. |
| `rows_per_hour` | Throughput: rows resolved (ticked or parked) per hour of wall-clock time. |
| `catch_ratio.enumerated_trigger_parks` | Parks triggered by an enumerated, mechanical condition. |
| `catch_ratio.judgment_parks` | Parks triggered by a worker's or conductor's judgment call rather than an enumerated trigger. |
| `needle_leak_rate` | Reserved for a future measure of needle-requirement leakage; `null` until that measure is defined. |

### `oversight`

| field | description |
|---|---|
| `operator_touches` | Count of times the operator had to intervene during the run. |
| `caught_problems` | Object with both members below; `operator_touches` is never reported alone (No Clean Evaluator) — a touch count with no paired evidence of what it caught is not meaningful on its own. |
| `caught_problems.parks_saving_work` | Count of parks that avoided wasted or wrong work by stopping before a bad tick. |
| `caught_problems.probe_failures_fired` | Count of times the mechanical verification probe fired a failure that blocked a tick. |

## Evolution rules

- Additive-only within a major version: new fields may be added to a `1.x` schema without a major bump.
- Readers ignore unknown fields: any consumer parsing a report tolerates fields it does not recognize.
- Renames or removals require a major version bump: changing or dropping an existing field name is never a minor/patch change.
- Enums grow via `other` plus a note: adding a new enumerated value (e.g. a new park-reason category) happens by using `other` together with a `park_notes` entry describing it, not by inventing a new bare enum value ahead of a schema bump.

## Non-goals (scope fence)

No store, no index, no dashboard, no persistence hook. No validator script or probe-mode ships against this schema — conformance rides on the conductor's D9 emission discipline, not on shipped validation machinery.
