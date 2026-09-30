# ipq — At a glance visuals

**Answers:** what each generated block shows, why it earns its place, and the rules every block keeps.
**Part of:** the [README](README.md), which introduces ipq.

## Summary

Six documents open with an **At a glance** section of plain-text blocks, generated from the
records they already hold. Each block answers one question a reader brings to that document:
where the milestones stand, whether evidence is arriving, who has to act on each blocker, which
requirements are traced to proof, which screen states are designed, which kinds of proof are
missing, how settled the design is, and whether known problems are growing or shrinking. Nobody
types the numbers, so they cannot drift from the records. Every block prints exact counts,
defines what it counts, refuses to guess, and makes no forecast. Read them as a map of where to
look, not as a verdict.

## Contents

- [The blocks](#the-blocks)
  - [Milestones: where the work stands](#milestones-where-the-work-stands)
  - [Velocity: whether the work is moving](#velocity-whether-the-work-is-moving)
  - [What each milestone is waiting on](#what-each-milestone-is-waiting-on)
  - [Requirements traced through the set](#requirements-traced-through-the-set)
  - [Screen states specified](#screen-states-specified)
  - [Checks with evidence, by class and milestone](#checks-with-evidence-by-class-and-milestone)
  - [Decision records by status](#decision-records-by-status)
  - [Delta entries opened and closed](#delta-entries-opened-and-closed)
  - [Questions waiting on a decision, by age](#questions-waiting-on-a-decision-by-age)
  - [Document sizes against the budget](#document-sizes-against-the-budget)
- [Rules every block keeps](#rules-every-block-keeps)
- [Why plain text](#why-plain-text)

## The blocks

Six documents open with a generated **At a glance** section. Each block is
plain text in a code fence, so it renders the same on GitHub, in an editor,
in a terminal, and in a model's context. Each is built only from records the
documents already hold. Nobody types these numbers, so nobody has to keep
them current.

The examples below, all but the illustrative size block, are real output
from [JinkiesList](examples/jinkieslist/docs/), a demo set for a shared
grocery list and pantry app. Run `ipq.py roadmap examples/jinkieslist/docs`
to see the full blocks.

### Milestones: where the work stands

**In** `roadmap.md`. **Answers:** what is done, what is next, and what is in
the way?

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

**Why it earns its place.** It sets side by side two measures that usually
live in different tools: work finished (the backlog) and requirements proved
(qa). A milestone with its work done and half its checks unproved isn't
finished, and this block makes that impossible to miss.

### Velocity: whether the work is moving

**In** `roadmap.md`. **Answers:** are we gaining evidence, period by period?

```text
QA checks first evidenced, by sprint · as of 2026-09-29

                     ▓
                     ▓
                  ▓  ▓     ▓
  sprint    1  2  3  4  5  6
  checks    ·  ·  1  3  ·  1

each ▓ is one check first evidenced in that sprint
· a sprint that linked no run
```

**Why it earns its place.** Only velocity shows whether the work is moving.
It counts checks that gained their *first* evidence, so re-running an
old test never looks like progress. A sprint that linked no run (say, one
spent on documents) shows `·` rather than a misleading `0`.

**Periods that fit how your team works.** The period can be a calendar day,
week, month, or quarter, with nothing to declare; a sprint of fixed length;
or an *iteration* of any length. An iteration is declared only when it
ends, in one line that links the runs it produced:

```markdown
- <a id="sprint-4"></a>**SPRINT-4** Invitations and conflicts — [B-008](backlog.md#b-008) · closed 2026-08-31
- <a id="sprint-3"></a>**SPRINT-3** Offline sync — [run](qa/runs/2026-08-14-sync.md) · closed 2026-08-14
```

The chart above is drawn from lines like these. Links decide where evidence
belongs, so several iterations can close on one day. Unlinked evidence falls
back to its date, and a date two iterations share makes `check` ask for a
link rather than guess. When every iteration is one backlog item, the
backlog's Done lines are the closing lines, with nothing extra to write.

### What each milestone is waiting on

**In** `roadmap.md`. **Answers:** blocked by what, and who has to act?

```text
Open delta entries blocking each milestone, by who has to act

  M2   ▓○  1 work · 1 external
  M3   ▲   1 decision

▲ a decision · ▓ work · ○ someone outside the team
```

**Why it earns its place.** "Blocked" is a status; this is a to-do list. It
groups every open disagreement by who must move next, so an owner can see at
once which blocks are theirs to lift.

### Requirements traced through the set

**In** `prd.md`. **Answers:** is each requirement carried all the way from
intent to proof?

```text
Accepted requirements traced through ux, tdd, backlog, qa, and evidence

4 of 6 accepted requirements fully traced

               ux       tdd      backlog  qa       evidence
  R-PANTRY-01  ▓        ▓        ▓        ▓        ░
  R-PANTRY-03  ▓        ▓        ▓        ▓        ░

▓ linked · ░ missing · − not required (the requirement's Trace field)
```

**Why it earns its place.** It's the densest check of the whole set on one
screen, and it lists only the requirements with gaps, so it stays short as
the set grows. A requirement that needs no screen says so in its `Trace`
field and shows `−`, not a false gap.

### Screen states specified

**In** `ux.md`. **Answers:** which screen states has nobody designed yet?

```text
Screen states specified

                         default empty   loading error   offline
  SCR-01 List            ▓       ▓       −       −       ▓
  SCR-02 Pantry          ▓       ▓       −       −       ▓
  SCR-03 Join household  ▓       ░       ▓       ▓       ▓
  SCR-04 Staples         ▓       ▓       ░       ░       ░
```

**Why it earns its place.** Empty, loading, error, and offline states are
the ones engineers end up inventing in code. This grid shows them missing
while they are still cheap to design. `−` records a deliberate "this state
can't happen", which is a design decision in its own right.

### Checks with evidence, by class and milestone

**In** `qa.md`. **Answers:** which *kind* of proof is missing?

```text
QA checks with evidence, by class and milestone

          M1    M2    total
  LIST    ▓▓▓▓        4/4
  PANTRY        ▓░░░  1/4
  total   4/4   1/4   5/8
```

**Why it earns its place.** "Five of eight checks have evidence" hides where
the missing three are. Split by class, a gap in, say, privacy or
accessibility testing stands out from a gap in routine checks.

### Decision records by status

**In** `tdd.md`, and in any document with decision records. **Answers:** how
much of the design is still open?

```text
Decision records by status

  ▓▓×

  ▓ accepted 2 · × superseded 1
```

**Why it earns its place.** One line shows how much of the design is
settled, how much is still proposed, and how much has been replaced. A long
run of `░` (proposed) warns that the design is less decided than its prose
suggests.

### Delta entries opened and closed

**In** `delta.md`. **Answers:** are we finding problems faster than we fix
them?

```text
Delta entries opened and closed, by sprint · as of 2026-09-30
Entries by the sprint of their Found date and of their close; open at end is
the running difference. Counts entries, not their size or severity.

  sprint         1   2   3   4   5   6
  opened         0   1   1   1   1   2
  closed         0   0   1   2   0   0
  open at end    0   1   1   0   1   3
```

**Why it earns its place.** It's velocity's counterpart. Velocity shows
evidence being gained; this shows the list of known problems growing or
shrinking. It prints the counts and no trend arrow, because an arrow would
read as a forecast.

### Questions waiting on a decision, by age

**In** `delta.md`. **Answers:** what is waiting on someone to decide, and
for how long?

```text
Delta entries waiting on a decision, by days open · as of 2026-09-30
Open delta entries whose Waits on is decision, by whole days since their Found
date.

  0-2    ·  0
  3-7    ·  0
  8-14   ·  0
  15+    ▲  1

▲ one open entry that waits on a decision
days counted from each entry's Found date
```

**Why it earns its place.** An unanswered question costs nothing visible
until it stalls a release. This makes the wait visible while there is still
time to answer.

### Document sizes against the budget

**In** the output of `check --advice`. It isn't embedded, because it would
change with almost every edit. **Answers:** which documents have outgrown an
overview? These numbers are illustrative:

```text
Lines per document against the budget of 1,500

  tdd.md       ▓▓▓▓▓▓▓▓▓▓┆▓▓▓▓▓▓▓▓▓           2,840
  delta.md     ▓▓▓▓▓▓▓▓▓▓┆▓▓                  1,720
  roadmap.md   ▓▓▓▓▓▓▓▓  ┆                    1,180

each ▓ ≈ 150 lines · ┆ the budget
```

**Why it earns its place.** It helps while you split an overgrown set into
supporting documents, and afterwards it keeps watch. It's advice, never an
error.

## Rules every block keeps

These rules keep the numbers trustworthy:

- **The title names the measure.** "Delta entries opened and closed, by
  sprint", not "Delta".
- **Exact counts sit beside the marks.** An observed zero is `0`; a quiet
  period is `·`.
- **Each block defines its measure.** A line under the title says what is
  counted, over what, and what is left out.
- **Nothing is typed by hand, and nothing is guessed.** When some records
  are incomplete, the block is drawn from the rest, marked `partial`, and
  the records left out are named. When records contradict each other, the
  block is not drawn: `check` says which record, and `fix` keeps the
  previous block.
- **No forecasts.** No trend lines, completion dates, or net-direction
  arrows, and no past percentage worked out against today's total.
- **Everything fits in 78 columns.** A block that would not fit scales, and
  says `each ▓ ≈ N`.
- **Screen readers are covered.** A plain-text sentence follows every block,
  such as "R-PANTRY-01 lacks evidence."
- **Only safe glyphs are used.** Each was measured to be one column wide in
  Menlo, SF Mono, Courier New, Andale Mono, and PT Mono, so columns line up.
- **Each section carries its as-of date.** A day passing never makes a
  document fail `check`. Whether it is still current is a separate,
  explicit question: `check --fresh`.

These charts have limits, and anyone reading them should know them:
- **Counts are unweighted.** A unit check and an end-to-end check each count
  one.
- **Tracing counts links, not correctness.**
- **Screen states count as specified once written down, not once
  reviewed.**
- **Evidence counts toward a milestone only for its stated revision,** when
  it states one.

Treat the charts as a map of where to look, not as a verdict.

## Why plain text

**Why plain-text charts instead of images or Mermaid?** They render the same
everywhere, diff cleanly in review, and a model can read them as easily as a
person can.
