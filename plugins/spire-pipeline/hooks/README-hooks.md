# Pipeline hooks — mechanical enforcement layer

## What the path guard does

`path_guard.py` is a PreToolUse hook on `Write|Edit`. When a pipeline run is
active, it canonicalizes each write target (resolving symlinks, including
through not-yet-existing paths) and checks it against the run's declared
staging ring and operator-granted paths:

- **Inside** the ring or a grant: the write proceeds silently.
- **Outside**, `mode: "block"` (default): the hook returns
  `permissionDecision: "ask"` — interactive sessions prompt the operator;
  non-interactive contexts treat it as not-allowed. Block-and-park: grant the
  path in the grants file, or park the row.
- **Outside**, `mode: "warn"`: the write proceeds with a visible
  `systemMessage` warning.

## Scope limit

**The guard sees Write/Edit tool calls only.** It is registered on the
`Write|Edit` PreToolUse matcher and nothing else — a write made through
`Bash` (redirection, `cp`, `mv`, a script the agent shells out to) or through
any other tool is NOT intercepted, mechanically, by this hook. The conductor
skill's prose write-toolchain rule (WRITE PATH, D8: "never ad-hoc local
editing tools or shell redirection") is what covers those paths — this is
defense-in-depth, stated plainly: the mechanical layer and the prose layer
cover different tool surfaces, and only the union of both is the real
boundary.

## The no-op invariant

**No grants file → the hook is a total no-op (exit 0 immediately).** The
plugin never interferes with normal sessions where no pipeline run is active.
An unparseable grants file also allows the write, but emits a one-line
warning. Any internal error in the guard itself fails open with a visible
degradation notice — the guard never crashes or blocks a session on its own
bugs.

## Grants file schema

`${CLAUDE_PROJECT_DIR}/.pipeline-grants.json` (fallback: `<cwd>/.pipeline-grants.json`),
written by the conductor at intake:

```json
{
  "schema_version": 1,
  "run_id": "run-2026-08-04-example",
  "ring": ["/abs/path/to/staging-ring-root"],
  "grants": ["/abs/path/to/operator-granted/file-or-dir"],
  "fixtures": {
    "unit-tests": {"cmd": ["python3", "-m", "pytest", "-q"], "cwd": "/abs/repo"}
  },
  "mode": "block"
}
```

- `ring`: staging-ring roots (absolute paths).
- `grants`: operator-granted out-of-ring paths (files or directories).
- `fixtures`: operator-ratified named test commands — argv arrays, never
  shell strings. Consumed by `scripts/probe_runner.py fixture <name>`.
- `mode`: `"block"` (default) or `"warn"`.

## Requirements

The hook and the companion scripts require `python3` on PATH. Honest caveat:
**without python3 the hook cannot run, and enforcement degrades to the v0.1
prose-only posture** — the skills' written rules still apply, but nothing
mechanically checks writes against the ring.
