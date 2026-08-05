---
type: run-list
status: live
project: demo-fixture
task: Acceptance-test fixture for the per-run report emission (OT-HQ-168)
created: 2026-08-05
---

# Run List — demo-fixture

Minimal 3-row fixture used only to exercise the conductor's D9 per-run report
emission (schema v1.0). Not a real build.

## Rows

### Row 1 — R1: rename the demo config key

- State: ✅ verified
- `[R1-VERDICT]` Renamed `old_key` to `new_key` in `demo-config.md` and updated its one reader.
- Receipt: `content_matches("demo-config.md", "new_key")` — PASS.

### Row 2 — R2: add the demo README section

- State: ✅ verified
- `[R2-VERDICT]` Added the "Per-Run Report" section to `demo-README.md`.
- Receipt: `file_exists("demo-README.md")` — PASS; `content_matches("demo-README.md", "Per-Run Report")` — PASS.

### Row 3 — R3: pick the default report retention policy

- State: 🅿 parked — operator-decision
- `[R3-VERDICT]` Cannot choose between "keep every interim report" and "overwrite-only" without operator input; both are defensible, this is not a judgment call the worker can make alone.
- ⏸️ NEED FROM YOU: Should the demo fixture's report retain interim history, or overwrite-only like schema v1.0 specifies?

## Return Board

| Row | Reason | Need |
|---|---|---|
| R3 | operator-decision | Should the demo fixture's report retain interim history, or overwrite-only like schema v1.0 specifies? |

## RUN SUMMARY

- Rows: ✅ 2 (R1, R2) · 🅿 1 (R3) · ⛔ 0
- Receipts index: R1 receipt above; R2 receipt above.
- Return-board state: 1 open card (R3, operator-decision).
