# ipq

[![ci](https://github.com/baw-dev/ipq/actions/workflows/ci.yml/badge.svg)](https://github.com/baw-dev/ipq/actions/workflows/ci.yml)
[![licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

**Answers:** what ipq is, whether it suits your project, and how to start.
**Look elsewhere for:** setup, reference, and the rest: see
[Where to look next](#where-to-look-next).

## Summary

ipq is a skill for Claude Code and local ChatGPT that keeps a repository's
planning documents honest and easy to read, for people and for models. It looks after eight documents under `docs/`, each the
one home for its kind of fact: what is built and why, what people see, how it
works, when it ships, what is next, how it is proved, how it is run, and
where the documents and the product disagree.

Every document follows a template that puts the answer first and the detail
last. Each opens with measurements generated from its own records, so nobody
types a number that can go stale. A small Python tool checks structure,
links, and traces. It proves the documents
agree with each other, not that they are true; accuracy still needs evidence
from the product.

Ask your assistant in plain words; it shows a plan before it changes anything.

<a id="contents"></a><a id="getting-started"></a><a id="using-it"></a>
## Get started

Install ipq into your project from a clone of this repository (use
`chatgpt` for local ChatGPT or Codex):

```bash
./install.sh claude --project /path/to/your/repo
```

Then ask your assistant, in that repository:

| To | Say |
|---|---|
| Start a document set | "Use ipq to set up `docs/` for this project." |
| Bring existing documents into line | "Use ipq to migrate `docs/`. Save every anchor first, and show me a plan." |
| Record a change | "The scope changed: ... Use ipq to update the documents." |
| See where things stand | "Use ipq to refresh the At a glance sections and tell me what changed." |

Every step also works by hand: see [SETUP.md](SETUP.md).

## What it keeps

Eight documents under `docs/`, each the owner of one kind of truth, and an
index that points into them.

| Document | Owns | Its reader asks |
|---|---|---|
| `prd.md` | What is being built, and why | Should this exist? |
| `ux.md` | What people see and do | What does this screen do in each state? |
| `tdd.md` | How it works, and why it was built that way | How does this part work, and why this way? |
| `roadmap.md` | What ships when | What ships next, and what is in its way? |
| `backlog.md` | What is being worked on | Who is doing what, and what is blocked? |
| `qa.md` | How it is proved | Is this requirement proved yet? |
| `runbook.md` | How it is run | Something broke: what do I do? |
| `delta.md` | Where the documents and the product disagree | What do we know is wrong, and who decides? |
| `README.md` | Which document answers which question, and what the words mean | Where do I look? |

## How it keeps them

<a id="coherent-every-fact-has-one-home"></a>**One home for every fact.** A
scope change goes in `prd.md`, not in whichever document mentions it. When
two sources disagree and nobody has decided, the disagreement goes into
`delta.md`, naming who must act.

<a id="standalone-passages-that-are-harder-to-misread-out-of-context"></a>**Passages
that stand alone.** People skim, and models read excerpts. So every claim
names its subject, and every exception sits beside its rule.

<a id="readable-the-answer-first-the-detail-last"></a>**The answer first.**
Each document opens with what it answers, a short Summary, and generated
measurements, so a reader can stop early. This is the roadmap's Milestones
block, from the [JinkiesList](examples/jinkieslist/docs/) example:

<!-- Jinkies! The last clue: every number in a block is generated, so if one looks off, unmask whoever typed it by hand. -->

```text
Milestones: backlog items done and qa checks with evidence

4 milestones · 1 done · 1 active · 1 planned · 1 cut

[x] M1   Shared list     done     2026-09-01
         work    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  7/7
         checks  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  4/4

[>] M2   Pantry          active   2026-10-31  after M1
         work    ▓▓▓▓░░░░░░░░░░░░░░░░░░░░  1/6
         checks  ▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░  1/4
         ! 1 blocked: B-016 · 2 open deltas: D-004, D-006
```

[VISUALS.md](VISUALS.md) shows all ten blocks, and why each earns its place.

## What `check` proves, and what it doesn't

| `check` proves | `check` does not prove |
|---|---|
| Every document has its sections, records, and fields | That what they say is true |
| Links resolve and identifiers are unique | That a linked design actually meets its requirement |
| Every backlog item and check traces to a requirement | That a check tests the right thing |
| Evidence is scoped to a milestone's revision, when one is set | That the product in production matches it |
| Generated sections match their records | That the records are current; ask `check --fresh` |

Accuracy comes from what the documents carry: run records that name the
revision they ran against, a register of disagreements that says who decides
and when each escalates, and reconciliation against the running product.

## What it will not do

- Invent an owner, a date, or an estimate to fill a gap. It writes `TBD` and
  marks the gap.
- Change what you meant, to make two documents agree.
- Claim the product matches the documents without looking at the product.
- Remove or rename an anchor that something might link to.

<a id="the-tool"></a><a id="adapting-it-to-your-project"></a><a id="adapted-templates"></a><a id="docsipqjson"></a><a id="troubleshooting"></a><a id="installing-and-updating"></a><a id="working-with-an-existing-set"></a><a id="at-a-glance-the-visuals-and-why-each-one-earns-its-place"></a><a id="milestones-where-the-work-stands"></a><a id="velocity-whether-the-work-is-moving"></a><a id="what-each-milestone-is-waiting-on"></a><a id="requirements-traced-through-the-set"></a><a id="screen-states-specified"></a><a id="checks-with-evidence-by-class-and-milestone"></a><a id="decision-records-by-status"></a><a id="delta-entries-opened-and-closed"></a><a id="questions-waiting-on-a-decision-by-age"></a><a id="document-sizes-against-the-budget"></a><a id="rules-every-block-keeps"></a>
## Where to look next

| For | See |
|---|---|
| Installing, starting, migrating, CI, updating, and removing | [SETUP.md](SETUP.md) |
| Every command, adapted templates, and `docs/ipq.json` | [SETUP.md: Reference](SETUP.md#reference) |
| What a finding means, and common problems | [SETUP.md: Fixing findings by hand](SETUP.md#fixing-findings-by-hand) |
| Every At a glance block, and why it earns its place | [VISUALS.md](VISUALS.md) |
| The rules your assistant follows | [skill/SKILL.md](skill/SKILL.md) |
| What changed in each version | [CHANGES.md](CHANGES.md) |
| Complete example sets | [`examples/jinkieslist/docs/`](examples/jinkieslist/docs/), and the smaller [`tests/fixtures/acme/docs/`](tests/fixtures/acme/docs/) |
| Problems and ideas | [github.com/baw-dev/ipq/issues](https://github.com/baw-dev/ipq/issues) |

## Questions

**Do I have to use all eight documents?** No. A missing document is a
warning, not an error. If a role doesn't apply to your product, say why in
`docs/README.md`.

**Does it send my documents anywhere?** No. The tool reads and writes files
under `docs/` and runs only the commands you list in `ipq.json`.

## Developing ipq

See [CONTRIBUTING.md](CONTRIBUTING.md). ipq is released under the
[MIT licence](LICENSE); to report a security problem, see
[SECURITY.md](SECURITY.md).

<details>
<summary>What does IPQ stand for?</summary>

Velma pushes up her glasses. "Jinkies! Depending on the system, it's an
Iteration, a Parameter, or a Quirk," she says. "But we'd better check the
technical documentation before Shaggy presses anything."

</details>
