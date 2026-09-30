---
name: ipq
description: >-
  Create, update, and reconcile repository planning documents so products are
  buildable, shippable, and operable, and later retrieval can locate sufficient,
  authoritative evidence. Enforces canonical ownership of product intent,
  experience and visual design, technical design, sequencing, work state,
  verification, operations, and reconciliation across the docs directory.
---

# IPQ

Use this skill when creating, updating, or reconciling product planning
documents under a repository's `docs/` directory.

Maintain one authoritative source for each kind of information. Make that
information easy for people and retrieval systems to locate, interpret, and
trace without introducing conflicting copies or expanding the requested scope.

## Priorities

Optimize in this order:

1. Factual correctness and canonical authority.
2. Complete scope, conditions, exceptions, and dependencies.
3. Discoverability for likely questions.
4. Clarity, concision, and maintainability.

Local self-containment is an authoring technique, not a guarantee that every
arbitrary fragment will retain its meaning. Optimize for realistic extraction
conditions when known; do not invent assumptions about the retrieval pipeline.

## Outcomes

- make intent, experience, design, sequencing, work state, verification, and
  operations easy to locate
- prevent contradictions through canonical ownership and precedence
- propagate changes only to affected documents and authoritative artifacts
- make requirements, screens, decisions, implementation, and verification
  traceable
- make completion include evidence and operability
- preserve an audit trail of product, experience, and technical decisions
- help later retrieval recover sufficient evidence with its qualifications
  and source context intact

## Canonical Document Set

Operate on documents under the repository's `docs/` directory. Prefer these
filenames. If the repository uses alternatives, map them once and keep that
mapping stable.

| Role | Preferred filename | Common aliases |
|---|---|---|
| `prd` | `docs/prd.md` | `product-requirements.md`, `requirements.md` |
| `ux` | `docs/ux.md` | `experience-design.md`, `ux-spec.md`, `ui-spec.md` |
| `tdd` | `docs/tdd.md` | `technical-design.md`, `design.md`, `architecture.md` |
| `roadmap` | `docs/roadmap.md` | `build-plan.md`, `plan.md` |
| `backlog` | `docs/backlog.md` | `execution-backlog.md`, `work-items.md` |
| `qa` | `docs/qa.md` | `test-plan.md`, `verification.md` |
| `runbook` | `docs/runbook.md` | `ops.md`, `operations.md` |
| `delta` | `docs/delta.md` | `reconciliation.md` |

Determine ownership from content and established repository conventions, not
filenames alone. Do not assign `design.md` to both `ux` and `tdd`.

If a needed canonical document is missing, propose creating it instead of
overloading another document. If a role does not apply to the product, record
that explicitly rather than inventing content.

If `docs/` does not exist, include the minimal appropriate canonical structure
in the change plan before editing.

## Canonical Boundaries

| Doc | Canonical truth for | Must contain | Must not contain | Primary owner |
|---|---|---|---|---|
| `prd` | Intent: what, why, scope, success | Problem or JTBD, target users, goals and metrics, scope and non-scope, requirements, user-facing acceptance criteria, constraints, risks | Detailed screen specifications, visual rules, architecture details, implementation details, task lists, sprint plans | Product |
| `ux` | Experience and visual design | Screen inventory, navigation, interaction flows, screen and component states, visual rules, responsive behavior, accessibility specifications, references to authoritative tokens and design assets | Product scope ownership, implementation architecture, duplicated token values, task tracking | Product Design |
| `tdd` | Technical design and decisions: how the system works and why | Architecture, responsibilities, data model, APIs and contracts, system workflows, NFRs, failure modes, rollout and rollback design, ADRs with dates, alternatives, consequences | Canonical interaction or visual specifications, roadmap dates, prioritization, task tracking, QA execution status | Engineering |
| `roadmap` | Sequencing and releases: what ships when | Milestones, releases, scope by milestone, dependencies, cut lines, rollout plan, entry and exit criteria, resourcing assumptions | Detailed experience or technical design, per-task tracking, status chatter | PM, Eng lead, TPM |
| `backlog` | Work state: what is next or in progress | Actionable items, definition of done, requirement and design links, estimate, owner, priority, milestone, dependencies | Canonical requirements, canonical experience or technical design, long narrative | Team |
| `qa` | Verification: how intent and specified behavior are proved | Test strategy, matrix mapped to acceptance criteria and applicable experience specifications, environments, automation plan, non-functional tests, release checklist, entry and exit criteria | Product or design decisions, backlog status, roadmap planning | QA, Engineering |
| `runbook` | Operations: how it is run and supported | SLOs or SLIs, dashboards, alerts, on-call ownership, incident playbooks, rollback procedures, data repair, flag operations, escalation | Product intent, design rationale, future planning | Engineering, Ops |
| `delta` | Reconciliation: implementation versus docs and artifacts | Deviations, evidence, reasons, impact, owners, follow-ups, reconciliation status | Net-new requirements, net-new design, roadmap ownership | Eng lead with PM and Product Design when relevant |

Keep unknown required information explicitly unresolved. Do not fabricate
owners, estimates, dates, acceptance criteria, design decisions, or operational
details to fill a document.

## Document Templates

IPQ 1.0. Every canonical document conforms to its template in `templates/`,
beside this file. Conformance is part of IPQ compliance, like canonical
ownership. The templates are the specification: `tools/ipq.py` reads its rules
from them. To change a rule for every project, change the template here; to
change it for one project, adapt it there (see Project templates and policy).

| Role | Template | Supporting documents |
|---|---|---|
| index | `templates/index.md`, as `docs/README.md` | none |
| each canonical role | `templates/<role>.md` | `templates/supporting.md`, as `docs/<role>/<topic>.md` |

### Progressive disclosure

Write each document so a reader can stop the moment they have their answer.
Abstraction falls as the reader moves down:

1. **Orientation.** The H1 title, then an `**Answers:**` line naming the
   questions this document answers and a `**Look elsewhere for:**` line
   pointing to the documents that answer the rest.
2. **Summary.** The whole document in 150 words or fewer, in plain language,
   for the reader who reads nothing else: the what and the why.
3. **Contents.** Generated from the headings. It lets an expert skip straight
   to the depth they need.
4. **At a glance.** Generated monospace blocks that measure the document's
   records: where work stands, whether it is moving, and what is missing.
5. **The how.** The role's body sections, in template order: structure, flows,
   interfaces, records.
6. **Detail and history.** Fine detail, finished work, and decision records
   come last, or live in supporting documents. They serve people changing
   the system, not people learning it.

### Structure rules

- Use the template's H2 sections, in the template's order, with the same
  names. Required sections are always present; write `TBD.` in one that has
  no content yet. Add an optional section only when it has content.
- Put any other heading at H3 or below, under the section it serves. A
  project that needs another H2 adapts its template; never add one ad hoc.
- Group material by what the reader is trying to do, not by feature or by
  when it was written.
- Hold each record (requirement, screen, component, decision, milestone,
  backlog item, check, playbook, disagreement) in the template's form: an
  `<a id>` anchor, a `### ID — title` heading, then `- **Field:** value`
  lines. The template declares each record's fields, the allowed values, and
  which fields must link to another role. Qa checks are table rows instead.
- A field holds a short value. Narrative goes in the record's body.
- Prefer a supporting document under `docs/<role>/` when a record, a
  paragraph, or a document grows hard to navigate. `check --advice` reports
  sizes against budgets (about 400 words a record, 120 a paragraph, 1,500
  lines a document) as guidance, not as rules. The Summary limit is the one
  size rule: a Summary over its budget is an error.
- Finished work leaves the working sections. A done backlog item or a closed
  delta entry becomes one dated line under Done or Closed: what happened,
  where the result lives, its requirement and milestone links, and the
  dates the template asks for. The full text follows the history policy.
- Record decisions as decision records in the document that owns them: ADRs
  in `tdd`; `DEC-` records in `prd`, `ux`, `roadmap`, or `qa` for rulings on
  scope, experience, sequencing, or evidence. Quote a ruling verbatim in its
  body.
- Never keep a diary above the records. Sprint results and dated status
  paragraphs are either measured in At a glance or recorded as one dated
  line in History.
- Never remove or rename an anchor. Moving content moves its anchor with it;
  condensing keeps it on the one-line entry. Code, tests, and run records
  link to anchors.
- Use plain words in the active voice. Define every term a new reader would
  not know in the glossary in `docs/README.md`, and use it exactly as
  defined there.

### Generated sections

Contents in every document, and At a glance in `prd`, `ux`, `tdd`, `roadmap`,
`qa`, and `delta`, are generated. Never edit them by hand; run
`tools/ipq.py fix`.

### At a glance

Each block is a monospace text block generated from records the documents
already hold.

| Document | Block | Built from |
|---|---|---|
| roadmap | Milestones: backlog items done and qa checks with evidence | milestones, backlog sections, qa rows, delta `Blocks` |
| roadmap | QA checks first evidenced, by period | the earliest date or run record in each qa row's Evidence |
| roadmap | Open delta entries blocking each milestone, by who has to act | delta `Blocks` and `Waits on` |
| prd | Accepted requirements traced through ux, tdd, backlog, qa, and evidence | links into each requirement; its `Trace` field names links it does not need |
| ux | Screen states specified | each screen's `States` field (`n/a` marks a state that cannot occur) |
| tdd, and any document with decision records | Decision records by status | decision records' `Status` |
| qa | QA checks with evidence, by class and milestone | the class in each check's ID, its Milestone, its Evidence |
| delta | Delta entries opened and closed, by period | `Found`, and the dates on each Closed line |
| delta | Delta entries waiting on a decision, by days open | open entries with `Waits on: decision` |

#### Periods

Velocity and delta flow count events per period. `docs/ipq.json` sets the
period; a week is the default.

| `period.unit` | Boundaries come from | Use when |
|---|---|---|
| `day`, `week`, `month`, `quarter` | The calendar, applied to each record's date | Most projects; nothing to declare |
| `sprint`, with `start` and `days` | A fixed cadence | Sprints of one fixed length |
| `iteration` | The closing line written when each iteration ends | Iterations of any length, several a day if need be |

Under `iteration`, nothing is declared before an iteration starts. When one
closes, write one dated line for it, linking the runs it produced:
in the roadmap's Iterations section (the default), or as the backlog's Done
line when every iteration is one backlog item (`"from": "backlog"`, with an
optional `"match"` word that picks out iteration lines). Iterations sort by
close date, then by the number in their identifier. An event belongs to an
iteration by link first: a run its closing line links, or a link to the
closing line. An unlinked event falls back to its date, and only when one
iteration fits it: a date on which several iterations closed needs a link.
An iteration that links no run is quiet (`·`); events after the last close
belong to the open iteration. `"flow"` sets a separate period for delta
flow when its entries are not linked to iterations.

A run record under `qa/runs/` may also name its period with a
`- **Period:**` line.

Every block keeps these rules, and the tool enforces them:

- The title names the measure.
- Exact counts are printed beside or under the marks. An observed zero is
  `0`; a quiet period (one declared quiet in `ipq.json`, or an iteration that
  linked no run) is `·`.
- A definition follows the title: what is counted, over what, and what is
  left out. A count is only as meaningful as its definition, and every
  block's counts are unweighted.
- Every block is generated, never typed. When some records are incomplete,
  for example undated, the block is drawn from the rest, marked `partial`,
  and the records left out are named. When records contradict each other,
  the block is not drawn: `check` reports why, and `fix` keeps the previous
  block.
- Measurements go in the block; status goes in the prose.
- No forecasts, trend lines, net-direction arrows, or completion dates. A
  past share is never computed against today's denominator.
- Lines fit in 78 columns. A block that would not fit scales, and its caption
  says `each ▓ ≈ N`.
- A plain-text fallback line follows each block, for screen readers and for
  renderers that mishandle block characters.
- Only glyphs measured to be one column wide in common monospace fonts are
  used. `▒` is excluded because Monaco draws it narrower; a project may still
  choose it in `ipq.json`.
- Each section carries its `as of` date. A block that depends on the date
  is redrawn when `fix` runs; `check` compares against the stamped date, so a
  passing day alone never makes a document fail. That is reproducibility,
  not freshness: see Freshness.

Know each block's limits and say them when reporting from it:

- **Coverage is not proof.** The trace block counts links. A linked
  requirement may still be wrong, and a check with evidence may test the
  wrong thing.
- **Counts are unweighted.** One end-to-end check and one unit check count
  the same. The qa class split shows kinds of evidence, not their strength.
- **Evidence counts only when its scope is known.** A milestone that names a
  `Revision` counts evidence only from run records naming that revision.
  Without one, any cited evidence counts.
- **Screen states are specified, not reviewed.** A state counts once it is
  listed and described.

#### Freshness

`check` is deterministic: the same records give the same result on any day.
Whether information is still current is a separate question, asked
explicitly with `check --fresh` (judged at today, or at a given date), or on
every check when `docs/ipq.json` sets `"freshness"`. Freshness findings are
warnings, never errors:

- an At a glance section drawn more than `glance_days` ago (default 14);
- an open delta entry past its `Escalate by` date, or open longer than
  `delta_days` (default 30);
- a check counted toward an active milestone whose newest evidence is older
  than `evidence_days` (default 90).

### Project templates and policy

A project adapts IPQ in two versioned places, never in ad hoc prose:

- **Templates.** `tools/ipq.py template ROLE` copies a template to
  `docs/.ipq/templates/ROLE.md`. Edit the copy to add sections, fields, record
  kinds, identifier forms, or allowed values. `check` uses the copy, names it
  in its output, and holds it to a floor: the title, the `Answers:` line,
  Summary, and Contents open the document, in that order; a kept At a
  glance stays generated; and every record kind of a required section keeps
  the upstream template's required fields. Keeping a required field but
  making it optional is allowed and warned about (`relaxed`) on every run;
  dropping it is an error. The floor is deliberately small,
  and IPQ's maintainers own it. A project's exception is an adapted template,
  which `check` names on every run.
- **Schema versions.** Every template states its schema version. When
  upstream moves ahead of an adapted copy, `check` warns; `CHANGES.md` in
  the ipq repository says what changed and how to update the copy.
- **`docs/ipq.json`.** Filenames, budgets, the history policy, evidence
  directories, the period, which blocks each document shows, project
  commands that generate a block (`"generated"`), project checks
  (`"checks"`, whose `path:line: level [rule] message` lines join the
  report), and the IPQ version the set was checked with.

The history policy decides where a finished record's full text goes:
`condense` (the default) leaves it to git; `archive` moves it to
`docs/<role>/archive.md` under the same anchor, beside its one-line entry.
Set it per document, for example `{"delta": "archive"}`. Under either policy
a record may carry dated correction notes in its body (`*Corrected
YYYY-MM-DD: …*`); follow the project's rule on visible corrections.

### Setting up a repository

`SETUP.md` in the ipq repository gives these steps for people working by
hand. Follow the same steps, so what you do and what they read agree.

**Installing into a repository.** Use the requested platform: `install.sh
claude --project <repository>` installs to `.claude/skills/ipq/`, and
`install.sh chatgpt --project <repository>` installs to `.agents/skills/ipq/`
for local ChatGPT/Codex. Run the installer from a clone of ipq, or copy this
skill's directory (the one holding this file) to the selected destination.
If the platform is unclear, ask which one; for both, install each target.
Both copies use the same project documents. Leave no `__pycache__` behind,
and tell the user to commit the installed folder or folders.

**Starting a new set.** Run `tools/ipq.py init --product NAME`. It creates
the nine documents and never overwrites a file. Draft the Summaries and the
first records from what the user said and from the code. Write `TBD` for
anything only the user can answer, then list those gaps. Run `fix`, then
`check`.

**Bringing an existing set into conformance.** Restructure in its own pass,
separate from substantive changes, so a reviewer can confirm that meaning
did not change.

1. Save the anchors: `tools/ipq.py anchors > .ipq-anchors.txt`. This lists
   every Markdown file under `docs/`, mapped or not.
2. Map existing files to roles in `docs/ipq.json` (`"files"`) before
   running `init`. Then `init` creates only the missing roles, and they link
   to the project's filenames.
3. Run `tools/ipq.py check` and read the tally by rule. Record each place
   the project's own rules differ from IPQ as a template adaptation or an
   `ipq.json` setting, and confirm those choices with the owner first.
4. Restructure each document into its skeleton (`tools/ipq.py skeleton
   ROLE`): sections, record form, anchors. Keep every old anchor, beside the
   record's new one on the same line. Move files that fill no role under
   their owner's folder as supporting documents. Then decide where detail
   belongs: supporting documents, the archive, or git.
5. Move content. Do not rewrite what it means. Delete only superseded
   running commentary whose substance already lives in its owning record,
   and only under the `condense` policy.
6. Run `tools/ipq.py fix`, then `check --keep-anchors .ipq-anchors.txt`,
   until no errors remain.
7. Review meaning, not only structure. `--keep-anchors` warns (`context`)
   wherever an anchor's governing headings changed; read each one and
   confirm its scope still reads the same. For the records most linked to,
   run `tools/ipq.py links-to FILE#ANCHOR` and read each incoming link in
   its new context. Ask the owner three representative questions of the old
   set and of the new, and compare the answers.

Propose the migration plan before editing a large set, as with any other
change.

## Tools

`tools/ipq.py` and `tools/ipq_visuals.py` are beside this file. They use only
the Python 3 standard library. `DOCS` defaults to `./docs`.

| Command | Does |
|---|---|
| `python3 tools/ipq.py check [DOCS]` | Reports every place the set departs from its templates: structure, record fields and values, anchors, links, identifiers defined twice, trace links to the wrong role, coverage gaps, blocks that cannot be drawn, stale generated sections, and project checks. Exits 1 on any error. |
| `check --advice` | Adds the document-size block and one line of size advice per file; `--advice=all` lists every instance. Advice never changes the exit status. |
| `check --keep-anchors FILE` | Errors on any anchor listed in FILE that no longer exists, and says where it moved; warns where an anchor's governing headings changed. |
| `check --fresh [DATE]` | Adds freshness warnings judged at today, or at DATE. |
| `python3 tools/ipq.py links-to FILE#ANCHOR [DOCS]` | Lists every link to an anchor, with its line, for reviewing it in context. |
| `python3 tools/ipq.py fix [DOCS]` | Regenerates every Contents and At a glance. It changes nothing else. |
| `python3 tools/ipq.py init [DOCS] --product NAME` | Creates each missing document from its template. It never overwrites a file. |
| `python3 tools/ipq.py roadmap [DOCS] [--html FILE]` | Prints the roadmap's At a glance, or writes the milestones as a standalone web page. |
| `python3 tools/ipq.py anchors [DOCS]` | Lists every explicit anchor as `file#anchor`. |
| `python3 tools/ipq.py template ROLE [DOCS]` | Copies a template into `docs/.ipq/templates/` to adapt it. |
| `python3 tools/ipq.py skeleton ROLE [DOCS]` | Prints a role's empty document, with the project's filenames, to move existing content into. |

Run `check` before planning changes to a set, and again after. Run `fix`
after any edit that adds or renames headings, or that changes records. Report
the final `check` result. Put a project's own verification in `"checks"`
rather than beside the tool, and do not script what `check` already covers.

## Experience, Screens, and Design Tokens

### Experience and visual design

Use `ux` to specify:

- navigation and user interaction flows
- screen structure, content hierarchy, and layout behavior
- typography, color usage, spacing, and other visual rules
- component appearance and interaction behavior
- responsive adaptations
- keyboard, focus, assistive-technology, and other accessibility behavior
- references to authoritative designs, assets, and tokens

Keep user-facing behavior in `ux` and technical mechanisms in `tdd`.

For example, `ux` specifies what a user sees and can do while a request is
pending; `tdd` specifies the request lifecycle, state management, and recovery
mechanisms that implement that behavior.

Product outcomes and acceptance criteria remain in `prd`.

### Screen inventory

Maintain the screen inventory in `ux`. Each applicable screen entry identifies:

- a stable screen ID and descriptive name
- purpose and linked `prd` requirements
- applicable user roles or access conditions
- route or entry point, where relevant
- navigation relationships and primary actions
- relevant states, such as loading, empty, partial, error, denied, and success
- links to detailed specifications or authoritative design assets

Include only states that apply. Do not invent behavior to complete a checklist.

Use stable screen and component anchors in backlog items and QA cases.

Start with one `ux` document. Split detailed screen specifications or a
design-system reference into supporting documents only when their size or
reuse warrants it. Keep `ux` as the index and preserve a single authoritative
location for each specification.

### Design-token authority

Keep token definitions and values in the repository's established authoritative
token source. This may include primitives, semantic tokens, themes, component
tokens, and aliases.

Use `ux` to explain token rationale, intended usage, and design constraints,
and to link to the authoritative definitions. Do not manually duplicate token
values in Markdown.

Identify which source is authoritative and which files or design artifacts are
generated or synchronized representations. Do not assume that both a design
tool and a code file can independently own the same token values.

If no token source exists, include the proposed source and ownership in the
change plan. Create or modify it only within the authorized scope.

Keep token build mechanics, transformations, framework bindings, and runtime
theme implementation in `tdd`.

Treat changes to authoritative token definitions or values as design changes
that require review of affected experience specifications, implementation,
verification, and work items.

## Precedence Rules

Resolve conflicting statements according to the kind of truth involved:

1. `prd` wins on what, why, scope, and product acceptance criteria.
2. `ux` wins on experience and visual-design decisions within `prd`
   requirements.
3. The designated token source wins on token definitions and values. `ux`
   governs their intended design usage.
4. `tdd` wins on technical implementation and architecture. It must identify
   constraints that require changes to `prd` or `ux` rather than silently
   redefining either.
5. `roadmap` wins on when and sequencing.
6. `qa` wins on how verification is performed, without redefining acceptance
   criteria or specified behavior.
7. `runbook` wins on how the system is operated.
8. `backlog` wins only on current work state.
9. `delta` records disagreement until the canonical document, artifact, or
   implementation is reconciled, then the entry is closed.

Update or remove conflicting statements in documents that do not own the
information. Do not retain contradictory statements as current guidance.

Document precedence does not erase observed implementation behavior. Record
implementation-versus-specification disagreements in `delta`, then determine
whether implementation should change or the canonical source is stale.

An owning document is the authority for what was intended and decided, not
for what the running product does. Keep the two apart: intent lives in the
owning record; observation lives in evidence (a run record, naming the
revision it ran against) and in `delta` when the two disagree. Never report
a requirement as met from its document alone. Cite in-scope evidence, or say
that none exists.

### Resolving a discrepancy

A `delta` entry is the start of a resolution, not the end of one:

- **Decision rights.** `Decides` names who may settle it, which may differ
  from the `Owner` who chases it. An entry that blocks a milestone needs one.
- **Resolution.** An entry closes only when the owning document changes, or
  the implementation changes with evidence to show it, and its one-line
  Closed entry says which.
- **Meanwhile.** `Meanwhile` says what affected work may proceed while the
  entry is open, or `nothing`. Without it, assume nothing that depends on
  the entry proceeds.
- **Escalation.** `Escalate by` is the date after which it goes to whoever
  the decider answers to. `check --fresh` reports entries past it.
- **Judgment, not regeneration.** `fix` never resolves a discrepancy. It only
  redraws generated sections.

Ask for a decision when the available evidence and authorization do not resolve
that choice.

## Required Cross-Linking

- Every `ux` screen specification links to applicable `prd` requirements.
  Shared component and visual rules have stable anchors referenced by the
  screens that use them.
- `ux` links to authoritative token definitions and design assets where relevant.
- Every `backlog` item links to a `prd` requirement and a `tdd` section, or
  explicitly states `no tdd needed` for the design link.
- Backlog items affecting experience or visual design also link to relevant
  `ux` screen, flow, component, or visual-rule anchors.
- Every `qa` test row links to a `prd` acceptance criterion. Experience,
  accessibility, and visual cases also link to the applicable `ux`
  specification and token source when relevant.
- Every `runbook` playbook links to the relevant `tdd` component and the related
  `roadmap` release when rollout matters.
- Every `roadmap` milestone lists included and excluded `prd` requirements and
  required `ux`, `tdd`, or ADR prerequisites.
- Whenever canonical sources disagree, identify the discrepancy immediately
  and open or update a `delta` entry within the authorized editing scope.
  If editing is not yet authorized, include it in the change plan.

Use stable identifiers and anchors. Preserve existing conventions. Include
needed new anchors in the change plan.

Links must identify their target and purpose. Prefer a requirement, screen,
component, decision, or procedure name over generic text such as “see above.”

## Discovery

Before planning changes:

1. Locate the repository root and inspect `docs/`. Run
   `tools/ipq.py check` to see where it departs from the templates.
2. Map existing files to the canonical document set.
3. Identify missing documents, aliases, identifiers, anchors, and cross-links.
4. Locate relevant screen inventories, design-system references, design assets,
   and token sources. Establish which are authoritative and which are derived.
5. Identify the trigger: a creation request, changed document or artifact,
   implementation change, or reconciliation request.
6. Read authoritative sources and affected canonical documents. Inspect
   implementation evidence when reconciliation requires it.
7. Identify the audience, document purpose, and likely questions the affected
   material should answer.
8. Inspect available retrieval constraints, such as chunk boundaries, overlap,
   metadata, and access to surrounding context.

Do not assume a repository layout beyond a repository-level `docs/` directory.
Do not require retrieval infrastructure or investigate unrelated systems merely
to improve document wording.

When retrieval behavior is unknown, use descriptive headings, coherent
passages, and explicit local context. Do not assume a heading or neighboring
paragraph will accompany an extracted passage.

## Editing Workflow

Apply this workflow to document creation, updates, and reconciliation:

1. Read the trigger material and affected authoritative sources.
2. Classify each proposed change by canonical ownership and precedence.
3. Identify contradictions, missing evidence, and downstream effects.
4. Present a concise document-change plan.
5. Proceed with changes already authorized by the user's request or prior
   approval. Do not request a second confirmation for the same authorized work.
6. Ask only about unresolved scope, substantive decisions, or actions outside
   existing authorization. Continue independent authorized work when possible.
7. Update the owning canonical source first, then propagate necessary changes
   according to the routing rules.
8. Run `tools/ipq.py fix`, then `tools/ipq.py check`, and resolve every
   error the change introduced.
9. Verify ownership, links, consistency, evidence completeness, and unresolved
   deltas.

Do not silently change product intent, experience, or technical design to make
sources agree. Distinguish editorial clarification from a substantive change
in requirements, behavior, design, or commitments.

### Planning Output

Before editing, identify:

- trigger document, artifact, or changed source
- change classification and canonical owner
- documents and artifacts to create, update, or leave untouched
- why each affected source changes
- precedence conflicts and unresolved decisions
- delta entries to open, update, or close
- retrieval-related structure or context changes when relevant

Keep the plan proportional to the work. Prefer a compact table or short list
grounded in canonical ownership.

## Change Routing

Apply these rules to new content as well as changed content. Inspect downstream
effects and edit only where the change requires it.

### If `prd` changes

1. Update `ux` if requirements affect screens, flows, interaction, visual
   constraints, or accessibility specifications.
2. Update `roadmap` for milestone or scope-sequencing effects.
3. Update `tdd` if design assumptions or ADRs change.
4. Update `qa` for acceptance-criteria coverage.
5. Update `backlog` for actionable work.
6. Update `runbook` only if operations or rollout expectations change.
7. Open or resolve `delta` entries for mismatches.

### If `ux` or authoritative design tokens change

1. Verify that the change still satisfies `prd`.
2. Update affected screen, flow, component, and visual specifications without
   duplicating authoritative token values.
3. Update `tdd` if implementation contracts, mechanisms, or technical
   constraints change.
4. Update `qa` for affected interaction, state, visual, responsive, and
   accessibility checks.
5. Update `backlog` for implementation and verification work.
6. Update `roadmap` if scope sequencing, design prerequisites, or release
   dependencies change.
7. Update `runbook` if support, operations, or rollout procedures change.
8. Update `prd` only if the design change reveals an intent, scope, or
   acceptance-criteria change.
9. Update `delta` for discrepancies among design sources, tokens, documents,
   and implementation.

### If `tdd` changes

1. Verify that the change still satisfies `prd` and applicable `ux`
   specifications.
2. Reconcile `ux` if technical constraints require an experience change.
   Do not treat the technical decision alone as approval to change the
   specified experience.
3. Update `roadmap` if sequencing or prerequisites change.
4. Update `qa` for verification impact.
5. Update `runbook` for operational impact.
6. Update `backlog` for execution impact.
7. Update `prd` only if the design change reveals an intent or scope change.
8. Update `delta` for divergence or reconciliation.

### If `roadmap` changes

1. Update affected `backlog` items.
2. Update `runbook` if rollout or release operations change.
3. Update `qa` if release gates change.
4. Update `prd` only if milestone changes reflect a real scope change.
5. Update `ux` or `tdd` only if sequencing changes the experience or technical
   design required for a release.
6. Update `delta` if implementation or canonical sources are out of sync.

### If `backlog` changes

1. Verify that it still matches `prd`, applicable `ux` specifications, `tdd`,
   and `roadmap`.
2. Update `roadmap` if work-state changes affect sequencing.
3. Update `qa` if definitions of done or verification steps change.
4. Update `runbook` if operational tasks are added or removed.
5. Update upstream sources only when the backlog exposes a real canonical
   change.
6. Update `delta` when the backlog reveals drift.

### If `qa` changes

1. Verify that every changed test maps to `prd` and applicable `ux`
   specifications.
2. Update `ux` only if test gaps reveal missing experience or visual-design
   decisions.
3. Update `tdd` only if test gaps reveal missing technical-design detail.
4. Update `runbook` if verification changes affect release or incident checks.
5. Update `backlog` for new work exposed by gaps.
6. Update `delta` for uncovered mismatches.

### If `runbook` changes

1. Verify that it matches current `tdd` and `roadmap`, and relevant `ux`
   behavior when procedures involve user-facing screens or flows.
2. Update `tdd` if the operational change reveals missing technical reality.
3. Update `ux` if operational evidence exposes an unresolved experience
   discrepancy.
4. Update `qa` if release or operational verification changes.
5. Update `backlog` for follow-up operational work.
6. Update `delta` for production-versus-specification drift.

### If `delta` changes or must be generated

1. Classify each divergence by canonical owner.
2. Determine whether implementation should change or a canonical source is
   stale.
3. Put lasting requirements and design decisions in their owning canonical
   sources, not in `delta`.
4. Keep each delta entry focused on the discrepancy, evidence, reason, impact,
   owner, follow-up, and reconciliation status.
5. Close the entry when the discrepancy is reconciled.

## Authoring and Editing Rules

### Preserve canonical authority

Update the smallest canonical surface that resolves the issue.

Keep each authoritative requirement, policy, experience specification, and
technical decision in its owning source. Never let `backlog` or `delta` become
substitute sources of product strategy, or let `qa` or `runbook` redefine
product scope or experience.

When material belongs elsewhere, move it to its canonical location and leave
a descriptive link or concise attributed summary where needed. A summary must
preserve relevant qualifications and must not introduce independent rules.

Repeat short identifying context when it helps interpretation. Avoid manually
duplicating changing requirements, token values, limits, exceptions, or
definitions across documents.

### Organize around likely questions

Give each passage a coherent purpose. Keep facts together when they jointly
answer a likely question, including necessary conditions and consequences.

Use broader passages when a question requires a complete procedure,
comparison, rationale, or synthesis. Do not force every sentence to stand
alone or every answer to fit in one passage.

Use descriptive headings and stable identifiers to support navigation and
precise retrieval. Essential meaning should not depend solely on a heading.

### Make important claims locally interpretable

Name the relevant entity, action, or relationship. Repeat identifying context
where detachment would otherwise create ambiguity.

Use pronouns when their referents remain clear within the passage. Avoid
unnecessary repetition and phrases such as “the above,” “the same value,” or
“this policy” when their meaning depends on distant context.

Write complete claims rather than fragments that require an earlier section
to supply their subject.

### Keep qualifications with claims

Place applicability, prerequisites, exceptions, units, effective dates,
versions, and mandatory-versus-optional status close to the statements they
qualify.

Avoid an unconditional-looking rule followed by a distant exception. State
the scope of quantities and limits precisely, including what is measured and
over what period when relevant.

For experience specifications, keep role, screen state, viewport, input method,
or theme qualifications with the behavior they affect.

Do not invent missing qualifications. Mark unresolved meaning explicitly and
route substantive decisions to the appropriate owner.

### Use precise, discoverable terminology

Preserve repository terminology, official names, screen and component IDs,
token names, identifiers, and error codes.

Define necessary abbreviations and include common aliases when they help
likely queries. Repeat a short expansion in another passage when its absence
would materially impair interpretation.

Avoid keyword stuffing, unnecessary synonym lists, and treating distinct
concepts as interchangeable.

### Preserve dependencies

For procedures and interaction flows, include the starting state,
prerequisites, ordered actions, decision conditions, and expected result.

When another passage is required, identify the dependency, explain its
relevance, and link to the precise source. Provide enough local context for a
reader to understand what must be consulted without copying the complete
upstream rule.

### Make structured and visual content interpretable

Give lists and tables explicit subjects, field labels, units, and scope.
Ensure values remain associated with the entities and conditions they describe.

Where expected extraction separates rows from headers, use labeled records,
carry essential labels into rows, or use an existing retrieval representation
that preserves the missing context.

Accompany important diagrams, mockups, and screenshots with concise text
identifying the screen or component, relevant state, and decisions they
illustrate. Essential behavior must not be specified only through an image.

Distinguish illustrative visuals from authoritative specifications. Do not
infer exact measurements, token values, or hidden behavior from a mockup
without supporting evidence.

Choose structure for the information and likely questions. Do not convert
every passage into repetitive fields solely for hypothetical chunking.

### Preserve provenance and uncertainty

Distinguish current requirements, observed implementation behavior, proposals,
estimates, examples, and unresolved questions. Mark status where a reader
could act on it: records and consequential claims, not every sentence.

Include source references, decision dates, versions, and applicability when
available and relevant. Clearly distinguish superseded decisions from current
guidance while preserving the decision history.

Never present inferred or generated context as an independently verified fact.

## Derived Retrieval Representations

Create contextualized chunks, records, or other retrieval representations only
when the task includes them or an existing pipeline supports them within scope.

- Derive them from canonical sources.
- Retain source references and available version context.
- Distinguish generated explanatory context from source statements.
- Regenerate affected representations when their sources change.
- Do not hand-maintain them as independent sources of requirements or design.
- Do not add retrieval infrastructure solely to complete a document-writing
  task.

## Verification

After changes, perform checks proportionate to the affected material.

### Governance and consistency

Verify that:

- `tools/ipq.py check` reports no errors, or each remaining error is
  pre-existing and named in the completion summary
- each information type has one canonical owner
- requirements and design remain within authorized intent and scope
- conflicts are resolved according to ownership and precedence
- required links and anchors resolve
- screens and relevant work items are traceable to requirements and design
- token authority is explicit and values are not independently maintained
  in multiple sources
- downstream documents reflect relevant canonical changes
- active delta entries describe unresolved discrepancies and follow-ups
- reconciled delta entries are closed
- the document set provides the information needed to build, ship, verify,
  and operate the product

### Experience coverage

For affected experience specifications, verify that:

- the screen inventory identifies relevant screens, roles, and entry points
- navigation and interaction flows have identifiable outcomes
- applicable screen and component states are specified
- responsive and accessibility behavior is explicit where it affects use
- visual rules reference authoritative tokens and assets
- QA coverage links to the relevant requirements and experience specifications

These are specification checks. Claim implementation conformity only when the
implementation has actually been inspected or tested.

### Evidence and interpretation

Check representative questions against the affected documents.

Verify that:

- the evidence supports the answer, including necessary exceptions and scope
- dependencies are identifiable when an answer spans passages or documents
- plausible extracted passages retain their subject and essential context
- tables retain meaningful associations among labels, values, and units
- procedures and flows preserve prerequisites and sequence
- quantities, terminology, and references are unambiguous
- summaries do not contradict or silently redefine their canonical sources
- questions unsupported by the sources remain unresolved

Inspect plausible extraction boundaries for separated subjects, exceptions,
headers, and procedural dependencies. Treat this as a diagnostic; do not claim
that every arbitrary cut preserves meaning.

### Retrieval evaluation

When an evaluation setup is available and its use is within scope, compare
complete-evidence retrieval and answer accuracy under comparable queries,
retrieval settings, and context budgets.

Include questions about qualifications, questions requiring multiple passages,
and questions the sources cannot answer. Test realistic boundary variations
when assessing extraction resilience.

Without retrieval evaluation, report only the document checks actually
performed. Do not claim measured retrieval improvements.

## Completion Output

Summarize:

- what changed and why
- which canonical documents and artifacts were affected
- verification performed and its practical limits, including the final
  `tools/ipq.py check` result
- unresolved decisions, missing evidence, and active deltas

When naming document roles, use:

- `prd`: intent
- `ux`: experience and visual design
- `tdd`: technical design and decisions
- `roadmap`: sequencing and releases
- `backlog`: work state
- `qa`: verification
- `runbook`: operations
- `delta`: reconciliation
