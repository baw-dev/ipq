# Changes

**Answers:** what changed in each version of ipq, and how to update a
project that adapted a template.

## How versions work

ipq has one version, `__version__` in `skill/tools/ipq.py`, printed by
`ipq.py --version`. Everything else quotes it, and a test fails if the
first entry below, its anchor, `__version__`, and SKILL.md disagree.

| Part | Changes when | What a pinned set sees |
|---|---|---|
| **Major** (2.0.0) | Documents must be migrated to keep passing | A `version` warning, and errors until migrated |
| **Minor** (1.1.0) | A new rule or finding, command, install target, or change to generated output | A `version` warning until the pin in `docs/ipq.json` is updated, since pins compare major and minor |
| **Patch** (1.0.1) | A fix that changes no rule and no generated output | Nothing |

The **template schema version** is a separate whole number in each template
(`<!-- ipq:schema version="2" -->`). It changes only when a template's
structure changes, and each entry below names the schema it ships. A template
with no schema line is read as version 1, the format used before the first
release.

Each entry has a permanent anchor, `#vMAJOR.MINOR.PATCH`, and a matching git
tag, so a project can link to the exact release it was checked with. Headings
may be reworded; anchors never change.

<a id="v1.0.1"></a>
## 1.0.1: an archive checks a record against its section's spec (template schema 2)

**For every project:**
- **Closed entries can be archived in full.** Inside a role's `archive.md`,
  a record is now checked against the spec whose `in` names the section it
  sits under, when a template declares one; otherwise against the first
  matching spec, as before. So a project can add, to an adapted delta
  template, a second `D-` record spec with `in="Closed"`, and archive closed
  entries with the fields a closed entry has. Before, every archived `D-`
  record was checked against the Open spec and needed `Waits on`. Outside an
  archive nothing changes, so a full record cannot sit under Closed in
  `delta.md` and be counted as open.

**Updating documents:** nothing to do. A pin of `"1.0"` stays valid.

<a id="v1.0.0"></a>
## 1.0.0: first public release (template schema 2)

ipq keeps a repository's planning documents honest and easy to read, for
people and for models. This first release includes:

- **Templates for eight documents and an index,** each opening with the
  questions it answers, a Summary, generated Contents, and At a glance.
- **`ipq.py`,** a standard-library Python tool: `check` for structure,
  links, traces, anchors, and freshness; `fix` to regenerate Contents and
  At a glance; `init`, `skeleton`, `template`, `anchors`, `links-to`, and
  `roadmap`.
- **At a glance blocks** that are generated from records, print exact
  counts, define what they count, and refuse to guess. See
  [VISUALS.md](VISUALS.md).
- **Periods** by day, week, month, quarter, fixed sprint, or iteration of
  any length, closed by a dated line.
- **Project adaptation** through adapted templates and `docs/ipq.json`,
  held to a small floor. A template that makes a required field optional
  is allowed, with a `relaxed` warning.
- **Migration support:** `anchors` and `check --keep-anchors` prove that no
  link target was lost.
- **Installation** for Claude Code or local ChatGPT/Codex, personally or
  inside a project, with `install.sh --check` to compare without copying.
- **Two example sets:** `tests/fixtures/acme/docs` and the fuller
  `examples/jinkieslist/docs`.

**Starting out:** see [SETUP.md](SETUP.md). To record the version a set was
checked with, put `{"ipq": "1.0"}` in `docs/ipq.json`.
