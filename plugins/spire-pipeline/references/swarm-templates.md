# Design Spec Skeleton — full template

<!-- REFERENCE FILE — extracted verbatim from design-swarm/SKILL.md S4/S5. Read
     this when actually writing the design spec at S4; the core S4/S5 section
     covers the frontmatter-field semantics and the durable-landing rule
     without the copy-in skeleton itself. -->

```
---
title: '<thing> — design spec (design-swarm run)'
project: <KEY>  # any short slug you use to group work; free text
date: YYYY-MM-DD
type: design-spec
status: live
consumed:
remnants:
mode: dispatch | serial_fallback | partial(<detail>)
run_stages: S0–S5, gates A+B held by operator
related_ids: [<owning-project work-item id if minted — field name and id format per cfg:gov.followup_queue>]  # field name follows your cfg:gov.followup_queue scheme; related_ids is the default
ratification: ratified-design, NOT built
---
Goal + hard locks (from S0, as ratified)
Chosen approach + axiom, and why it won (Gate B record)
What was killed and why (one line each — the kills are part of the design's defense)
Salvaged elements folded in
Design detail (the actual spec: components, seams, contracts, sequencing)
Acceptance sketch: how we'll know it works — the concrete signals/checks a build session will turn into stage-2 done-when criteria and probes
Known sacrifices + unpriced risks (from critique, honestly carried)
Build handoff note: "next step is a run-list session; this document is its input. Stage 2 flips this spec's status to consumed and carries the kills forward as a do-not-drift line."
```
