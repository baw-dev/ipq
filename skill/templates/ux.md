# {{product}} — Experience and visual design
<!-- ipq:schema version="2" -->

**Answers:** what people see and do: screens, flows, states, visual rules, and
accessibility.
**Look elsewhere for:** why a screen exists ([prd](prd.md)), how it is built
([tdd](tdd.md)), token values (the token source named under Visual rules).

<!-- ipq:record id="SCR-\d+" in="Screens" fields="Purpose*; Requirements*@prd; Roles; Entry; States*" -->
<!-- ipq:record id="FLW-\d+" in="Flows" fields="Goal*; Requirements*@prd; Starts; Ends*" -->
<!-- ipq:record id="CMP-\d+" in="Components" fields="Purpose*; States; Used by" -->
<!-- ipq:record id="VR-\d+" in="Visual rules" fields="Applies to*; Tokens" -->
<!-- ipq:record id="DEC-\d{4}" in="Decision records" fields="Status*=proposed|accepted|superseded|rejected; Date*; Decided by*; Supersedes; Superseded by" -->

## Summary
<!-- The experience in 150 words or fewer: who uses it, the few things they
     come to do, and the principles that shape every screen. -->

TBD.

## Contents
<!-- ipq:generated -->

## At a glance
<!-- ipq:generated -->

## Screen inventory
<!-- One table row per screen: ID linked to its record, name, and purpose.
     The records under Screens hold the detail. -->

TBD.

## Flows
<!-- One record per flow, grouped by what the user is trying to achieve.
     The body lists the starting state, ordered steps, decision points, and
     the outcome.

<a id="flw-01"></a>
### FLW-01 — Import a statement

- **Goal:** get a month of transactions into the household ledger
- **Requirements:** [R-CORE-01](prd.md#r-core-01)
- **Starts:** [SCR-02](#scr-02) with no statements imported
- **Ends:** [SCR-03](#scr-03) showing the imported transactions
-->

TBD.

## Screens
<!-- One record per screen. States lists the states the screen has, and
     marks one that cannot occur `n/a` (for example `offline n/a`). The body
     covers layout and content hierarchy, then one `- **State:**` line per
     listed state, then responsive and accessibility behavior specific to
     this screen.

<a id="scr-01"></a>
### SCR-01 — List

- **Purpose:** see and check off what to buy
- **Requirements:** [R-CORE-01](prd.md#r-core-01)
- **States:** default, empty, loading, error, offline

- **Default:** unchecked items in the order added.
- **Empty:** one line, "Nothing to buy".
- ...
-->

TBD.

## Components
<!-- ipq:optional -->
<!-- One record per shared component: appearance, behavior, and states. -->

## Visual rules
<!-- ipq:optional -->
<!-- Name the authoritative token source first. Then one record per rule:
     where it applies and which tokens it uses. Never copy token values. -->

## Accessibility
<!-- ipq:optional -->
<!-- Rules that apply across screens: keyboard, focus, screen readers,
     contrast, motion. Screen-specific behavior stays with the screen. -->

## Open questions
<!-- ipq:optional -->

## History
<!-- ipq:optional -->
<!-- Superseded design decisions, newest first, one line each. -->

## Decision records
<!-- ipq:optional -->
<!-- Decisions this document owns, newest first: rulings on
     experience and visual design.
     Each body gives the question, the decision (quoted verbatim when it
     was a ruling), and what it changed. Supersede a record; never delete it.

<a id="dec-0001"></a>
### DEC-0001 — The list works one-handed

- **Status:** accepted
- **Date:** 2026-10-01
- **Decided by:** product owner
-->
