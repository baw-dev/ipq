# Setting up ipq in your repository

**Answers:** how to install ipq, start a new document set, and bring an
existing one into line, with Claude Code or local ChatGPT, or by hand.
**Look elsewhere for:** what ipq is and why ([README](README.md)).

## Summary

There are three jobs, and you may need only one or two of them:

1. **Install** the skill, either for yourself or inside your repository so
   your whole team gets it.
2. **Start** a document set in a repository that has none.
3. **Migrate** a repository whose documents already exist.

Each job has two routes. **Ask your assistant:** paste the prompt and review what it
proposes. **By hand:** follow the numbered steps. Every step works without
an AI, using a terminal, a text editor, and `python3`.

## Contents

- [Before you start](#before-you-start)
- [1. Install](#1-install)
- [2. Start a new document set](#2-start-a-new-document-set)
- [3. Migrate an existing repository](#3-migrate-an-existing-repository)
- [4. Keep it conformant](#4-keep-it-conformant)
- [5. Update or remove ipq](#5-update-or-remove-ipq)
- [Reference](#reference)
- [Fixing findings by hand](#fixing-findings-by-hand)

## Before you start

You need:

- **Claude Code or ChatGPT's local desktop environment**, to use the skill.
  The Python tool also runs independently of either assistant.
- **Python 3.8 or later**, as `python3`. The tool uses only the standard
  library; there is nothing to `pip install`.
- **git**, to get ipq and review changes.
- **A POSIX shell** for `install.sh`. On Windows, use Git Bash or WSL, or
  use the [manual copy instructions](#manual-copy-windows).

The `chatgpt` target installs a local filesystem skill, also discoverable by
Codex. Local skill discovery is described in
[OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).
This guide covers local installation; ChatGPT workspace imports have a
separate lifecycle.

In the commands below, `IPQ` stands for the path to the tool. Choose one:

| Installation | Set in your terminal |
|---|---|
| Claude, project | `IPQ=.claude/skills/ipq/tools/ipq.py` |
| Claude, personal | `IPQ=~/.claude/skills/ipq/tools/ipq.py` |
| ChatGPT, project | `IPQ=.agents/skills/ipq/tools/ipq.py` |
| ChatGPT, personal | `IPQ=~/.agents/skills/ipq/tools/ipq.py` |

Run `python3 "$IPQ" check` from your project's root. `docs/` is the default
folder; name another one after the command, for example
`python3 "$IPQ" check handbook`.

## 1. Install

Both targets use the same skill, templates, and Python tools. Install into
your project for a version shared by teammates and CI, or personally for
use across projects.

### Get the source

Clone ipq once:

```bash
git clone https://github.com/baw-dev/ipq ~/src/ipq
```

Run the commands below from the project you want to use ipq in, rather
than from the ipq source checkout.

### Claude Code

Install into your project:

```bash
~/src/ipq/install.sh claude --project .
```

Or install personally:

```bash
~/src/ipq/install.sh claude
```

The destinations are `.claude/skills/ipq/` in the project and
`~/.claude/skills/ipq/` for a personal install. An omitted target defaults
to `claude`, preserving the existing `install.sh` and
`install.sh --project DIR` commands.

### ChatGPT locally

Install into your project:

```bash
~/src/ipq/install.sh chatgpt --project .
```

Or install personally:

```bash
~/src/ipq/install.sh chatgpt
```

The destinations are `.agents/skills/ipq/` in the project and
`~/.agents/skills/ipq/` for a personal install. These local skills are also
available to Codex. See [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills)
for local discovery and invocation. It does not upload a skill to a ChatGPT
workspace.

### Using both

Run both targets against the same project:

```bash
~/src/ipq/install.sh claude --project .
~/src/ipq/install.sh chatgpt --project .
```

Commit both installed folders. The copies have identical contents and use
the same `docs/` directory and `docs/ipq.json`. Choose either installed tool
for CI; running both copies of the checker is unnecessary. Update each
installation from the same source checkout to keep versions aligned.

### Ask your assistant

Open the destination project and ask, substituting `claude` or `chatgpt`:

> Clone https://github.com/baw-dev/ipq into a temporary folder and run its
> `install.sh <target> --project .` from this project's root. Show me what
> it added, then run the installed tool's `--version`.

For a personal install, omit `--project .`. For both platforms, ask it to
run each target.

### Verify the installation

The installer prints its target, destination, file checksums, and tool
command. Set `IPQ` using the table above, then run:

```bash
python3 "$IPQ" --version
```

For a project install, commit `.claude/skills/ipq/`, `.agents/skills/ipq/`,
or both, according to the targets you selected.

Start a new session in the project and ask the assistant to use ipq. In
ChatGPT, select the skill with `@`; in Codex, use `$ipq`. If it does not
appear, restart the app and confirm that the installed folder contains
`SKILL.md`, `templates/`, and `tools/`.

### Manual copy (Windows)

Copy the complete `skill` folder from the clone to the selected destination:

| Target | Project | Personal |
|---|---|---|
| Claude | `.claude\skills\ipq` | `%USERPROFILE%\.claude\skills\ipq` |
| ChatGPT | `.agents\skills\ipq` | `%USERPROFILE%\.agents\skills\ipq` |

Its contents must be `SKILL.md`, `templates\`, and `tools\`. Use `py -3`
wherever this guide says `python3`. In WSL, the shell's home and project
paths belong to WSL; use the environment where your assistant runs.

## 2. Start a new document set

For a repository with no `docs/` folder, or an empty one.

### Ask your assistant

> Use ipq to set up `docs/` for this project. It's called <name>. Here is what
> it is and who it's for: <two or three sentences>. Ask me for anything you
> can't infer from the code.

Your assistant creates the documents, drafts what it can from your
description and the code, writes `TBD` where only you can answer, and shows
you a plan before it edits.

### By hand

1. Create the documents:

   ```bash
   python3 "$IPQ" init --product "Your product"
   ```

   This writes nine files in `docs/`: `README.md` and the eight documents
   listed in the [README](README.md#what-it-keeps). It never overwrites a
   file that already exists. Each file holds its required sections, `TBD.`
   where content goes, and a short comment under each heading saying what
   belongs there.

2. Confirm the empty set passes:

   ```bash
   python3 "$IPQ" check
   ```

   The result should be `0 errors, 0 warnings`.

3. Write the Summaries first. Each document's Summary is 150 words or fewer
   in plain language. Start with `prd.md`: the problem, who has it, and what
   you'll build.

4. Add your first records. Copy the example inside the comment under a
   section, then change it. A requirement in `prd.md` looks like this:

   ```markdown
   <a id="r-core-01"></a>
   ### R-CORE-01 — People can record a tally

   - **Priority:** must
   - **Status:** accepted

   Acceptance criteria:

   1. A tap adds one to the count within 100 ms.
   ```

   The anchor goes on the line before the heading, and it is the ID in lower
   case. The fields come straight after the heading. Their allowed values
   are listed in the template's comments, and `check` names them if you
   choose one it doesn't allow.

5. Regenerate the generated sections, then check again:

   ```bash
   python3 "$IPQ" fix && python3 "$IPQ" check
   ```

   `fix` rewrites only Contents and At a glance. Each error names its file,
   line, and rule, and says what to change. See [Fixing findings by
   hand](#fixing-findings-by-hand).

6. Commit:

   ```bash
   git add docs && git commit -m "Start the ipq document set"
   ```

Optional: to record which version of ipq the set was checked with, create
`docs/ipq.json` containing `{"ipq": "1.0"}`.

## 3. Migrate an existing repository

For a repository whose planning documents already exist under any names.
Migration **moves content without rewriting what it means**. Do it in its own
branch, separate from any real change, so a reviewer can see that nothing's
meaning moved.

Expect many findings at first. That doesn't mean the content is wrong: most
findings are about structure, and they fall quickly.

### Ask your assistant

> Use ipq to migrate `docs/` in this repository. First save every anchor,
> map our existing files to ipq's roles, and show me the check tally and a
> migration plan. Ask me wherever our existing rules differ from ipq's, such
> as how we count sprints, or whether closed entries keep their full text.
> Don't change what any document means. Finish with `check --keep-anchors`.

Review the plan before approving it. The decisions only you can make are:
- which document owns what, when two overlap;
- whether finished work keeps its full text in an archive or is condensed;
- how your team counts time: weeks, sprints, or iterations;
- any section or field your project needs that the templates lack.

### By hand

1. **Branch.**

   ```bash
   git switch -c ipq-migration
   ```

2. **Save every anchor.** Code, tests, and other documents link to them, so
   none may disappear:

   ```bash
   python3 "$IPQ" anchors > .ipq-anchors.txt
   ```

   This lists anchors from every Markdown file under `docs/`, mapped or not.

3. **Map your files to roles.** Create `docs/ipq.json` for every document
   that already exists under another name:

   ```json
   {
     "ipq": "1.0",
     "files": {"prd": "requirements.md", "tdd": "architecture.md"}
   }
   ```

   The roles are `index` (the `README.md` in `docs/`), `prd`, `ux`, `tdd`,
   `roadmap`, `backlog`, `qa`, `runbook`, and `delta`. If one file mixes two
   roles, map it to the role that owns most of it; you will move the rest in
   step 7.

4. **Create what is missing.**

   ```bash
   python3 "$IPQ" init --product "Your product"
   ```

   Existing files are left alone. New files link to your filenames.

5. **Read the tally.**

   ```bash
   python3 "$IPQ" check
   ```

   The bottom lists how many findings each rule produced. Work from the
   biggest.

6. **Record where your rules win.** Before restructuring, decide where
   your project's existing conventions should stay, and record them. Don't
   fight them in prose.
   - **A section or field ipq lacks:** adapt the template with
     `python3 "$IPQ" template backlog`, then edit
     `docs/.ipq/templates/backlog.md`.
   - **How time is counted, and where finished work goes:** set `period`
     and `history` in `docs/ipq.json`. The
     [the Reference](#docsipqjson) lists every key.

7. **Restructure each document.** For each one, print its skeleton:

   ```bash
   python3 "$IPQ" skeleton prd --product "Your product" > prd-skeleton.md
   ```

   Then move the existing content into the skeleton's sections and replace
   the old file with it. Do not rewrite the content. Rules of thumb:
   - Anything with an ID or a status becomes a record: an anchor, a
     `### ID — title` heading, and `- **Field:** value` lines.
   - **Keep every old anchor.** Put it on the same line as the record's new
     one: `<a id="req-1"></a><a id="r-count-01"></a>`.
   - Put other headings under the section they serve, one level down.
   - Turn a status diary ("Sprint 3 closed…") into one dated line in
     History. The generated At a glance section replaces status prose.
   - Move a file that is not one of the eight roles, such as meeting notes,
     under its owner's folder, for example `docs/tdd/notes.md`. Give it a
     title, an `**Answers:**` line, a Summary, and a Contents section; the
     `supporting` skeleton has the shape.
   - Where you don't know something the template asks for, write `TBD`.
     Never guess.

   Delete the skeleton file once it's used.

8. **Regenerate, and prove nothing was lost:**

   ```bash
   python3 "$IPQ" fix && python3 "$IPQ" check --keep-anchors .ipq-anchors.txt
   ```

   Repeat steps 7 and 8 until no errors remain. An anchor error says which
   file the anchor moved to. Either leave it where the links point, or
   update every link to it.

   **Then review meaning, not just structure.** Moving a paragraph can change
   what it appears to govern, even when every word is the same:
   - Read each `context` warning. It names an anchor whose governing
     headings changed. Check that what it points to still reads with the
     same scope.
   - For the records most linked to, list their incoming links and read
     each one in its new context:

     ```bash
     python3 "$IPQ" links-to requirements.md#r-count-01
     ```

   - Ask three questions someone would really ask, such as "what does v2
     include?", of the old documents and the new, and compare the answers.

9. **Review and commit.** Read `git diff --stat` and check that it shows
   moves, not rewrites. Delete `.ipq-anchors.txt`, then commit and open a
   review:

   ```bash
   git add -A docs && git commit -m "Bring docs/ into line with ipq"
   ```

Warnings can wait: they point to gaps worth filling, not to broken
structure. Advice (`check --advice`) is about size and never blocks.

## 4. Keep it conformant

**Day to day.** After editing documents, run:

```bash
python3 "$IPQ" fix && python3 "$IPQ" check
```

Or ask your assistant to "use ipq to record this change". It edits the
document that owns the change, follows it downstream, and runs both commands.

**In CI.** `check` exits 1 on any error, so it can gate a pull request. With
ipq installed into the repository, a GitHub Actions workflow is enough.
This example uses the Claude path; for ChatGPT, replace `.claude` with
`.agents`:

```yaml
# .github/workflows/docs.yml
name: docs
on: [push, pull_request]
jobs:
  ipq:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 .claude/skills/ipq/tools/ipq.py check docs
```

A day passing never makes `check` fail. Each At a glance section is compared
against its own as-of date. Only a change to the records makes it stale.

**Freshness, on a schedule (optional).** `check` never fails because time
passed. To hear about stale status, overdue discrepancies, and old
evidence, run the freshness warnings nightly or before a release:

```bash
python3 "$IPQ" check docs --fresh
```

**Before each commit (optional).** Save this as `.git/hooks/pre-commit` and
make it executable. Use `.agents` in place of `.claude` for ChatGPT:

```bash
#!/bin/sh
python3 .claude/skills/ipq/tools/ipq.py check docs --errors-only
```

## 5. Update or remove ipq

**Update:** pull the source once, then reinstall the targets you use:

```bash
git -C ~/src/ipq pull
~/src/ipq/install.sh claude --project .
~/src/ipq/install.sh chatgpt --project .
python3 "$IPQ" check
```

Run either or both installer commands. Omit `--project .` for personal
installs. Each command updates only its selected copy. Other locations,
including older local installations, are not migrated automatically.

If you pinned a version in `docs/ipq.json`, `check` warns until you change
the pin. A new version may add rules; read its release notes and run `fix`.

**Compare without changing anything:** select each target you want to check:

```bash
~/src/ipq/install.sh claude --check --project .
~/src/ipq/install.sh chatgpt --check --project .
```

Omit `--project .` to compare a personal install. A missing, changed, or
extra installed file makes `--check` exit nonzero; it never repairs files.

**Remove:** delete only the installed folder for the target and scope:

| Target | Project | Personal |
|---|---|---|
| Claude | `.claude/skills/ipq/` | `~/.claude/skills/ipq/` |
| ChatGPT | `.agents/skills/ipq/` | `~/.agents/skills/ipq/` |

Removing one platform's copy leaves the other in place. Your documents
remain plain Markdown and need nothing from ipq to be read.

Account-managed skills, including a copy offered by the Claude desktop
app, are separate from these local installations. `install.sh` neither
updates nor checks those copies.

## Reference

### Commands

`skill/tools/ipq.py` does the mechanical work. It needs only Python 3.8 or
later, with no packages to install. Your assistant runs it for you, but you
can run it too. `DOCS` defaults to `./docs`. From your repository's root, with ipq
installed into the repository:

```bash
python3 .claude/skills/ipq/tools/ipq.py check   # Claude Code
python3 .agents/skills/ipq/tools/ipq.py check   # local ChatGPT/Codex
```

Choose the command for your installation. For a personal install, the paths
are `~/.claude/skills/ipq/tools/ipq.py` and `~/.agents/skills/ipq/tools/ipq.py`.

| Command | Does |
|---|---|
| `check [DOCS]` | Reports what departs from the templates, with a tally by rule. Exits 1 on any error, so it works in CI. |
| `check --advice` | Adds the size chart and one line of size advice per file. `--advice=all` lists each instance. |
| `check --keep-anchors FILE` | Fails if an anchor listed in FILE has gone, and says where it moved. Warns where an anchor's governing headings changed, so its scope can be reviewed. |
| `check --fresh [DATE]` | Adds warnings about age, judged at today or DATE: stale sections, overdue discrepancies, old evidence. Never an error. |
| `links-to FILE#ANCHOR` | Lists every link to an anchor, with its line |
| `check --errors-only` | Hides warnings |
| `fix [DOCS]` | Regenerates every Contents and At a glance. It changes nothing else. |
| `init [DOCS] --product NAME` | Creates missing documents from the templates. It never overwrites a file. |
| `roadmap [DOCS] [--html FILE]` | Prints the roadmap's At a glance, or writes the milestones as a web page |
| `anchors [DOCS]` | Lists every anchor as `file#anchor` |
| `template ROLE [DOCS]` | Copies a template into your project to adapt it |
| `skeleton ROLE [DOCS]` | Prints a role's empty document, with your filenames, to move existing content into |
| `--version` | Prints the version |

Each finding reads `path:line: level [rule] message`, so editors and CI can
link straight to it. There are three levels:

- **error:** the set does not conform. `check` exits 1.
- **warning:** something worth a look, such as an accepted requirement no
  check verifies. Exit status unaffected.
- **advice:** sizes against budgets, hidden unless you ask for them.

To run it in CI, add a step such as:

```
python3 path/to/ipq/skill/tools/ipq.py check docs
```

### Adapted templates

Your project may already have rules that differ from ipq's defaults. Record
them in two versioned places, never in ad hoc prose, so `check` enforces
your rules rather than fighting them.

```bash
python3 .claude/skills/ipq/tools/ipq.py template backlog
```

For local ChatGPT/Codex, use `.agents/skills/ipq/tools/ipq.py` instead.

This copies the template to `docs/.ipq/templates/backlog.md`. Edit the copy
to add sections, fields, record kinds, identifier forms, or allowed values.
`check` uses your copy, names it in its output, and holds it to a floor it
cannot drop: the title, the `Answers:` line, Summary, Contents, and At a
glance open the document, in that order, and every record keeps the upstream
template's required fields. A copy may make a required field optional; `check`
allows it and warns (`relaxed`) on every run, so the choice stays visible.

### `docs/ipq.json`

Every key is optional.

| Key | Sets | Example |
|---|---|---|
| `ipq` | The version this set was checked with; `check` warns on a mismatch | `"1.0"` |
| `files` | Other filenames for roles | `{"tdd": "architecture.md"}` |
| `budgets` | The Summary limit, and the advice thresholds | `{"summary_words": 200, "doc_lines": 2500}` |
| `history` | Where a finished record's full text goes: git (`condense`) or `docs/<role>/archive.md` (`archive`), for all documents or per document | `{"delta": "archive"}` |
| `evidence` | Folders of run records and other evidence, which are link-checked but not held to a template | `["qa/runs"]` |
| `period` | The unit for velocity and delta flow: `day`, `week` (the default), `month`, `quarter`, a fixed `sprint`, or `iteration` | `{"unit": "iteration", "name": "sprint"}` or `{"unit": "sprint", "start": "2026-07-06", "days": 14, "quiet": {"5": "documents-only"}}` |
| `period.from`, `period.match` | Under `iteration`: where the closing lines are (`roadmap` Iterations, or `backlog` Done), and a word that marks which lines close an iteration | `{"unit": "iteration", "from": "backlog", "match": "sprint"}` |
| `flow` | A separate period for delta flow, when delta entries aren't linked to iterations | `{"unit": "day"}` |
| `visuals` | Which blocks each document shows, in order | `{"roadmap": ["milestones", "velocity"]}` |
| `generated` | Your own command to draw a block; its output is used as-is | `{"roadmap.md#velocity": "python3 ../tools/velocity.py"}` |
| `checks` | Your own verification commands; their `path:line: level [rule] message` lines join the report | `["python3 ../tools/verify.py"]` |
| `ux_states` | The screen states every screen should consider | `["default", "empty", "loading", "error", "offline"]` |
| `glyphs` | Different marks, such as `▒` for done (Monaco draws it narrower) | `{"done": "▒"}` |
| `freshness` | Run the freshness warnings on every check, with these limits in days | `{"glance_days": 14, "delta_days": 30, "evidence_days": 90}` |

Evidence finds its period in this order: a link from an iteration's closing
line; a `- **Period:** 29` line in the run record; the date in the run
record's filename, such as `2026-09-24-pantry.md`; a date in the Evidence
cell.

## Fixing findings by hand

Each finding reads `path:line: level [rule] message`. The message says what
to change. This table says why the rule exists.

### Errors: `check` fails until they are fixed

| Rule | Means | Fix |
|---|---|---|
| `title` | The document doesn't open with exactly one H1 | Make the first line `# Product — Role` |
| `answers` | No `**Answers:**` line before the first section | Add one line naming the questions this document answers |
| `sections` | A section is missing, out of order, repeated, or not in the template | Use the skeleton's sections in its order. Put other headings under the section they serve, or adapt the template |
| `summary` | The Summary is over its word budget | Cut it to what a reader who stops there needs |
| `generated` | Contents or At a glance is out of date | Run `fix` |
| `visual` | An At a glance block can't be drawn from the records | The message names the record: add the missing date, `Waits on`, or link |
| `placement` | A record is in the wrong section | Move it. A finished item becomes a one-line entry under Done or Closed |
| `anchor` | A record lacks its anchor, or an anchor is defined twice | Add `<a id="lower-case-id"></a>` on the line before the heading |
| `fields` | A required field is missing or empty, or a value isn't allowed | Add the field, write `TBD` if unknown, or use a listed value |
| `dates` | A one-line entry lacks the date its template asks for | Add `done YYYY-MM-DD`, `found …`, or `closed …` as the message says |
| `trace` | A field must link into another document and doesn't | Link the requirement, design section, or milestone |
| `link` | A link points to a missing file or anchor | Correct the link, or restore the anchor |
| `duplicate` | One ID is defined twice | Keep one home. Link to it from the other place |
| `placeholder` | A template placeholder like `{{topic}}` remains | Replace it |
| `kept-anchor` | An anchor saved before the migration is gone | Restore it where links point, or update every link |
| `template` | An adapted template drops something every document keeps | Restore the title, `Answers:`, Summary, Contents, At a glance, or the required fields |
| `checks` | A project command in `ipq.json` failed | Run the command yourself and read its output |

### Warnings: worth a look, never blocking

| Rule | Means |
|---|---|
| `coverage` | An accepted requirement has no qa check yet |
| `states` | A screen lists a state its body never describes |
| `fields` | A record has a field its template doesn't declare |
| `archive` | Under the archive policy, a finished line and its full record don't pair up |
| `missing` | A role has no document. Create it, or say in `docs/README.md` why it doesn't apply |
| `unmapped` | A Markdown file in `docs/` isn't one of the roles. Map it, fold it in, or move it under its owner's folder |
| `adapted` | The set uses your copy of a template. This is informational |
| `relaxed` | Your adapted template keeps a field the upstream template requires but makes it optional. Allowed, and shown so the choice stays visible |
| `version` | `docs/ipq.json` pins a different version of ipq |
| `schema` | Your adapted template is based on an older template schema; see [CHANGES.md](CHANGES.md) |
| `evidence-scope` | A check's evidence is for a different revision than its milestone is judged at, so it isn't counted |
| `decider` | A delta entry blocks a milestone but names no one who `Decides` it |
| `context` | After a migration, an anchor sits under different headings; check its scope still reads right |
| `stale` | Only with `--fresh`: a section, discrepancy, or piece of evidence is older than its limit |

### Advice: shown only with `check --advice`

`paragraph`, `record-size`, `field-size`, `condensed`, and `doc-size`
compare sizes with the budgets in `docs/ipq.json`. They never fail a check.
Use them to decide where a supporting document would make an overview easier
to read.

### Common problems

**"At a glance is out of date" or "Contents is out of date".** A record
changed after the section was generated. Run `ipq.py fix` and commit the
result with the change.

**"At a glance cannot be drawn: …"** A block refused to guess. The message
names the record. The usual causes:

- a qa row has evidence but no date or dated run record;
- a delta entry has no `Found` date, or no `Waits on` while it blocks a
  milestone;
- a Closed line lacks `found YYYY-MM-DD · closed YYYY-MM-DD`;
- a date is later than the section's as-of date.

**"… is the close date of SPRINT-2, SPRINT-3; link the evidence …"** Two
iterations closed that day, so a date alone can't say which one the
evidence belongs to. Link the run from its iteration's closing line. For a
delta entry, link the iteration from its `Found` field, for example
`2026-09-24, in [sprint 3](roadmap.md#sprint-3)`. Or set `"flow": {"unit":
"day"}` to count delta flow by day.

**"its evidence is for 1.3.0; M1 is judged at revision 1.4.0".** The check
passed, but against a different build. Rerun it against the milestone's
revision, and cite the new run record, which names that revision on a
`- **Revision:**` line.

**"… blocks M2 but names no one who Decides it".** Add a `Decides` field
naming who can settle the entry, and a `Meanwhile` saying what may proceed
until they do.

**"anchor … was under X and is now under Y".** After a migration, an anchor
now sits under different headings. Read what it points to in its new place,
and check that its scope still reads the same.

**"'X' is not a roadmap section".** Each template allows a fixed set of
sections, in order. Make the material an H3 under the section it serves,
move it to a supporting document, or, if your project really needs the
section, add it to an adapted template.

**Hundreds of errors on an existing set.** See [3. Migrate an existing repository](#3-migrate-an-existing-repository), and the
rule tables above for what each rule means and how to fix it by hand. Start with `check --errors-only`. The
tally at the bottom shows which few rules account for most of it.

**Blocks look misaligned.** The font is drawing a glyph at the wrong width.
The default glyphs are measured to be safe in common monospace fonts. If
you changed `glyphs` in `ipq.json`, change it back. Monaco, for example,
draws `▒` narrower than one column.

**A day passed and nothing changed, but `fix` rewrote a section.** Only
blocks that depend on the date do this: days open, and the current period.
`check` never fails for this reason alone.

**The skill in the desktop app behaves like an older version.** The app can
offer the skill from your account, and that copy is separate from the one
`install.sh` manages. See [5. Update or remove ipq](#5-update-or-remove-ipq).
