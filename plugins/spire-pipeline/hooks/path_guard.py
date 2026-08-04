#!/usr/bin/env python3
"""PreToolUse path guard for the pipeline staging ring (predict-and-pregrant).

Reads the hook payload on stdin, looks for a machine-readable grants file
(.pipeline-grants.json) at $CLAUDE_PROJECT_DIR or the session cwd, and checks
whether the Write/Edit target resolves inside the declared staging ring or an
operator-granted path.

CRITICAL INVARIANT: if no grants file exists, this hook is a TOTAL no-op
(exit 0 immediately). The plugin must never interfere with normal sessions
where no pipeline run is active.

Failure posture (ratified): the guard itself must never crash the session.
Any internal exception in the guard fails OPEN (exit 0) but emits a visible
systemMessage so the operator knows mechanical enforcement degraded. This is
an honest trade-off: a broken guard silently blocking all writes would be
worse than a broken guard loudly stepping aside.

Exit code is always 0; decisions are conveyed via JSON on stdout
(hookSpecificOutput.permissionDecision "ask" for out-of-ring writes in block
mode, systemMessage for warn mode and degradation notices).
"""

import json
import os
import sys

GRANTS_FILENAME = ".pipeline-grants.json"


def emit(obj):
    """Print a single JSON object on stdout for the hook runner."""
    sys.stdout.write(json.dumps(obj))
    sys.stdout.write("\n")


def find_grants_file(cwd):
    """Locate the grants file: $CLAUDE_PROJECT_DIR first, then session cwd.

    Returns the path if a candidate exists, else None (=> total no-op).
    """
    candidates = []
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        candidates.append(os.path.join(project_dir, GRANTS_FILENAME))
    if cwd:
        candidates.append(os.path.join(cwd, GRANTS_FILENAME))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def canonicalize(path):
    """Resolve symlinks even for paths whose tail does not exist yet.

    Walk up to the deepest existing ancestor (lexists, so a dangling symlink
    still counts and gets resolved), realpath() it, then re-append the
    not-yet-existing components. This catches writes routed "through" a
    symlinked parent directory out of the ring, and writes targeting a
    symlink that itself points out of the ring.
    """
    path = os.path.abspath(path)
    remaining = []
    current = path
    while current and not os.path.lexists(current):
        parent, tail = os.path.split(current)
        if not tail or parent == current:
            break
        remaining.append(tail)
        current = parent
    resolved = os.path.realpath(current)
    for component in reversed(remaining):
        resolved = os.path.join(resolved, component)
    return resolved


def is_under(target, root):
    """True if canonical `target` equals or lies under canonical `root`."""
    try:
        return os.path.commonpath([target, root]) == root
    except ValueError:
        # Different drives / mixed absolute-relative — cannot be inside.
        return False


def main():
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not file_path:
        return  # Nothing to guard.

    cwd = payload.get("cwd") or os.getcwd()
    grants_path = find_grants_file(cwd)
    if grants_path is None:
        return  # No pipeline run active: TOTAL no-op.

    try:
        with open(grants_path, "r", encoding="utf-8") as fh:
            grants_doc = json.load(fh)
        if not isinstance(grants_doc, dict):
            raise ValueError("grants file root is not a JSON object")
    except Exception as exc:  # Unparseable grants: allow, but say so.
        emit({
            "systemMessage": (
                "pipeline path guard: grants file at %s is unparseable (%s); "
                "guard is allowing writes without ring enforcement."
                % (grants_path, exc)
            )
        })
        return

    roots = []
    for key in ("ring", "grants"):
        value = grants_doc.get(key) or []
        if isinstance(value, list):
            for root in value:
                if isinstance(root, str) and root:
                    roots.append(canonicalize(root))

    target = canonicalize(file_path)
    if any(is_under(target, root) for root in roots):
        return  # Inside the ring or a granted path: allow.

    run_id = grants_doc.get("run_id", "unknown")
    mode = grants_doc.get("mode", "block")
    if mode == "warn":
        emit({
            "systemMessage": (
                "pipeline path guard (warn mode): %s resolves outside the "
                "staging ring and granted paths (run %s). Allowed, but this "
                "write was not predicted at intake." % (target, run_id)
            )
        })
        return

    # block mode (default): ask. Interactive sessions prompt the operator;
    # non-interactive contexts treat "ask" as not-allowed — the ratified
    # block-and-park posture.
    emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                "%s resolves outside the pipeline staging ring and granted "
                "paths (run %s). Grant it in %s, or park this row: this "
                "write was not predicted at intake."
                % (target, run_id, GRANTS_FILENAME)
            ),
        }
    })


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # Never crash the session (ratified fail-open).
        try:
            emit({
                "systemMessage": (
                    "pipeline path guard degraded (internal error: %s); "
                    "write allowed without ring enforcement." % exc
                )
            })
        except Exception:
            pass
    sys.exit(0)
