# {{product}} — Verification
<!-- ipq:schema version="2" -->

**Answers:** how each requirement is proved, and what evidence exists so far.
**Look elsewhere for:** what counts as correct ([prd](prd.md), [ux](ux.md)),
who is writing tests ([backlog](backlog.md)).

<!-- ipq:table id="QA-[A-Z0-9]+-\d+" in="Coverage" columns="ID*; Verifies*@prd; Check*; Level*=unit|integration|e2e|manual|review; Milestone*@roadmap; Evidence*" -->
<!-- ipq:record id="DEC-\d{4}" in="Decision records" fields="Status*=proposed|accepted|superseded|rejected; Date*; Decided by*; Supersedes; Superseded by" -->

## Summary
<!-- Verification in 150 words or fewer: the approach, how much of the
     current milestone is proved, and the largest gap. -->

TBD.

## Contents
<!-- ipq:generated -->

## At a glance
<!-- ipq:generated -->

## Strategy
<!-- What is tested at which level, and why. -->

TBD.

## Coverage
<!-- One table row per check. The ID cell carries the anchor. Verifies links
     a prd requirement and names the criterion. Evidence is `none` or a link
     to the run record that produced it. A run record in qa/runs/ may name
     what it ran against: `- **Revision:** 1.4.2` (a build, commit, or
     version) and `- **Release:** M2`. A milestone judged at a revision
     counts only evidence naming that revision.

| ID | Verifies | Check | Level | Milestone | Evidence |
|---|---|---|---|---|---|
| <a id="qa-core-01"></a>QA-CORE-01 | [R-CORE-01](prd.md#r-core-01) AC 1 | import a 500-row CSV in under ten seconds | e2e | [M1](roadmap.md#m1) | none |
-->

TBD.

## Environments and automation
<!-- ipq:optional -->

## Non-functional tests
<!-- ipq:optional -->

## Release checklist
<!-- ipq:optional -->
<!-- The checks that gate a release, in order. -->

## Gaps
<!-- ipq:optional -->
<!-- Requirements with no check yet, and why. -->

## History
<!-- ipq:optional -->

## Decision records
<!-- ipq:optional -->
<!-- Decisions this document owns, newest first: rulings on
     what counts as evidence.
     Each body gives the question, the decision (quoted verbatim when it
     was a ruling), and what it changed. Supersede a record; never delete it.

<a id="dec-0001"></a>
### DEC-0001 — Simulator runs do not count for sync checks

- **Status:** accepted
- **Date:** 2026-10-01
- **Decided by:** product owner
-->
