# {{product}} — Reconciliation
<!-- ipq:schema version="2" -->

**Answers:** where the documents and the product disagree, and who decides.
**Look elsewhere for:** the resolved truth, which lives in the document that
owns it.

<!-- ipq:record id="D-\d{3,}" in="Open" fields="Owner*; Waits on*=decision|work|external; Decides; Canonical source*; Found*; Blocks; Meanwhile; Escalate by; Follow-up" -->
<!-- ipq:condensed id="D-\d{3,}" in="Closed" dates="found; closed" -->

## Summary
<!-- The open disagreements in 150 words or fewer: how many, which block a
     milestone, and which wait on a decision. -->

TBD.

## Contents
<!-- ipq:generated -->

## At a glance
<!-- ipq:generated -->

## Open
<!-- One record per disagreement. The body states the two things that
     disagree, the evidence for each, and the impact. It never states the
     resolution: that goes in the owning document, and the entry closes.
     Waits on says what has to happen next: a decision, work, or someone
     outside the team. Decides names who holds the decision rights, which
     may differ from the Owner who chases it. Meanwhile says what work may
     go ahead while the entry is open, or `nothing`. Escalate by is the
     date after which the entry goes to whoever the Decides holder answers
     to. An entry that blocks a milestone needs a Decides.

<a id="d-001"></a>
### D-001 — Import timeout differs between prd and tdd

- **Owner:** engineering lead
- **Waits on:** decision
- **Decides:** product owner
- **Canonical source:** [R-CORE-01](prd.md#r-core-01)
- **Found:** 2026-10-01
- **Blocks:** [M1](roadmap.md#m1)
- **Meanwhile:** import work continues against the prd's 10 s target
- **Escalate by:** 2026-10-15
- **Follow-up:** [B-004](backlog.md#b-004)
-->

TBD.

## Closed
<!-- ipq:optional -->
<!-- Resolved entries, newest first, one line each, 60 words or fewer: what
     was decided and where it now lives.

- <a id="d-001"></a>**D-001** Import timeout — prd wins; tdd updated in [T-INGEST](tdd.md#t-ingest) · found 2026-10-01 · closed 2026-10-03

Under the archive history policy the full entry moves to delta/archive.md,
keeping its anchor; otherwise git keeps it. -->
