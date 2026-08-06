---
name: setup
description: "(v2026-08-06.1) First-run onboarding helper for the spire-pipeline config layer: replays the config discovery order, and either reports on an existing house-config.md (diff mode — read-only) or interviews the operator with two plain questions and writes a minimal starter config. Trigger on: 'setup', 'set up the pipeline', 'configure the pipeline', 'first-run config', 'house-config help', 'help me make a house config' — and 'check my config' / 'audit my config' for diff mode. Explicit invocation ONLY: no other skill calls this, and nothing in any skill's config-load step detects a missing config and routes here. Do NOT trigger for running the pipeline itself (design-swarm / run-list / conductor)."
---

<!-- ENGINE FILE — one source, two cuts. Installation-specific values (path
     roots, hooks, governance rule names, reference docs) are referenced
     generically as `cfg:<key>` and resolved by the config layer:
     `config/house-config.md` (house cut) or `config/house-config.example.md`
     (public example). Shared pipeline vocabulary lives in
     `shared/pipeline-conventions.md`. This file states NO installation-specific
     value anywhere — everything it writes is read from the example config or
     the plugin manifest at runtime, or confirmed by the operator. -->

# Setup — first-run onboarding for the config layer (optional)

**Running with no config file is fully supported** — every key falls back to its documented "Omit →" default and the pipeline runs in safe zero-config mode. This helper is optional convenience: it gets an operator from nothing to a minimal, correct `house-config.md` in one short conversation, or reports on the config they already have. It is invoked explicitly by name, and only by the operator — **no skill in this plugin detects a missing config and invokes setup on its own; the three pipeline skills' config-load step never routes here.**

## Invariants (binding — read before running)

- **I1 — No half-states.** The config is written as ONE whole-file write or not at all. Any abort, at any step, leaves no file behind. There is no partially-written config, ever.
- **I2 — Never overwrite.** An existing `house-config.md` at either discovery location is READ-ONLY in every mode of this skill. Setup never edits, appends to, renames, moves, or replaces an existing config. Found config = diff mode = report and exit.
- **I3 — Parse-tolerance asymmetry.** Heuristic reads of the example config (scanning for `cfg:<key>` tokens, eyeballing table rows) are allowed ONLY on report-only paths that never write. The WRITE path depends on nothing parsed from table geometry: the chosen keys come from the example's Quickstart section, and if that read fails, fail loud — tell the operator to open `config/house-config.example.md` and follow its Quickstart by hand. Never guess keys. Never substitute a table scan for the Quickstart read on the write path.
- **I4 — No engine vocabulary in questions.** The operator-facing questions are phrased in outcome terms (where things live, what survives, project vs machine). Words like staging ring, durable_root, dispatch mechanism, tier, probe, cfg-key do not appear in a question.
- **I5 — Hardcode nothing derivable.** This skill text names no config keys, no key defaults, and no key count. The chosen key set is read from the example config's Quickstart section AT RUNTIME — if the example changes, this skill follows it with no edit here. The plugin version in the generated-by line is read from the plugin manifest at runtime.

## Step 0 — discovery replay

Re-run the README's config discovery order exactly: **(1) project root, (2) home directory; first found wins — project beats home.** Check both locations regardless of the first hit, so shadowing is visible.

**Config found → DIFF MODE (report-only, then exit).** Report three things, touch nothing, and exit:

- **(a) Shadowing.** If BOTH locations hold a `house-config.md`, state which file wins under the discovery order and that the other is shadowed (present but never loaded).
- **(b) Missing keys.** Read the CURRENT example config's key table and list keys present in the example but absent from the operator's config. For each, note whether it has a documented "Omit →" default (absent = fine, running on the default) — and flag any missing key with NO documented default as **action-needed** (those are deny-by-default when a skill hits them).
- **(c) Quickstart coverage.** State which of the example's Quickstart chosen keys are present in the operator's config and which are absent.

The key scan is a soft heuristic over `cfg:<key>` tokens — imperfection is tolerable here precisely because this path never writes (I3). Say so in the report if anything looked malformed. **Diff mode touches nothing. It ends the skill.**

**No config at either location → continue to Step 1.**

## Step 1 — detection, evidence-first

Detect, and record the evidence for, three facts:

1. **Host OS.** BINDING bridge/cloud rule: in a cloud/bridge session, the container's OS is NOT the host OS — a Linux shell in the container proves nothing about the machine the config will live on. Confirm the host OS from **stated evidence** (device-bridge tools present in the session, OS-shaped paths in connected folders, an explicit operator statement) or ASK the operator. **Silent OS inference in an ambiguous session is prohibited.** In a plainly local session, the session's own OS is the evidence — name it.
2. **Hash tool.** Follows from host OS: Windows → `certutil -hashfile <path> SHA256` (because `sha256sum` is absent on stock Windows); macOS/Linux/WSL → `sha256sum`. If the host OS is unconfirmed, this value is unconfirmed too — it inherits the CONFIRM mark in Step 2.
3. **Subagent/dispatch tooling.** Whether the session has subagent/Task-style tooling available for fanning work out, or will run serial in-session.

Every detected value carries a one-line evidence note (what was observed that supports it). A value without evidence is not detected — it is a guess, and guesses go to the operator as questions, not into the config.

## Step 2 — the asks (outcome terms only)

**Two questions in the happy path. No more.** Both phrased in outcome terms (I4):

1. **"Where should things you keep — plans, specs, finished outputs — live?"** Propose the detected candidates: the git repo root, an existing docs directory, the current working directory. The answer becomes the durable location the pipeline lands keeper artifacts in.
2. **"Config next to this project, or one config for your whole machine?"** The answer picks the write location — project root or home directory. Propose project root when the current directory is plausibly a project (a repo, a manifest, a src tree).

On the same confirm step, show every detected value from Step 1, each with its one-line evidence note. Any bridge-ambiguous item (host OS or anything derived from it, unconfirmed) is marked **CONFIRM** and must be explicitly confirmed by the operator before Step 3.

A third question is permitted only if Step 1 found ZERO durable-root candidates to propose — then ask the operator to name a location outright.

## Step 3 — write (minimal + atomic)

Read the example config's **Quickstart section at runtime** to get the chosen key set (I5). If the Quickstart section cannot be found or its chosen keys cannot be read, **fail loud**: stop, write nothing, and tell the operator to open `config/house-config.example.md` and follow its Quickstart by hand. Never guess keys, and never fall back to scanning the key table — the write path does not depend on table geometry (I3).

The file to write contains ONLY:

- A short header: one line saying what the file is (the pipeline's config layer); one pointer line to `config/house-config.example.md` for the full key table; and a plain-prose generated-by line — `generated by spire-pipeline:setup, plugin v<version from the plugin manifest>, <today's date>` — **no hash, no sha256 stamp, nothing machine-verifiable in that line; it is prose.**
- The Quickstart's chosen keys, each with the value confirmed in Step 2. **No other keys. No placeholder values.** A chosen key whose value the operator declined to confirm is OMITTED entirely, never written with a placeholder — omission means its documented default, which is exactly correct.
- One comment line: `every other key is deliberately omitted = its documented omit-default`.

**No-clobber, no half-states (I1 + I2):** immediately before the write, re-assert that no `house-config.md` exists at the confirmed location (the world may have changed since Step 0 — another session, a sync, the operator). If one now exists, abort: report it and exit with nothing written. The write itself is ONE whole-file write. Any failure or abort at any point in this step leaves no file.

## Step 4 — prove it

1. **Replay discovery** (same order as Step 0) and assert the first-found file IS the file just written — the shadow check. If something else wins the discovery order, say so loudly: the config just written is shadowed and will never load.
2. **Read back** the written keys from the file on disk and show them to the operator.
3. **Show the echo line** the operator will see on the next pipeline skill run: `loaded config from <path>` — so they know what "it worked" looks like.
4. If the confirmed placement is a git repository root, **offer** (never apply unasked) a one-line `.gitignore` append: `house-config.md` — a filled config is personal to the installation and should not ride along in commits.

Then stop. Setup writes one file, proves it loads, and ends — it does not run the pipeline, edit other files, or schedule anything.

## Lineage & credits

- **First cut 2026-08-06** (onboarding design spec, ratified 2026-08-06). Engine file under the one-source rule: house and public cuts share this exact text; only the config layer differs. Version log: the repo's git history (`cfg:refs.version_logs`).
