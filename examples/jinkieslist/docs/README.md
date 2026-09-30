# JinkiesList — Documentation

**Answers:** which document to read for a question, and what the words mean.
**Look elsewhere for:** everything else; this page only points.

## Summary

JinkiesList is a shared grocery list and pantry tracker for households. Start with
the [prd](prd.md) Summary for what it is and why, then the [roadmap](roadmap.md)
Status for where it stands.

## Contents

- [Summary](#summary)
- [Find an answer](#find-an-answer)
- [Identifiers](#identifiers)
- [Glossary](#glossary)

## Find an answer

| To learn | Read |
|---|---|
| What we are building, and why | [prd](prd.md), Summary |
| What a screen does | [ux](ux.md), Screen inventory |
| How a part of the system works | [tdd](tdd.md), Components |
| Why it was built that way | [tdd](tdd.md), Decision records |
| What ships next | [roadmap](roadmap.md), Status |
| What is being worked on | [backlog](backlog.md), Now |
| Whether a requirement is proved | [qa](qa.md), Coverage |
| What to do when something breaks | [runbook](runbook.md), Playbooks |
| Where the documents are wrong | [delta](delta.md), Open |

## Identifiers

| Kind | Form | Lives in |
|---|---|---|
| Requirement | `R-<AREA>-<NN>`; areas `LIST`, `PANTRY`, `PLAN`, `STORE` | [prd](prd.md) |
| Screen, flow, component, visual rule | `SCR-<N>`, `FLW-<N>`, `CMP-<N>`, `VR-<N>` | [ux](ux.md) |
| Component | `T-<NAME>` | [tdd](tdd.md) |
| Decision record | `ADR-<NNNN>` | [tdd](tdd.md) |
| Milestone | `M<N>` | [roadmap](roadmap.md) |
| Backlog item | `B-<NNN>` | [backlog](backlog.md) |
| Check | `QA-<AREA>-<NN>` | [qa](qa.md) |
| Playbook | `RB-<NN>` | [runbook](runbook.md) |
| Disagreement | `D-<NNN>` | [delta](delta.md) |

## Glossary

- **Household:** the people who share one list and one pantry. A person can
  belong to one household.
- **Item:** a thing to buy, with a name, an optional quantity, and a checked
  state.
- **List:** a household's items still to buy. Each household has one list.
- **Pantry:** a household's record of what it has at home, with quantities
  and, where known, expiry dates.
- **Staple:** a pantry entry the household always wants in stock. When a
  staple runs out, JinkiesList adds it to the list.
- **Sync:** copying changes between a member's device and the server so every
  member sees the same list.
