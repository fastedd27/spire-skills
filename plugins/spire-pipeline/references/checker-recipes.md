# Checker Recipes — getting a decorrelated lineage to run the check

<!-- REFERENCE FILE — pointed at by `cfg:dispatch.checker_lineage` in
     config/house-config.example.md. Vendor-neutral, no installation-specific
     values. -->

`cfg:dispatch.checker_lineage` asks for a genuinely different model lineage to
run the decorrelated check (e.g. the context-pack contract's back-translation
check), not just a second call to the same vendor's model. "Decorrelated"
means: a different training lineage, so the checker is unlikely to share the
same blind spot as the drafter. Same-vendor, same-family, or same-weights
calls (even at a different temperature or a fresh context) do not qualify —
they're correlated, not decorrelated.

## What a check prompt carries

Whatever recipe you use, the check prompt is built the same way:

- **The original row text** — the material being checked, verbatim.
- **The worker's restatement** — the drafter's needle list / back-translation
  / claim being checked against the original.
- **Never the corruption key or the expected answer.** The checker's job is
  to compare restatement against original and flag mismatches on its own; if
  it's handed the expected answer it isn't checking anything, it's grading a
  key it was already given. Keep the check prompt to those two artifacts plus
  a short instruction ("does this restatement accurately preserve every
  material fact in the original? name what it drops, adds, or flips") and
  nothing else.

## (a) A second CLI agent

Invoke any non-Claude coding CLI available on the host (a different vendor's
agent tool) on the check prompt as a one-shot, non-interactive call. This
gets you a genuinely different lineage with minimal ceremony if the host
already has such a tool installed and authenticated. Capture the output
verbatim into the receipt; don't paraphrase the verdict.

## (b) Direct API call to another vendor

A single-prompt call to another vendor's API (the check prompt as the entire
input, no system scaffolding beyond the instruction above) is the cleanest
decorrelated check when API access and a key are already available. Cheapest
in wall-clock time, and the easiest to script into `cfg:hooks.*` once it's
been run by hand a few times. Log which vendor/model answered in the receipt
— that's the provenance the decorrelation claim rests on.

## (c) The manual paste loop

No API key, no second CLI — this still works, and it's the proven fallback:
paste the check prompt (original + restatement + instruction) into another
vendor's chat UI in a browser, then paste the verdict back into the run.
Slower and more manual than (a)/(b), but it needs nothing pre-installed and
nothing pre-authenticated, which is why it's the cheapest recipe in terms of
setup cost even though it's the most manual in terms of run cost. Record which
vendor's UI answered, same as (a)/(b).

## (d) Honest fallback: same-model + correlation caveat

If none of (a)–(c) are available, run the check with the same model lineage
that drafted the material, and record a prominent correlation caveat in the
receipt — say plainly that the check is correlated with the draft and may
share its blind spots, and that the result should be weighted accordingly.
This is what `cfg:dispatch.checker_lineage` degrades to when omitted; it is
honest, not disqualifying, as long as the caveat actually ships with the
verdict rather than getting silently dropped.

## Choosing a recipe

Prefer (a) or (b) when the tooling is already there — they're the least
manual per run. Reach for (c) when nothing is pre-wired and this is a
one-off or first-time check. Only fall back to (d) when no other vendor is
reachable at all; don't let (d) become the default just because it's the
path of least resistance — a same-lineage check with a caveat is weaker
evidence than any of (a)–(c), not an equivalent substitute.
