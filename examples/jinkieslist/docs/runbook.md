# JinkiesList — Operations

**Answers:** how the system is run, watched, and repaired.
**Look elsewhere for:** how it works ([tdd](tdd.md)), what ships when
([roadmap](roadmap.md)).

## Summary

One API service and one managed Postgres database run in a single cloud
region. Fred and Velma share on-call, a week each. Start with the sync-lag
dashboard: almost every user-visible problem shows there first.

## Contents

- [Summary](#summary)
- [Service overview](#service-overview)
- [Service levels and alerts](#service-levels-and-alerts)
- [On-call and escalation](#on-call-and-escalation)
- [Playbooks](#playbooks) · 2 entries

## Service overview

| Part | Runs on | Owner |
|---|---|---|
| [T-API](tdd.md#t-api) | two containers behind a load balancer | Fred |
| [T-STORE](tdd.md#t-store) | managed Postgres with daily backups kept 14 days | Velma |

## Service levels and alerts

| Objective | Measured as | Alert | Playbook |
|---|---|---|---|
| Changes reach other members fast | 95th percentile sync lag under 3 s, over 1 hour | lag above 10 s for 5 minutes | [RB-01](#rb-01) |
| The API answers | 99.5% of requests succeed, over 30 days | error rate above 2% for 5 minutes | [RB-02](#rb-02) |

## On-call and escalation

The on-call person answers pages within 15 minutes. If the database is at
fault, escalate to the provider's support after 30 minutes.

## Playbooks

<a id="rb-01"></a>
### RB-01 — Changes are slow to reach other members

- **Trigger:** the sync-lag alert fires
- **Impact:** members see stale lists while shopping
- **Component:** [T-SYNC](tdd.md#t-sync)
- **Severity:** 2

1. Open the sync-lag dashboard. If lag rose for every household, go to step 3.
2. If one household is affected, check its operation count; above 10,000,
   run compaction for that household. Expected: lag falls within 5 minutes.
3. Check websocket connections. If they dropped to zero, restart the API
   containers one at a time. Expected: connections recover within 2 minutes.

Rollback: if lag began with a deploy, roll back to the previous release.

<a id="rb-02"></a>
### RB-02 — The API returns errors

- **Trigger:** the error-rate alert fires
- **Impact:** members cannot sync; their phones keep changes in the outbox
- **Component:** [T-API](tdd.md#t-api)
- **Severity:** 1
- **Release:** [M2](roadmap.md#m2)

1. Check the database status page. If it is down, follow the provider's
   incident and escalate after 30 minutes.
2. Otherwise read the API's error log for the commonest error and roll back
   if it began with a deploy.
