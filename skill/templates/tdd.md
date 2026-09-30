# {{product}} — Technical design
<!-- ipq:schema version="2" -->

**Answers:** how the system works, and why it was built that way.
**Look elsewhere for:** what it must do ([prd](prd.md)), what users see
([ux](ux.md)), when it ships ([roadmap](roadmap.md)), how it is run
([runbook](runbook.md)).

<!-- ipq:record id="T-[A-Z0-9]+" in="Components" fields="Responsibility*; Requirements@prd; Depends on; Detail" -->
<!-- ipq:record id="ADR-\d{4}" in="Decision records" fields="Status*=proposed|accepted|superseded|rejected; Date*; Supersedes; Superseded by" -->

## Summary
<!-- The system in 150 words or fewer: what it is, the shape of the
     architecture, and the two or three decisions that matter most. -->

TBD.

## Contents
<!-- ipq:generated -->

## At a glance
<!-- ipq:generated -->

## Context and constraints
<!-- The requirements, quality goals, and limits that drive the design. Link
     to prd; do not restate it. -->

TBD.

## Architecture
<!-- The system on one page: its parts, how data flows between them, and
     the boundaries that matter. Add a diagram with a text description. -->

TBD.

## Components
<!-- One record per component: what it is responsible for, its interfaces,
     and its failure behavior. When a component needs more than about 400
     words, move the detail to docs/tdd/<component>.md and link it from the
     Detail field.

<a id="t-ingest"></a>
### T-INGEST — Statement ingestion

- **Responsibility:** parse bank exports into ledger transactions
- **Requirements:** [R-CORE-01](prd.md#r-core-01)
- **Depends on:** [T-STORE](#t-store)
- **Detail:** [tdd/ingest.md](tdd/ingest.md)
-->

TBD.

## Data model
<!-- ipq:optional -->

## Interfaces
<!-- ipq:optional -->
<!-- APIs, events, and contracts other systems depend on. -->

## Quality attributes
<!-- ipq:optional -->
<!-- How the design meets performance, reliability, security, privacy, and
     cost goals. -->

## Failure modes
<!-- ipq:optional -->

## Rollout and rollback
<!-- ipq:optional -->
<!-- The design that makes release and reversal safe. Dates belong in the
     roadmap; procedures belong in the runbook. -->

## Open questions
<!-- ipq:optional -->

## Decision records
<!-- Architecture decision records, newest first. Each body covers context,
     the decision, alternatives considered, and consequences. When a record
     is superseded, set its Status and link its successor; do not delete it.
     This section is last because it serves people changing the system, not
     people learning it.

<a id="adr-0001"></a>
### ADR-0001 — Store transactions as an append-only log

- **Status:** accepted
- **Date:** 2026-01-15
-->

TBD.
