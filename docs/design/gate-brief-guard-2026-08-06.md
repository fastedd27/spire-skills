---
title: Gate-Brief Guard — mechanical enforcement for No Naked Gate
project: spire-pipeline
thread: OT-HQ-168 (pipeline review)
date: 2026-08-06
type: design-spec
status: live
ratification: operator-approved 2026-08-06 (approach: "add mechanical enforcement")
mode: authored inline; hook probe-verified (8/8) in cloud container
---

# Gate-Brief Guard

## Problem (confirmed root cause)

The **No Naked Gate** rule shipped in plugin **0.4.0** and is live in the
version sessions currently load (**0.4.1**). It is **prose only** — a written
instruction in `shared/pipeline-conventions.md` plus the Gate A / Gate B lines
in `design-swarm/SKILL.md`. The plugin's only hook (`path_guard.py`) guards
`Write|Edit` targets and nothing else. **Nothing mechanically enforces the gate
brief.**

On the 2026-08-06 live run the orchestrating model had the rule in context
(the stage labels in the run — `Gate A — operator redirect`, `S2 — approaches
(3 axioms)` — match 0.4.1 exactly, ruling out a stale cache), emitted its
heartbeat line ("All six lenses landed… then Gate A"), and jumped straight to a
bare `AskUserQuestion` widget with no discovery summary. A classic soft-rule
skip.

Diagnostic notes:
- Not a stale copy: deployed skill = committed source = synced = 0.4.1, all
  carry the rule.
- Not a lost edit: the repo working tree shows every file "modified," but
  `git diff --ignore-cr-at-eol` is empty — pure CRLF churn (the mounted-repo
  trap), not a pending fix.
- Therefore: prose enforcement failed in the field. The maiden run (which the
  rule was written for) plus this run make **two** field failures. By the
  plugin's own earn-the-complexity rule, the gate brief has earned teeth.

## Mechanism

A second PreToolUse hook, `gate_brief_guard.py`, matched on `AskUserQuestion`.
It mirrors `path_guard.py`'s contract exactly (same `emit()` shape, same
`hookSpecificOutput.permissionDecision` field, same fail-open posture).

Two model obligations, both the same "write to the run folder" muscle the
skill already uses for digests:

1. **S0 arms it.** When `design-swarm` creates the run folder, it also writes a
   marker `${CLAUDE_PROJECT_DIR}/.swarm-active.json` containing
   `{ "run_folder": "<abs path to this run's folder>" }`. HALT (S5) deletes it.
2. **Each gate writes its brief file first.** Immediately before the Gate A /
   Gate B ask, the conductor writes the brief to
   `<run-folder>/gate-A-brief.md` (or `gate-B-brief.md`) AND renders that same
   content into the conversation (one writer, many surfaces).

The hook then enforces:

- **No marker → total no-op** (exit 0, emit nothing). `AskUserQuestion` is used
  everywhere; only an active swarm arms the guard. This invariant is
  load-bearing and is the first probe below.
- **Marker present, no fresh brief → `deny`** with a reason telling the model
  to write + render the brief and retry. `deny` (not `ask`) is deliberate: we
  want the model to self-correct, not prompt the operator to rubber-stamp a
  naked gate.
- **Fresh brief present** (`gate-*-brief.md`, ≥ 400 bytes, modified within
  300 s) **→ allow.** Freshness separates Gate A's brief from Gate B's without
  the hook needing to know which gate is firing — the two are minutes apart
  with S2/S3 between them.
- **Stale marker (> 6 h, crashed run) → step aside** with a visible warning.
- **Any internal error / bad payload → fail open** with a systemMessage.

Why a file-freshness check instead of a per-gate state flag: less model
bookkeeping (no flag to toggle/clear), and the presence of a just-written brief
file IS the signal we want — the model cannot advance the widget without having
just produced a brief.

## Implementation

### 1. New hook — `plugins/spire-pipeline/hooks/gate_brief_guard.py`

(Full file below; probe-verified 8/8. Ships alongside `path_guard.py`.)

```python
#!/usr/bin/env python3
"""PreToolUse gate-brief guard — mechanical backstop for No Naked Gate.

Blocks an AskUserQuestion call during an ACTIVE design-swarm run unless a
FRESH, non-trivial gate-brief file was just written to the run folder. This is
the teeth behind the prose rule in shared/pipeline-conventions.md: the operator
must be shown a readable brief before any gate ask.

NO-OP INVARIANT (load-bearing): no active-swarm marker => exit 0 immediately.
AskUserQuestion is used across every session and skill; this guard must never
touch a non-swarm ask. Only an active swarm arms it.

FAIL-OPEN: any internal error allows the ask but emits a visible systemMessage,
same posture as path_guard.py. A broken guard must never wedge a session.
"""

import glob
import json
import os
import sys
import time

MARKER_FILENAME = ".swarm-active.json"
FRESH_SECONDS = 300          # brief must have landed within 5 min of the ask
MIN_BYTES = 400              # a real brief, not a one-line stub
STALE_MARKER_SECONDS = 6 * 3600  # a crashed run's leftover marker => step aside


def emit(obj):
    sys.stdout.write(json.dumps(obj))
    sys.stdout.write("\n")


def find_marker(cwd):
    for base in (os.environ.get("CLAUDE_PROJECT_DIR"), cwd):
        if base:
            candidate = os.path.join(base, MARKER_FILENAME)
            if os.path.isfile(candidate):
                return candidate
    return None


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return  # Not our data / unparseable payload: fail open silently.

    cwd = payload.get("cwd") or os.getcwd()
    marker_path = find_marker(cwd)
    if marker_path is None:
        return  # No active swarm: TOTAL no-op.

    # Stale marker from a crashed run => step aside loudly, don't gate.
    if time.time() - os.path.getmtime(marker_path) > STALE_MARKER_SECONDS:
        emit({"systemMessage": (
            "gate-brief-guard: stale %s (>6h old) ignored; delete it if no "
            "swarm is running." % MARKER_FILENAME)})
        return

    with open(marker_path, "r", encoding="utf-8") as fh:
        marker = json.load(fh)
    run_folder = marker.get("run_folder")
    if not run_folder or not os.path.isdir(run_folder):
        emit({"systemMessage": (
            "gate-brief-guard: marker present but run_folder missing/invalid "
            "(%r) — allowing ask (degraded)." % run_folder)})
        return

    now = time.time()
    fresh = [
        b for b in glob.glob(os.path.join(run_folder, "gate-*-brief.md"))
        if os.path.getsize(b) >= MIN_BYTES
        and now - os.path.getmtime(b) <= FRESH_SECONDS
    ]
    if fresh:
        return  # A real, just-written gate brief exists: allow the ask.

    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "No Naked Gate: before this gate ask, write the gate brief to "
                "%s/gate-<A|B>-brief.md (>= %d bytes: decision, each option = "
                "what it is + its tradeoff, recommendation + why, reversibility) "
                "AND render that same brief in the conversation. Then retry the "
                "question. See shared/pipeline-conventions.md."
                % (run_folder, MIN_BYTES)
            ),
        }
    })


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # Ratified fail-open: never crash the session.
        try:
            emit({"systemMessage": (
                "gate-brief-guard degraded (internal error: %s); ask allowed "
                "without gate-brief enforcement." % exc)})
        except Exception:
            pass
    sys.exit(0)
```

### 2. Wire it in — `plugins/spire-pipeline/hooks/hooks.json`

Add a second PreToolUse entry matched on `AskUserQuestion`, using the same
python fallback chain as the path guard:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if python3 -c \"\" >/dev/null 2>&1; then python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/path_guard.py\"; elif python -c \"\" >/dev/null 2>&1; then python \"${CLAUDE_PLUGIN_ROOT}/hooks/path_guard.py\"; elif py -3 -c \"\" >/dev/null 2>&1; then py -3 \"${CLAUDE_PLUGIN_ROOT}/hooks/path_guard.py\"; else echo \"path-guard: no working Python found (python3/python/py) - guard INACTIVE, prose write rules apply\" >&2; exit 0; fi"
          }
        ]
      },
      {
        "matcher": "AskUserQuestion",
        "hooks": [
          {
            "type": "command",
            "command": "if python3 -c \"\" >/dev/null 2>&1; then python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/gate_brief_guard.py\"; elif python -c \"\" >/dev/null 2>&1; then python \"${CLAUDE_PLUGIN_ROOT}/hooks/gate_brief_guard.py\"; elif py -3 -c \"\" >/dev/null 2>&1; then py -3 \"${CLAUDE_PLUGIN_ROOT}/hooks/gate_brief_guard.py\"; else echo \"gate-brief-guard: no working Python found - guard INACTIVE, prose gate rules apply\" >&2; exit 0; fi"
          }
        ]
      }
    ]
  }
}
```

### 3. `design-swarm/SKILL.md` edits

- **Non-negotiable #8 (Never go dark)** or a new **#9**: add "The gate brief is
  mechanically enforced — see Gate A/B. A naked gate ask is blocked by
  `gate_brief_guard.py`."
- **S0 — Frame**, at "Create the run folder": append — *"and write the marker
  `${CLAUDE_PROJECT_DIR}/.swarm-active.json` = `{\"run_folder\": \"<abs run
  folder>\"}` so the gate-brief guard is armed for this run."*
- **Gate A** (line ~69): append — *"Write this brief to
  `<run-folder>/gate-A-brief.md` as the act immediately before the ask (the
  gate-brief guard blocks the `AskUserQuestion` otherwise), then render the same
  content in the conversation."*
- **Gate B** (line ~88): same, `gate-B-brief.md`.
- **S4/S5 — HALT**: append — *"Delete `${CLAUDE_PROJECT_DIR}/.swarm-active.json`
  so the guard disarms."*

### 4. `shared/pipeline-conventions.md` — No Naked Gate section

Append one paragraph under the existing rule: *"Mechanical backstop (design-
swarm): `hooks/gate_brief_guard.py` denies an `AskUserQuestion` during an active
swarm run unless a fresh `gate-*-brief.md` (≥ 400 B, < 5 min old) exists in the
run folder. The prose rule remains the spec; the hook is defense-in-depth on the
one surface (`AskUserQuestion`) where the maiden-run and 2026-08-06 failures
occurred. Same no-op / fail-open posture as the path guard."*

### 5. Version + changelog

Bump plugin to **0.4.2** (or 0.5.0 if you treat a new enforcement surface as
minor). Changelog entry: *"Gate-brief guard: mechanical PreToolUse enforcement
of No Naked Gate on `AskUserQuestion` (design-swarm), after prose-only
enforcement skipped the brief on a live run 2026-08-06."* Bump design-swarm
version tag.

## Acceptance (probe-verified 2026-08-06, 8/8)

Run these against the hook; all must pass before deploy:

| # | Setup | Expected |
|---|---|---|
| 1 | no marker | allow **and emit nothing** (true no-op) |
| 2 | marker, no brief | deny |
| 3 | marker, brief < 400 B | deny |
| 4 | marker, real fresh brief | allow |
| 5 | marker, brief > 5 min old | deny |
| 6 | marker > 6 h old (crashed run) | allow (step aside) |
| 7 | malformed stdin payload | allow, silent fail-open |

## Deployment (operator act — cloud can't push)

The fix reaches live runs only after commit + push + plugin re-sync. This cloud
session cannot push (git proxy denies unauthorized repos) and cannot do
device-side git writes (the mounted `.git/index.lock` can't be unlinked — it is
currently present and wedging git). Sequence, run locally on alita-pc:

1. **Clear the stale lock:** `del D:\Code\spire-skills\.git\index.lock`
2. **Kill the CRLF noise first** so the real diff is reviewable — e.g.
   `git -C D:\Code\spire-skills add --renormalize .` (or checkout the churned
   files) so `git status` shows only the real change.
3. Confirm `gate_brief_guard.py` is in `plugins/spire-pipeline/hooks/` (this
   session drops it there) and apply edits 2–5 above.
4. `git add -A && git commit -m "0.4.2: gate-brief guard — mechanical No Naked Gate on AskUserQuestion"`
5. `git push`
6. Re-sync the plugin (version bump makes the new hook load); start a fresh
   design-swarm to confirm a naked Gate A is now blocked.

## Comparison Discipline / earn-the-complexity

- **Wash?** No existing surface enforces this — `path_guard.py` matches
  `Write|Edit` only. New capability, not a rebuild.
- **Differentiator:** the one hook that turns the twice-failed prose rule into a
  hard stop, on exactly the tool where it failed.
- **Cost:** one additive ~90-line hook + a one-line marker write at S0 and one
  brief-file write per gate (same muscle as digests) + marker delete at HALT.
  No new dependency; same fail-open/no-op invariants as the proven guard.
- **Loss:** a stale marker after a hard crash gates the next ask in that project
  until the 6 h window or a manual delete — bounded, visible, warned.
