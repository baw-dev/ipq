# JinkiesList — Offline sync

**Answers:** how a device's changes reach the server and other devices, and
how conflicts are found.
**Part of:** [T-SYNC](../tdd.md#t-sync), which owns this material.

## Summary

Each device numbers its changes and keeps them in an outbox until the server
confirms them. The server applies each device's operations in sequence and
broadcasts them. Two operations conflict only when they change the same field
of the same item from the same starting value; the member then chooses.

## Contents

- [Summary](#summary)
- [The outbox](#the-outbox)
- [Applying operations](#applying-operations)
- [Conflicts](#conflicts)

## The outbox

A change is written to the local store and the outbox in one transaction, so
the screen updates at once. The outbox sends operations in sequence order and
removes each one when the server confirms it.

## Applying operations

The server applies operations from one device in sequence order and ignores
any sequence number it has already applied, so resending is always safe.

## Conflicts

An operation carries the value it replaced. If the server's current value
differs, and the field is a name or quantity, the server records a conflict
instead of applying it. Checking an item off never conflicts.
