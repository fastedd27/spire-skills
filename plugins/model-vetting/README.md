# model-vetting

Two paired skills for looking at an AI model **before** you adopt it: a fast triage
pass and a deep static read. Both are static — neither one ever runs code that came
out of the artifact, and neither one clears it.

The honest framing up front: this is a negligence detector. It reliably catches
sloppy and careless code and raises the cost of an attack. It is not a security audit,
it does not prove an artifact is clean, and no output it produces is a clearance.

## The two skills

**`model-scorecard` — the triage pass.** Point it at a public HuggingFace repo. It
reads the public API file manifest and `config.json` with `curl` and `jq` — no token,
no account, no weight download — and answers one question fast: *what could this thing
do to me when it loads?* It detects the weight format (safetensors / GGUF vs the
pickle family), detects whether the model runs custom code on load
(`trust_remote_code`), and assigns a coarse `(format, loader)` tier with a
plain-language card:

| Tier | What it means |
|---|---|
| **E** | Non-executing weights, no custom code. The low-risk case. |
| **D** | Non-executing weights, but runs custom code on load. A static look can't clear it. |
| **C** | Non-safetensors binary weights. Pickle-family and Keras `.h5` can execute code on load — hard flag. Flax `.msgpack` is data-only and sits here by conservatism, which the card says out loud. |
| **C?** | Unrecognized weight format. Fails **up**, never down. |

Blast radius is a property of the format and its loader, not of the model's
popularity. A ten-million-download model shipped in a pickle format is still Tier C —
reputation cannot lower the tier, and the card says so.

**`model-eval` — the deep pass.** For a model that ships custom code, or a model
folder already on your disk (private, air-gapped, already downloaded). It runs a
deterministic collector (downloads code and text only, never weights), identifies
which files actually run on load, then writes a behavioral claim about that
code **twice** — once from the full source, once ignoring every comment and docstring.
Divergence between the two is a finding on its own: the artifact's prose was steering
the reader. The claim is then cross-checked against the collector's ground-truth call
graph, so "no network calls" beside a network import in a load-path file comes out as
a loud, deterministic contradiction rather than a judgment call.

It traces whether model-generated output can reach a dangerous sink, scores against a
fixed rubric on three tracks kept unfused (Provenance / Artifact / Instruction —
never averaged into one number), and produces a report that leads with a decision a
non-technical reader fully understands, with the developer-grade evidence underneath.

## How they fit together

Triage first, deep pass only when triage says you need it.

```
model-scorecard  →  Tier E  →  done (low-risk case; still not a security scan)
                 →  Tier C / C? / D  →  model-eval  →  report + scoped human read
```

The scorecard is designed to be cheap enough to run on every candidate. `model-eval`
is the pass you spend real time on, and its output always ends in a residue list —
the specific contradictions, opaque call targets, and unverified claims a human still
has to look at.

## What these deliberately don't do

- **They never execute anything from the artifact.** The collector and the
  claim-writing step read text and emit structure; they take no filesystem, network,
  or downstream action driven by artifact content. That's the floor under
  evaluator-injection: the artifact's prose can bias a claim, but it can't make the
  pipeline *do* something.
- **They never issue a clearance.** There is no "pass". A code-bearing artifact always
  routes to a human read.
- **`model-eval` is static-only, so a code-execution artifact gets a disclaimer of
  opinion.** When the artifact can execute code (tier A/B/C) and was seen static-only,
  the tool refuses to state a confidence-bearing rating. That refusal is the honest
  answer, not a bug — the declared-vs-exercised differential that would earn a rating
  doesn't exist yet.
- **No blended safety score, ever.** Three tracks stay separate. A strong reputation
  next to a red code read is exactly the case these exist to make un-hideable.
- **Silence is not safety.** A quiet scan, a missing signal, an uncontradicted claim —
  none of them is evidence the artifact is fine, and the output says so in plain words.
- **Pickle scanning is delegated, not reimplemented.** The scorecard detects that a
  pickle-family format is *present*; the real opcode-level check belongs to
  `modelscan` / `picklescan`. Same for provenance attestation (SLSA-style tooling).

## Quick usage

Both skills trigger from plain requests — no slash command needed.

- **Scorecard:** "is this model safe to pull?", "quick check on `owner/repo` before I
  use it", "scorecard this HuggingFace model". Takes an `owner/repo` or a HuggingFace
  URL.
- **Deep pass:** "evaluate / vet / audit this model", "should we adopt `owner/repo`?",
  or automatically as the follow-up when the scorecard returns tier C or D. Takes an
  `owner/repo`, a URL, or **a local model folder path**, plus an optional risk tier
  (1 casual · 2 internal tooling · 3 production; default 2).

`skills/model-eval/EXAMPLE-baidu-Unlimited-OCR.md` is a worked report in the required
shape — read it if you want to know what you get back before you run anything.

## Requirements

| | Needs | Network |
|---|---|---|
| `model-scorecard` (`scripts/scorecard.sh`) | `bash`, `curl`, `jq` | yes — public HF API |
| `model-eval` collector (`scripts/collect_signals.sh`), HF mode | `bash`, `curl`, `jq`, `python3` (stdlib only) | yes — public HF API, code and text files only |
| `model-eval` collector, local mode (`MAE_LOCAL_DIR=<folder>`) | `bash`, `python3` (stdlib only) | no |
| `model-eval` fixtures (`fixtures/run_fixtures.sh`) | `bash`, `jq`, `python3` | no |

No tokens or accounts are required anywhere. Both scripts will use `HF_TOKEN` for
higher rate limits if it happens to be set in the environment, and work fine
anonymously if it isn't. `python3` is stdlib-only — no pip installs, no virtualenv.

There is no config layer in this plugin. Install it and use it.

## Verifying the analyzer still fires

`bash skills/model-eval/fixtures/run_fixtures.sh` generates a small corpus with known
properties (a benign custom-code model, a module whose docstring contradicts its
imports, an obfuscated `getattr`, a `torch.load`, a sink in a non-load-path script,
pickle weights), runs the collector against each offline, and asserts the analyzer
catches what it's supposed to catch. No network. Run it after any change to the
collector.

## Install

```
/plugin marketplace add fastedd27/spire-skills
/plugin install model-vetting@spire-skills
```

Desktop / Cowork: Settings → Plugins → add the marketplace `fastedd27/spire-skills`,
then install **model-vetting**. Skills load at session start, so open a fresh session
after installing or updating.

## Versioning

Plugin version lives in `.claude-plugin/plugin.json`; release history is in
[CHANGELOG.md](CHANGELOG.md). Scoring behavior is governed by
`skills/model-eval/references/rubric.md` — treat a change there as a behavior change
and note it in the changelog.

## Credits

Built on Claude (Anthropic) tooling. From **The Spire Library**
(https://thespirelibrary.com). Both skills are the model-artifact siblings of a
repo-oriented scorecard/eval pair; pickle-opcode scanning and provenance attestation
are delegated to the existing tools that own them (`modelscan` / `picklescan`,
SLSA-style checks) rather than rebuilt here.

## License

MIT — see [LICENSE](LICENSE).
