# Resume Walkdown — ordering and spot-check detail

<!-- REFERENCE FILE — extracted verbatim from conductor/SKILL.md D4. The core
     rule (write a walkdown note before dispatch resumes) stays in D4; read
     this file when you need the reconstruction-ordering mechanics or the
     Vouched spot-check detail behind that note. -->

The walkdown reconstructs claimed/parked rows in an order DERIVED from downstream fan-out read off the existing dependency graph (the `Consumed-from:` backlinks, D6) — never by document order and never by an asserted `Precedence:` field (Infer-Don't-Require; a conductor-asserted precedence field was considered and rejected, item 36). The walkdown also re-runs ONE sampled Vouched inspection (the verbatim-quote check from WRITE PATH) per resume as a spot-check line — not a full re-audit, one sample. A persistently 100% agreement rate across many spot-checks is itself the strongest false-positive signal; real independent review occasionally disagrees (item 35).
