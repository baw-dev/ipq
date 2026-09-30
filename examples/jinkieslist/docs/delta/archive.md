# JinkiesList — Closed delta entries

**Answers:** the full text of every closed disagreement, as it stood when it
closed, with any later corrections marked.
**Part of:** [delta](../delta.md), whose Closed section lists each entry in one line.

## Summary

Three disagreements were closed during M1. Each was settled in the document
that owns the answer, which the entry links.

## Contents

- [Summary](#summary)
- [Entries](#entries) · 3 entries

## Entries

<a id="d-003"></a>
### D-003 — Invitation expiry differs between prd and build

- **Owner:** Daphne
- **Waits on:** decision
- **Canonical source:** [R-LIST-03](../prd.md#r-list-03)
- **Found:** 2026-08-21

The prd said invitation links last 30 days; the build expired them after 7.
Product ruled for 7 days, and the prd changed to match.

<a id="d-002"></a>
### D-002 — Offline conflicts lost edits

- **Owner:** Fred
- **Waits on:** work
- **Canonical source:** [R-LIST-02](../prd.md#r-list-02)
- **Found:** 2026-08-03

Two phones renaming one item offline kept only the later name, breaking
acceptance criterion 3. Resolved by [ADR-0002](../tdd.md#adr-0002).

*Corrected 2026-08-19: the loss affected quantities as well as names.*

<a id="d-001"></a>
### D-001 — Sync target differs between ux and prd

- **Owner:** Daphne
- **Waits on:** decision
- **Canonical source:** [R-LIST-01](../prd.md#r-list-01)
- **Found:** 2026-07-29

The ux draft said changes appear instantly; the prd said within 3 seconds.
The prd wins; ux now describes the pending-sync state.
