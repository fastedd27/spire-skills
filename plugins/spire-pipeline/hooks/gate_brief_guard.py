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
