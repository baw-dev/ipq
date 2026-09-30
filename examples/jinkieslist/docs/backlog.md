# JinkiesList — Backlog

**Answers:** what is being worked on now, what is next, and what is blocked.
**Look elsewhere for:** requirements ([prd](prd.md)), design ([tdd](tdd.md),
[ux](ux.md)), milestone dates ([roadmap](roadmap.md)).

## Summary

Two M2 items are in progress: moving bought items to the pantry and the
expiring-soon view. Staples are next. Expiry reminders are blocked on the
notification decision in [D-004](delta.md#d-004). Meal planning waits for M3.

## Contents

- [Summary](#summary)
- [Now](#now) · 2 entries
- [Next](#next) · 2 entries
- [Blocked](#blocked) · 1 entry
- [Later](#later) · 1 entry
- [Definition of done](#definition-of-done)
- [Done](#done) · 8 entries

## Now

<a id="b-012"></a>
### B-012 — Offer to add checked items to the pantry

- **Milestone:** [M2](roadmap.md#m2)
- **Requirement:** [R-PANTRY-01](prd.md#r-pantry-01)
- **Design:** [T-PANTRY](tdd.md#t-pantry)
- **UX:** [FLW-01](ux.md#flw-01)
- **Owner:** Fred
- **Estimate:** 3 days
- **Done when:** [QA-PANTRY-01](qa.md#qa-pantry-01) has evidence

<a id="b-013"></a>
### B-013 — Expiring-soon section on the pantry screen

- **Milestone:** [M2](roadmap.md#m2)
- **Requirement:** [R-PANTRY-02](prd.md#r-pantry-02)
- **Design:** [T-PANTRY](tdd.md#t-pantry)
- **UX:** [SCR-02](ux.md#scr-02), [VR-01](ux.md#vr-01)
- **Owner:** Velma
- **Estimate:** 2 days
- **Done when:** [QA-PANTRY-02](qa.md#qa-pantry-02) has evidence

## Next

<a id="b-014"></a>
### B-014 — Staples restock the list

- **Milestone:** [M2](roadmap.md#m2)
- **Requirement:** [R-PANTRY-03](prd.md#r-pantry-03)
- **Design:** [T-PANTRY](tdd.md#t-pantry)
- **UX:** [SCR-04](ux.md#scr-04)
- **Owner:** TBD
- **Estimate:** 4 days
- **Done when:** [QA-PANTRY-04](qa.md#qa-pantry-04) has evidence

<a id="b-015"></a>
### B-015 — Default expiry dates by category

- **Milestone:** [M2](roadmap.md#m2)
- **Requirement:** [R-PANTRY-02](prd.md#r-pantry-02)
- **Design:** no tdd needed
- **Owner:** TBD
- **Done when:** new pantry entries in the ten commonest categories get a date

## Blocked

<a id="b-016"></a>
### B-016 — Daily expiry reminder

- **Milestone:** [M2](roadmap.md#m2)
- **Requirement:** [R-PANTRY-02](prd.md#r-pantry-02)
- **Design:** TBD
- **Owner:** Velma
- **Blocked by:** [D-004](delta.md#d-004)
- **Done when:** [QA-PANTRY-03](qa.md#qa-pantry-03) has evidence

## Later

<a id="b-017"></a>
### B-017 — Weekly meal plan

- **Milestone:** [M3](roadmap.md#m3)
- **Requirement:** [R-PLAN-01](prd.md#r-plan-01)
- **Design:** TBD
- **Owner:** TBD
- **Done when:** TBD

## Definition of done

An item is done when its code is merged, its qa rows have evidence, its
owning documents describe what was built, and `ipq.py check` reports no new
errors.

## Done

- <a id="b-011"></a>**B-011** Pantry data model — [R-PANTRY-01](prd.md#r-pantry-01) · [M2](roadmap.md#m2) · done 2026-09-19
- <a id="b-010"></a>**B-010** Resolve conflicts on the list screen — [R-LIST-02](prd.md#r-list-02) · [M1](roadmap.md#m1) · done 2026-08-29
- <a id="b-009"></a>**B-009** Revoke invitation links — [R-LIST-03](prd.md#r-list-03) · [M1](roadmap.md#m1) · done 2026-08-27
- <a id="b-008"></a>**B-008** Invitation links — [R-LIST-03](prd.md#r-list-03) · [M1](roadmap.md#m1) · done 2026-08-22
- <a id="b-007"></a>**B-007** Operation-based sync, per [ADR-0002](tdd.md#adr-0002) — [R-LIST-02](prd.md#r-list-02) · [M1](roadmap.md#m1) · done 2026-08-18
- <a id="b-006"></a>**B-006** Offline outbox — [R-LIST-02](prd.md#r-list-02) · [M1](roadmap.md#m1) · done 2026-08-12
- <a id="b-005"></a>**B-005** Live updates over websocket — [R-LIST-01](prd.md#r-list-01) · [M1](roadmap.md#m1) · done 2026-08-08
- <a id="b-004"></a>**B-004** List screen — [R-LIST-01](prd.md#r-list-01) · [M1](roadmap.md#m1) · done 2026-08-04
