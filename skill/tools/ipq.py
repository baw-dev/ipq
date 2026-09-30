#!/usr/bin/env python3
"""ipq: keep a docs/ directory conformant to the IPQ templates.

Usage:
    ipq.py check    [DOCS] [--advice[=all]] [--keep-anchors FILE] [--errors-only]
    ipq.py fix      [DOCS]                 regenerate Contents and At a glance sections
    ipq.py init     [DOCS] --product NAME  create missing documents from the templates
    ipq.py roadmap  [DOCS] [--html FILE]   print the roadmap's blocks, or write a web page
    ipq.py anchors  [DOCS]                 list every explicit anchor as file#anchor, with its heading path
    ipq.py links-to TARGET [DOCS]          list every link to file#anchor, with its line
    ipq.py template ROLE [DOCS]            copy a template into docs/.ipq/templates to adapt it
    ipq.py skeleton ROLE [DOCS] [--product NAME]
                                           print a role's empty document, to move existing content into
    ipq.py --version

DOCS defaults to ./docs. Standard library only; Python 3.8 or later.

The templates in ../templates are the specification. Each template's H2 headings
are its sections, in order; `<!-- ipq:optional -->` under a heading makes it
optional and `<!-- ipq:generated -->` makes its body generated. The
`<!-- ipq:record|condensed|table ... -->` directives declare the records a
document holds. A project adapts a template by copying it to
docs/.ipq/templates/<role>.md; check holds any copy to a floor it cannot drop.

docs/ipq.json, all keys optional:
    {"ipq": "1.0",                                  the version this set was checked with
     "files": {"tdd": "architecture.md"},           other filenames for roles
     "budgets": {"summary_words": 150, ...},        advice thresholds, and the Summary limit
     "history": "condense" | "archive" | {"delta": "archive"},  where finished records' full text goes
     "evidence": ["qa/runs"],                       directories of evidence, not documents
     "period": {"unit": "week"} or {"unit": "sprint", "start": "2026-01-05", "days": 14,
                "quiet": {"13": "documents-only"}},
     "visuals": {"roadmap": ["milestones", "velocity"]},
     "generated": {"roadmap.md#velocity": "python3 ../tools/velocity.py"},
     "checks": ["python3 ../tools/verify.py"],
     "ux_states": ["default", "empty", "loading", "error", "offline"],
     "glyphs": {"done": "▒"}}
"""
import argparse
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in the skill, which projects commit
sys.modules.setdefault("ipq", sys.modules[__name__])  # so ipq_visuals shares this module when run as a script
import ipq_visuals as visuals  # noqa: E402

__version__ = "1.0.0"

SKILL = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL / "templates"
OVERRIDES = Path(".ipq") / "templates"

ROLES = ["index", "prd", "ux", "tdd", "roadmap", "backlog", "qa", "runbook", "delta"]
DEFAULT_FILES = dict({r: f"{r}.md" for r in ROLES}, index="README.md")
BUDGETS = {
    "summary_words": 150,    # a Summary longer than this is an error: it is the place a reader may stop
    "paragraph_words": 120,  # advice from here down: a longer paragraph or list item reads as a wall
    "field_words": 30,       # a field holds a value, not narrative
    "record_words": 400,     # a longer record may read better as a supporting document
    "condensed_words": 60,   # a Done or Closed line
    "doc_lines": 1500,       # a longer document may read better split into supporting documents
}
ADVICE_RULES = {"paragraph", "record-size", "field-size", "condensed", "doc-size"}
EMPTY = {"", "tbd", "none", "n/a", "-", "—"}  # no evidence, no milestone
BLANK = {"", "-", "—"}                          # a required field with nothing in it
FLOOR = ["Summary", "Contents"]                 # every document opens with these, in this order

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
RECORD_HEADING = re.compile(r"^([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)\s+[—–-]\s+(.+)$")
ANCHOR = re.compile(r"""<a\s+(?:id|name)=["']([^"']+)["']""")
ANCHOR_LINE = re.compile(r"""^\s*(?:<a\s+(?:id|name)=["'][^"']+["']\s*>\s*</a>\s*)+$""")  # a line of anchors and nothing else
LINK = re.compile(r"!?\[([^\]]*)\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
FIELD = re.compile(r"^\s*[-*]\s+\*\*([^*]+?)(?::\*\*|\*\*:)\s*(.*)$")
CONDENSED = re.compile(r"""^\s*[-*]\s+<a\s+id=["']([^"']+)["']\s*>\s*</a>\s*\*\*([^*]+)\*\*""")
DIRECTIVE = re.compile(r"<!--\s*ipq:(record|condensed|table)\s+(.*?)-->", re.S)
SCHEMA = re.compile(r"<!--\s*ipq:schema\s+version=\"(\d+)\"\s*-->")
ATTR = re.compile(r'(\w+)="([^"]*)"')
MILESTONE = re.compile(r"\bM\d+\b")
WORD = re.compile(r"\S+")
FINDING = re.compile(r"^(.+?):(\d+): (error|warning|advice) \[([\w-]+)\] (.*)$")


# ---------------------------------------------------------------- markdown

def clean_lines(raw):
    """Blank out HTML comments and fenced code, keeping line numbers."""
    out, code, in_fence, in_comment = [], [], None, False
    for line in raw:
        if in_fence:
            out.append(""); code.append(True)
            if line.strip().startswith(in_fence):
                in_fence = None
            continue
        s = line
        if not in_comment:
            m = re.match(r"^\s*(```+|~~~+)", s)
            if m:
                in_fence = m.group(1)[:3]
                out.append(""); code.append(True)
                continue
        text = ""
        while s:
            if in_comment:
                end = s.find("-->")
                if end < 0:
                    s = ""
                else:
                    s, in_comment = s[end + 3:], False
            else:
                start = s.find("<!--")
                if start < 0:
                    text, s = text + s, ""
                else:
                    text, s, in_comment = text + s[:start], s[start + 4:], True
        out.append(text); code.append(False)
    return out, code


def without_code_spans(line):
    """The line with inline code spans removed: runs of backticks and what they enclose, so a
    literal such as `[]Boundary{{…}}` or ``a`b`` is never read as a link or a placeholder."""
    return re.sub(r"(`+).+?\1", "", line)


def plain(text):
    """Rendered-ish text: links to their text, tags and emphasis removed."""
    text = LINK.sub(lambda m: m.group(1), text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"[`*_]", "", text)


def words(text):
    return len(WORD.findall(plain(text)))


def slugify(text):
    s = plain(text).strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


class Heading:
    def __init__(self, level, text, line):
        self.level, self.text, self.line = level, text, line
        self.end = None  # index of the first line after this heading's scope
        self.slug = ""


class Record:
    def __init__(self, id, form, spec, section, line, title=""):
        self.id, self.form, self.spec, self.section = id, form, spec, section
        self.line, self.title = line, title
        self.fields = {}      # name -> (value, line)
        self.body_words = 0
        self.text = ""        # the whole condensed line or table row
        self.anchor = ""      # the anchor a condensed or table record carries
        self.body_start = line + 1  # a heading record's first line after its fields


class Doc:
    def __init__(self, path, role, supporting=False, evidence=False):
        self.path, self.role, self.supporting, self.evidence = path, role, supporting, evidence
        self.raw = path.read_text(encoding="utf-8").splitlines()
        self.clean, self.code = clean_lines(self.raw)
        self.headings = []
        for i, line in enumerate(self.clean):
            m = HEADING.match(line)
            if m:
                self.headings.append(Heading(len(m.group(1)), m.group(2), i))
        for n, h in enumerate(self.headings):
            h.end = next((x.line for x in self.headings[n + 1:] if x.level <= h.level), len(self.raw))
        self.anchors = {}
        self.duplicate_anchors = []
        for i, line in enumerate(self.clean):
            for a in ANCHOR.findall(line):
                if a in self.anchors:
                    self.duplicate_anchors.append((a, i))
                self.anchors.setdefault(a, i)
        seen = {}
        for h in self.headings:
            s = slugify(h.text)
            if s in seen:
                seen[s] += 1
                s = f"{s}-{seen[s]}"
            else:
                seen[s] = 0
            h.slug = s
        self.slugs = {h.slug for h in self.headings}
        self.records = []

    @property
    def h2s(self):
        return [h for h in self.headings if h.level == 2]

    def section(self, name):
        return next((h for h in self.h2s if h.text == name), None)

    def section_of(self, line):
        cur = None
        for h in self.h2s:
            if h.line <= line:
                cur = h
        return cur.text if cur else None

    def body(self, h):
        return self.clean[h.line + 1:h.end]

    def body_end(self, h):
        """Where a section's own lines end: before any anchor-only lines directly above the next
        heading, and the blank lines among and below them. heading_path gives the lowest of those
        anchors to that heading, and any stacked above it stay with it; so a generated body never
        includes them, and fix never writes over them."""
        end, i = h.end, h.end - 1
        while i > h.line and not self.raw[i].strip():
            i -= 1
        while i > h.line and ANCHOR_LINE.match(self.raw[i]):
            end, i = i, i - 1
            while i > h.line and not self.raw[i].strip():
                i -= 1
        return end

    def raw_body(self, name):
        h = self.section(name)
        return "\n".join(self.raw[h.line + 1:self.body_end(h)]) if h else None

    def field(self, name):
        """The value of a `- **Name:** value` line anywhere in the document, as for a run record."""
        for line in self.clean:
            m = FIELD.match(line)
            if m and m.group(1).strip().lower() == name.lower():
                return plain(m.group(2)).strip()
        return None

    def period_field(self):
        """The `- **Period:** label` a run record may declare."""
        return self.field("period")


# ---------------------------------------------------------------- the specification

class FieldSpec:
    PATTERN = re.compile(r"^(?P<name>[^*=@]+?)(?P<req>\*)?(?:=(?P<enum>[^@]+))?(?:@(?P<role>\w+)(?:/(?P<alt>.+))?)?$")

    def __init__(self, text):
        m = self.PATTERN.match(text.strip())
        if not m:
            raise ValueError(f"bad field spec {text!r}")
        self.name = m.group("name").strip()
        self.required = bool(m.group("req"))
        self.enum = [v.strip() for v in m.group("enum").split("|")] if m.group("enum") else None
        self.role = m.group("role")
        self.alt = m.group("alt")


class RecordSpec:
    def __init__(self, kind, attrs, role):
        self.kind, self.role = kind, role
        self.id_re = re.compile(attrs["id"])
        self.sections = attrs.get("in", "").split("|")
        spec = attrs.get("fields") or attrs.get("columns") or ""
        self.fields = [FieldSpec(f) for f in spec.split(";") if f.strip()]
        self.dates = [d.strip() for d in attrs.get("dates", "").split(";") if d.strip()]

    def matches(self, id):
        return bool(self.id_re.fullmatch(id))


class Spec:
    def __init__(self, role, template):
        self.role, self.path = role, template
        raw = template.read_text(encoding="utf-8")
        self.lines = raw.splitlines()
        clean, _ = clean_lines(self.lines)
        self.clean = clean
        self.sections = []  # (name, optional, generated)
        for i, line in enumerate(clean):
            m = HEADING.match(line)
            if m and len(m.group(1)) == 2:
                flags = set()
                for nxt in self.lines[i + 1:]:
                    d = re.fullmatch(r"\s*<!--\s*ipq:(optional|generated)\s*-->\s*", nxt)
                    if not d:
                        break
                    flags.add(d.group(1))
                self.sections.append((m.group(2), "optional" in flags, "generated" in flags))
        self.records = [RecordSpec(k, dict(ATTR.findall(a)), role) for k, a in DIRECTIVE.findall(raw)]
        m = SCHEMA.search(raw)
        self.schema = int(m.group(1)) if m else 1  # templates before schema versions count as version 1

    @property
    def names(self):
        return [s[0] for s in self.sections]

    def generated(self, name):
        return any(s[0] == name and s[2] for s in self.sections)


def template_path(role):
    return TEMPLATES / ("index.md" if role == "index" else f"{role}.md")


RECORD_NOUN = {"record": "records", "table": "table rows", "condensed": "condensed lines"}


def floor_problems(upstream, override):
    """Why a project's template falls below what every IPQ document keeps (errors), and which
    required fields it makes optional (warnings: a project may relax a field, but visibly)."""
    out, relaxed = [], []
    first = next((l for l in override.clean if l.strip()), "")
    if not first.startswith("# "):
        out.append("the template must open with an H1 title")
    if not any(l.strip().startswith("**Answers:**") for l in override.clean):
        out.append("the template has no `**Answers:**` line")
    want = [n for n in FLOOR if n in upstream.names]
    got = override.names[:len(want)]
    if got != want:
        out.append(f"the sections must open with {', '.join(want)}, in that order")
    for name in want + ["At a glance"]:  # At a glance is the project's to keep or drop, but stays generated if kept
        sec = next((s for s in override.sections if s[0] == name), None)
        if sec and sec[1] and name in FLOOR:
            out.append(f"{name} cannot be optional")
        if sec and name != "Summary" and not sec[2]:
            out.append(f"{name} must stay generated")
    optional = {n for n, opt, _ in upstream.sections if opt}
    for u in upstream.records:
        if set(u.sections) <= optional:
            continue  # records of optional sections are the project's to keep or drop
        o = next((o for o in override.records if o.kind == u.kind and set(o.sections) & set(u.sections)), None)
        what = f"the {RECORD_NOUN.get(u.kind, u.kind + ' records')} under {' or '.join(u.sections)}"
        if not o:
            out.append(f"{what} are no longer declared")
            continue
        declared = {f.name.lower(): f for f in o.fields}
        lost = [f.name for f in u.fields if f.required and f.name.lower() not in declared]
        if lost:
            out.append(f"{what} drop {', '.join(lost)}")
        eased = [f.name for f in u.fields
                 if f.required and f.name.lower() in declared and not declared[f.name.lower()].required]
        if eased:
            relaxed.append(f"{what} make {', '.join(eased)} optional; "
                           f"upstream requires {'it' if len(eased) == 1 else 'them'}")
    return out, relaxed


def load_specs(root=None):
    """Each role's spec, preferring a project copy; the floor problems of each copy; the
    required fields each copy relaxes; and copies whose schema is behind upstream."""
    specs, problems, relaxed, overridden, behind = {}, [], [], [], []
    for role in ROLES + ["supporting"]:
        upstream = Spec(role, TEMPLATES / "supporting.md" if role == "supporting" else template_path(role))
        local = root / OVERRIDES / f"{role}.md" if root else None
        if local and local.exists():
            spec = Spec(role, local)
            overridden.append(role)
            errors, eased = floor_problems(upstream, spec)
            problems += [(local, p) for p in errors]
            relaxed += [(local, p) for p in eased]
            if spec.schema < upstream.schema:
                behind.append((local, f"your {role} template is based on schema version {spec.schema}; "
                                      f"the upstream template is version {upstream.schema}. See CHANGES.md "
                                      "in the ipq repository for what changed, then update your copy"))
            specs[role] = spec
        else:
            specs[role] = upstream
    return specs, problems, relaxed, overridden, behind


# ---------------------------------------------------------------- the document set

class DocSet:
    def __init__(self, root):
        self.root = root.resolve()
        self.cfg = {}
        cfg_path = self.root / "ipq.json"
        if cfg_path.exists():
            self.cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        self.files = dict(DEFAULT_FILES, **self.cfg.get("files", {}))
        self.budgets = dict(BUDGETS, **self.cfg.get("budgets", {}))
        h = self.cfg.get("history", "condense")
        self.history = h if isinstance(h, dict) else {r: h for r in ROLES}
        (self.specs, self.template_problems, self.template_relaxed,
         self.overridden, self.template_behind) = load_specs(self.root)
        self.docs = []
        self.by_role = {}
        for role in ROLES:
            p = self.root / self.files[role]
            if p.exists():
                d = Doc(p, role)
                self.docs.append(d)
                self.by_role[role] = d
        for role in ROLES:
            sub = self.root / Path(self.files[role]).stem
            if role != "index" and sub.is_dir():
                for p in sorted(sub.glob("*.md")):
                    self.docs.append(Doc(p, role, supporting=True))
        self.evidence = []
        for e in self.cfg.get("evidence", ["qa/runs"]):
            if (self.root / e).is_dir():
                self.evidence += [Doc(p, None, evidence=True) for p in sorted((self.root / e).rglob("*.md"))]
        known = {d.path for d in self.docs}
        self.unmapped = [p for p in sorted(self.root.glob("*.md")) if p not in known]
        self._anchor_cache = {}
        for d in self.docs:
            parse_records(d, self.specs[d.role].records)

    def role_of(self, path):
        path = path.resolve()
        for role in ROLES:
            if path == self.root / self.files[role]:
                return role
            if role != "index" and path.parent == self.root / Path(self.files[role]).stem:
                return role
        return None

    def evidence_doc(self, path):
        return next((d for d in self.evidence if d.path.resolve() == path), None)

    def targets(self, path):
        """Anchors and heading slugs a link into `path` may use."""
        path = path.resolve()
        if path not in self._anchor_cache:
            d = next((d for d in self.docs + self.evidence if d.path.resolve() == path), None) or Doc(path, None)
            self._anchor_cache[path] = set(d.anchors) | d.slugs
        return self._anchor_cache[path]

    def records(self, role, form=None):
        return [r for d in self.docs if d.role == role for r in d.records
                if form is None or r.form == form]

    def rel(self, path):
        try:
            return str(path.resolve().relative_to(self.root))
        except ValueError:
            return str(path)


def parse_records(doc, specs):
    """Find heading records, condensed records, and table records in `doc`."""
    def spec_for(id, kind):
        return next((s for s in specs if s.kind == kind and s.matches(id)), None)

    for h in doc.headings:
        if h.level < 3:
            continue
        m = RECORD_HEADING.match(plain(h.text).strip())
        if not m or not re.search(r"[\d-]", m.group(1)):
            continue
        spec = spec_for(m.group(1), "record")
        if not spec:
            continue
        r = Record(m.group(1), "heading", spec, doc.section_of(h.line), h.line, m.group(2))
        i, last = h.line + 1, None
        while i < h.end and not doc.clean[i].strip():
            i += 1
        while i < h.end:
            f = FIELD.match(doc.clean[i])
            if f:
                last = f.group(1).strip()
                r.fields[last] = (f.group(2).strip(), i)
            elif last and doc.clean[i].startswith("  ") and doc.clean[i].strip():
                v, ln = r.fields[last]
                r.fields[last] = (v + " " + doc.clean[i].strip(), ln)
            else:
                break
            i += 1
        r.body_words = sum(words(x) for x in doc.clean[i:h.end])
        r.body_start = i
        doc.records.append(r)

    for i, line in enumerate(doc.clean):
        m = CONDENSED.match(line)
        if m:
            id = plain(m.group(2)).strip()
            spec = spec_for(id, "condensed")
            if spec:
                r = Record(id, "condensed", spec, doc.section_of(i), i)
                r.anchor, r.text = m.group(1), line
                doc.records.append(r)

    tables = [s for s in specs if s.kind == "table"]
    i = 0
    while i < len(doc.clean) and tables:
        if not (doc.clean[i].lstrip().startswith("|") and i + 1 < len(doc.clean)
                and re.match(r"^\s*\|?\s*:?-{3,}", doc.clean[i + 1])):
            i += 1
            continue
        header = [plain(c).strip().lower() for c in split_row(doc.clean[i])]
        j = i + 2
        while j < len(doc.clean) and doc.clean[j].lstrip().startswith("|"):
            cells = split_row(doc.clean[j])
            first = cells[0] if cells else ""
            a = ANCHOR.search(first)
            id = plain(first).strip()
            spec = next((s for s in tables if s.matches(id)), None)
            if spec:
                r = Record(id, "table", spec, doc.section_of(j), j)
                r.anchor, r.text = a.group(1) if a else "", doc.clean[j]
                for name, value in zip(header, cells):
                    r.fields[name] = (value, j)
                doc.records.append(r)
            j += 1
        i = j


def run_command(cmd, cwd):
    """Run a project command from the docs directory: (succeeded, output)."""
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "timed out after 300 seconds"
    return p.returncode == 0, p.stdout if p.returncode == 0 else (p.stdout + p.stderr)


# ---------------------------------------------------------------- the report

class Report:
    def __init__(self, ds):
        self.ds, self.items = ds, []
        self.fresh = None  # the date freshness was judged at, when it was

    def add(self, level, doc_or_path, line, rule, msg):
        path = getattr(doc_or_path, "path", doc_or_path)
        self.items.append((level, path, line, rule, msg))

    def error(self, *a):
        self.add("error", *a)

    def warn(self, *a):
        self.add("warning", *a)

    def advise(self, *a):
        self.add("advice", *a)

    def count(self, level):
        return sum(1 for x in self.items if x[0] == level)

    def print(self, errors_only=False, advice=None):
        """Print findings. advice is None (hide it), "summary" (one line per file), or "all"."""
        cwd = Path.cwd()

        def shown(path):
            try:
                return path.resolve().relative_to(cwd)
            except ValueError:
                return path

        levels = {"error"} if errors_only else {"error", "warning"}
        if advice == "all":
            levels.add("advice")
        visible = [x for x in self.items if x[0] in levels]
        for level, path, line, rule, msg in sorted(visible, key=lambda x: (str(x[1]), x[2], x[3])):
            print(f"{shown(path)}:{line + 1}: {level} [{rule}] {msg}")
        if advice == "summary":
            block = visuals.size_block(self.ds)
            if block:
                print("\n" + block.title + "\n\n" + "\n".join(block.lines) + "\n")
            per = {}
            for level, path, _, rule, _ in self.items:
                if level == "advice":
                    per.setdefault(path, {}).setdefault(rule, 0)
                    per[path][rule] += 1
            names = {"paragraph": "long paragraph", "record-size": "long record",
                     "field-size": "long field", "condensed": "long finished line"}
            for path in sorted(per, key=str):
                parts = ["over the line budget" if r == "doc-size" else f"{n} {names.get(r, r)}{'s' * (n != 1)}"
                         for r, n in sorted(per[path].items())]
                print(f"{shown(path)}: advice — {'; '.join(parts)}")
        if len(visible) > 20:
            tally = {}
            for level, _, _, rule, _ in visible:
                tally[(level, rule)] = tally.get((level, rule), 0) + 1
            print("\nby rule:")
            for (level, rule), n in sorted(tally.items(), key=lambda x: -x[1]):
                print(f"  {n:6}  {level:7} {rule}")
        if self.fresh:
            print(f"freshness judged at {self.fresh}")
        e, w, a = self.count("error"), self.count("warning"), self.count("advice")
        tail = f", {a} advice" + ("" if advice else " (show with --advice)") if a else ""
        print(f"{e} error{'s' * (e != 1)}, {w} warning{'s' * (w != 1)}{tail}")
        return e


# ---------------------------------------------------------------- checks

FRESHNESS = {"glance_days": 14, "delta_days": 30, "evidence_days": 90}


def latest_evidence_date(ds, doc, r):
    """The newest date a qa row's evidence names: in a cited run's filename or Date line, or in the cell."""
    cell = r.fields.get("evidence", ("", 0))[0]
    dates = [dt.date.fromisoformat(x) for x in re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", LINK.sub("", cell))]
    for _, t in LINK.findall(cell):
        path = (doc.path.parent / t.partition("#")[0]).resolve()
        ev = ds.evidence_doc(path)
        for text in (path.name, ev.field("date") if ev else ""):
            m = re.search(r"\d{4}-\d{2}-\d{2}", text or "")
            if m:
                dates.append(dt.date.fromisoformat(m.group(0)))
    return max(dates) if dates else None


def check_freshness(ds, report, today):
    """Warnings about age, judged at `today`. Conformance never depends on these."""
    limits = dict(FRESHNESS, **(ds.cfg.get("freshness") or {}))
    for d in ds.docs:
        if d.supporting:
            continue
        stamp = visuals.stamp_of(d.raw_body("At a glance"))
        if stamp and (today - stamp).days > limits["glance_days"]:
            report.warn(d, d.section("At a glance").line, "stale",
                        f"At a glance was drawn {(today - stamp).days} days ago, on {stamp}; run `ipq.py fix`")
        if d.role == "delta":
            for r in d.records:
                if r.form != "heading":
                    continue
                esc = re.search(r"\d{4}-\d{2}-\d{2}", plain(r.fields.get("Escalate by", ("", 0))[0]))
                found = re.search(r"\d{4}-\d{2}-\d{2}", plain(r.fields.get("Found", ("", 0))[0]))
                if esc and dt.date.fromisoformat(esc.group(0)) < today:
                    report.warn(d, r.line, "stale", f"{r.id} is past its escalation date, {esc.group(0)}")
                elif found and (today - dt.date.fromisoformat(found.group(0))).days > limits["delta_days"]:
                    report.warn(d, r.line, "stale",
                                f"{r.id} has been open {(today - dt.date.fromisoformat(found.group(0))).days} days")
    active = {m["id"] for m in milestones(ds)[0] if m["status"] == "active"}
    for d in ds.docs:
        if d.role != "qa":
            continue
        for r in d.records:
            if r.form != "table":
                continue
            mids = [m for m in MILESTONE.findall(plain(r.fields.get("milestone", ("", 0))[0])) if m in active]
            newest = latest_evidence_date(ds, d, r)
            if mids and newest and (today - newest).days > limits["evidence_days"]:
                report.warn(d, r.line, "stale",
                            f"{r.id}: its newest evidence is {(today - newest).days} days old, and "
                            f"{mids[0]} is active; rerun it or confirm it still applies")


def check(ds, report, keep_anchors=None, fresh=None):
    for path, problem in ds.template_problems:
        report.error(path, 0, "template", problem)
    for path, msg in ds.template_relaxed:
        report.warn(path, 0, "relaxed", msg)
    for path, msg in ds.template_behind:
        report.warn(path, 0, "schema", msg)
    for role in ds.overridden:
        report.warn(ds.root / OVERRIDES / f"{role}.md", 0, "adapted",
                    f"this set adapts the {role} template; its rules come from this copy")
    pin = ds.cfg.get("ipq")
    if pin and ".".join(str(pin).split(".")[:2]) != ".".join(__version__.split(".")[:2]):
        report.warn(ds.root / "ipq.json", 0, "version", f"this set pins IPQ {pin}; the tool is {__version__}")
    for role in ROLES:
        if role not in ds.by_role and role != "index":
            report.warn(ds.root / ds.files[role], -1, "missing",
                        f"no {role} document; create it with `ipq.py init`, or record in README why the role does not apply")
    for p in ds.unmapped:
        report.warn(p, 0, "unmapped",
                    "not one of the canonical documents; map it in ipq.json, fold it into its owner, "
                    "or move it under the owning document's directory")
    for d in ds.docs:
        check_structure(ds, d, report)
        check_records(ds, d, report)
        check_links(ds, d, report)
        check_prose(ds, d, report)
    for d in ds.evidence:
        check_links(ds, d, report)
    check_ids(ds, report)
    check_coverage(ds, report)
    check_resolution(ds, report)
    check_evidence_scope(ds, report)
    check_states(ds, report)
    check_glance(ds, report)
    if keep_anchors:
        check_kept_anchors(ds, report, keep_anchors)
    if fresh is None and ds.cfg.get("freshness"):
        fresh = dt.date.today()
    if fresh:
        report.fresh = fresh
        check_freshness(ds, report, fresh)
    for cmd in ds.cfg.get("checks", []):
        ok, out = run_command(cmd, ds.root)
        parsed_error = False
        for line in out.splitlines():
            m = FINDING.match(line.strip())
            if m:
                parsed_error |= m.group(3) == "error"
                report.add(m.group(3), ds.root / m.group(1), int(m.group(2)) - 1, m.group(4), m.group(5))
        if not ok and not parsed_error:
            tail = out.strip().splitlines()[-1] if out.strip() else "no output"
            report.error(ds.root / "ipq.json", 0, "checks", f"`{cmd}` failed: {tail}")


def check_structure(ds, d, report):
    spec = ds.specs["supporting" if d.supporting else d.role]
    first = next((i for i, l in enumerate(d.clean) if l.strip()), 0)
    h1s = [h for h in d.headings if h.level == 1]
    if not h1s or h1s[0].line != first:
        report.error(d, first, "title", "the document must open with its H1 title")
    for h in h1s[1:]:
        report.error(d, h.line, "title", "only one H1 per document")
    first_h2 = d.h2s[0].line if d.h2s else len(d.raw)
    if not any(re.match(r"\*\*Answers:\*\*", l.strip()) for l in d.clean[:first_h2]):
        report.error(d, first, "answers", "no `**Answers:**` line between the title and the first section")

    names = [h.text for h in d.h2s]
    for h in d.h2s:
        if names.count(h.text) > 1 and d.h2s.index(h) != names.index(h.text):
            report.error(d, h.line, "sections", f"section {h.text!r} appears more than once")
    if d.supporting:
        if names[:2] != FLOOR:
            report.error(d, first_h2 if d.h2s else first, "sections",
                         "a supporting document opens with Summary, then Contents")
        if "History" in names and names[-1] != "History":
            report.error(d, d.section("History").line, "sections", "History must be the last section")
    else:
        allowed = spec.names
        for h in d.h2s:
            if h.text not in allowed:
                report.error(d, h.line, "sections",
                             f"{h.text!r} is not a {d.role} section; allowed, in order: {', '.join(allowed)}. "
                             "Make it an H3 under the section it serves, move it to a supporting document, "
                             "or adapt the template (`ipq.py template`)")
        missing = [name for name, optional, _ in spec.sections if not optional and name not in names]
        if missing:
            report.error(d, first_h2, "sections",
                         f"missing required section{'s' * (len(missing) > 1)}: {', '.join(missing)}")
        order = [n for n in names if n in allowed]
        expect = [n for n in allowed if n in order]
        for got, want in zip(order, expect):
            if got != want:
                report.error(d, d.section(got).line, "sections",
                             f"{got!r} is out of order; sections run: {', '.join(expect)}")
                break

    h = d.section("Summary")
    if h:
        n = sum(words(l) for l in d.body(h))
        if n > ds.budgets["summary_words"]:
            report.error(d, h.line, "summary",
                         f"Summary is {n} words; keep it to {ds.budgets['summary_words']} so a reader can stop there")
    h = d.section("Contents")
    if h and d.raw_body("Contents").strip() != render_contents(d).strip():
        report.error(d, h.line, "generated", "Contents is out of date; run `ipq.py fix`")


def check_records(ds, d, report):
    b = ds.budgets
    reported_tables = set()
    for r in d.records:
        spec = r.spec
        if not d.supporting and r.section not in spec.sections:
            hint = ""
            if r.form == "heading" and any(s.kind == "condensed" and s.matches(r.id) for s in ds.specs[d.role].records):
                hint = "; a finished entry is one line: see the template's condensed form"
            report.error(d, r.line, "placement",
                         f"{r.id} belongs under {' or '.join(spec.sections)}, not {r.section!r}{hint}")
        if r.form == "heading":
            prev = next((d.raw[i] for i in range(r.line - 1, -1, -1) if d.raw[i].strip()), "")
            if r.id.lower() not in ANCHOR.findall(prev):
                report.error(d, r.line, "anchor", f'put <a id="{r.id.lower()}"></a> on the line before {r.id}\'s heading')
            if r.body_words > b["record_words"]:
                report.advise(d, r.line, "record-size",
                              f"{r.id} is {r.body_words} words; a supporting document may read better")
        elif r.anchor != r.id.lower():
            report.error(d, r.line, "anchor", f'{r.id} needs <a id="{r.id.lower()}"></a> at the start of its entry')
        if r.form == "condensed":
            if words(r.text) > b["condensed_words"]:
                report.advise(d, r.line, "condensed",
                              f"{r.id} is {words(r.text)} words; a finished entry reads best as one line")
            for kind in spec.dates:
                if not re.search(rf"\b{re.escape(kind)} \d{{4}}-\d{{2}}-\d{{2}}\b", plain(r.text)):
                    report.error(d, r.line, "dates", f"{r.id}: the line needs `{kind} YYYY-MM-DD`")
            continue
        names = {k.lower(): k for k in r.fields}
        if r.form == "heading" and not r.fields:
            report.error(d, r.line, "fields",
                         f"{r.id} has no field list; put `- **Name:** value` lines right under its heading: "
                         + ", ".join(f.name for f in spec.fields if f.required))
            continue
        if r.form == "table":
            missing = [f.name for f in spec.fields if f.required and f.name.lower() not in names]
            key = (d.path, tuple(names))
            if missing and key not in reported_tables:
                reported_tables.add(key)
                report.error(d, r.line, "fields", f"this table has no {', '.join(missing)} column; "
                             f"columns run: {', '.join(f.name for f in spec.fields)}")
        for f in spec.fields:
            key = names.get(f.name.lower())
            if key is None:
                if f.required and r.form == "heading":
                    report.error(d, r.line, "fields", f"{r.id} has no {f.name!r} field")
                continue
            value, line = r.fields[key]
            check_value(ds, d, r, f, value, line, report)
        if r.form == "heading":
            declared = {f.name.lower() for f in spec.fields}
            for k, (value, line) in r.fields.items():
                if k.lower() not in declared:
                    report.warn(d, line, "fields",
                                f"{r.id}: {k!r} is not a field of this record; put it in the body, or adapt the template")
                elif words(value) > b["field_words"]:
                    report.advise(d, line, "field-size",
                                  f"{r.id}: {k} is {words(value)} words; a field reads best as a short value")


def check_value(ds, d, r, f, value, line, report):
    text = plain(value).strip()
    if f.enum:
        if text.lower() not in [e.lower() for e in f.enum]:
            report.error(d, line, "fields", f"{r.id}: {f.name} is {text!r}; use one of {', '.join(f.enum)}")
        return
    if f.required and text in BLANK:
        report.error(d, line, "fields", f"{r.id}: {f.name} is empty; write TBD if it is unknown")
        return
    if f.role and text.lower() != "tbd":
        if f.alt and text.lower() == f.alt.lower():
            return
        ok = any(ds.role_of((d.path.parent / t.split("#")[0]) if t.split("#")[0] else d.path) == f.role
                 for _, t in LINK.findall(value))
        if not ok:
            alt = f", or {f.alt!r}" if f.alt else ""
            report.error(d, line, "trace", f"{r.id}: {f.name} must link into the {f.role} document{alt}")


def check_links(ds, d, report):
    for a, line in d.duplicate_anchors:
        report.error(d, line, "anchor", f"anchor {a!r} is defined more than once")
    for i, line in enumerate(d.clean):
        for _, target in LINK.findall(without_code_spans(line)):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            path, _, frag = target.partition("#")
            dest = (d.path.parent / path) if path else d.path
            if not dest.exists():
                report.error(d, i, "link", f"{target}: no such file")
                continue
            if frag and dest.suffix == ".md" and frag not in ds.targets(dest):
                report.error(d, i, "link", f"{target}: no anchor or heading {frag!r} there")


def check_prose(ds, d, report):
    b = ds.budgets
    if len(d.raw) > b["doc_lines"]:
        where = "another supporting document" if d.supporting else f"supporting documents under {d.path.stem}/"
        report.advise(d, 0, "doc-size",
                      f"{len(d.raw)} lines, over the budget of {b['doc_lines']}; detail may read better in {where}")
    block, start = [], 0

    def flush():
        n = words(" ".join(block))
        if block and n > b["paragraph_words"]:
            report.advise(d, start, "paragraph", f"{n} words in one paragraph; a list or a break may read better")

    for i, line in enumerate(d.clean + [""]):
        if "{{" in without_code_spans(line):
            report.error(d, i, "placeholder", "a template placeholder is still here")
        s = line.strip()
        new_item = bool(re.match(r"^([-*+]|\d+[.)])\s", s))
        if not s or s.startswith(("#", "|")) or new_item:
            flush()
            block, start = ([s] if new_item else []), i
        else:
            if not block:
                start = i
            block.append(s)


def is_archive(d):
    return d.supporting and d.path.name == "archive.md"


def check_ids(ds, report):
    seen = {}
    condensed = {}
    archived = {}
    for d in ds.docs:
        for r in d.records:
            if r.form == "condensed" and not d.supporting:
                condensed[r.id] = (d, r)
            if is_archive(d) and r.form == "heading":
                archived[r.id] = (d, r)
    for d in ds.docs:
        for r in d.records:
            if is_archive(d) and r.form == "heading" and r.id in condensed:
                continue  # the full text of a finished record, beside its one line
            if r.id in seen:
                pd, pl = seen[r.id]
                report.error(d, r.line, "duplicate",
                             f"{r.id} is also defined at {ds.rel(pd.path)}:{pl + 1}; an identifier has one home")
            else:
                seen[r.id] = (d, r.line)
    for id, (d, r) in condensed.items():
        if ds.history.get(d.role, "condense") == "archive":
            if id not in archived:
                report.warn(d, r.line, "archive",
                            f"{id} is finished but has no full record in {Path(d.path.stem) / 'archive.md'}")
    for id, (d, r) in archived.items():
        if id not in condensed:
            report.warn(d, r.line, "archive", f"{id} is archived but has no one-line entry in its main document")


def check_evidence_scope(ds, report):
    """Evidence counts toward a milestone only for the revision the milestone is judged at."""
    ms, _ = milestones(ds)
    for m in ms:
        for rid, found, d, line in m["out_of_scope"]:
            names = ", ".join(f for f in found if f != "none") or "no revision"
            report.warn(d, line, "evidence-scope",
                        f"{rid}: its evidence is for {names}; {m['id']} is judged at revision {m['revision']}, "
                        "so it is not counted. Rerun the check, or cite a run record naming that revision")


def check_resolution(ds, report):
    """An open discrepancy that blocks a milestone names who can decide it, and dates are dates."""
    for d in ds.docs:
        if d.role != "delta" or d.supporting:
            continue
        for r in d.records:
            if r.form != "heading":
                continue
            names = {k.lower(): (v, line) for k, (v, line) in r.fields.items()}
            blocks = MILESTONE.findall(plain(names.get("blocks", ("", 0))[0]))
            if blocks and plain(names.get("decides", ("", 0))[0]).strip().lower() in BLANK | {"tbd"}:
                report.warn(d, r.line, "decider",
                            f"{r.id} blocks {', '.join(blocks)} but names no one who Decides it")
            esc = names.get("escalate by")
            if esc and not re.search(r"\b\d{4}-\d{2}-\d{2}\b", plain(esc[0])):
                report.error(d, esc[1], "fields", f"{r.id}: Escalate by must be a date, YYYY-MM-DD")


def check_coverage(ds, report):
    verified = set()
    for r in ds.records("qa", "table"):
        v = next((val for k, (val, _) in r.fields.items() if k == "verifies"), "")
        verified |= {t.partition("#")[2] for _, t in LINK.findall(v)}
    for d in ds.docs:
        if d.role != "prd":
            continue
        for r in d.records:
            status = plain(r.fields.get("Status", ("", 0))[0]).strip().lower()
            if r.form == "heading" and status == "accepted" and r.id.lower() not in verified:
                report.warn(d, r.line, "coverage", f"{r.id} is accepted but no qa row verifies it")


def check_states(ds, report):
    """Every state a screen lists is described in its body as `- **State:** ...`."""
    for d in ds.docs:
        if d.role != "ux":
            continue
        for r in d.records:
            if r.form != "heading" or not r.id.startswith("SCR-"):
                continue
            h = next(h for h in d.headings if h.line == r.line)
            described = {m.group(1).strip().lower() for l in d.clean[r.body_start:h.end]
                         for m in [FIELD.match(l)] if m}
            for state, specified in visuals.screen_states(r).items():
                if specified and state not in described:
                    report.warn(d, r.fields["States"][1] if "States" in r.fields else r.line, "states",
                                f"{r.id} lists the {state} state but its body has no `- **{state.capitalize()}:**` line")


def check_glance(ds, report):
    for d in ds.docs:
        if d.supporting or d.section("At a glance") is None:
            continue
        current = d.raw_body("At a glance")
        as_of = visuals.stamp_of(current) or dt.date.today()
        body, findings = visuals.render_glance(ds, d.role, as_of)
        h = d.section("At a glance")
        for f in findings:
            report.error(d, h.line, "visual", f"At a glance cannot be drawn: {f}")
        if not findings and current.strip() != body.strip():
            report.error(d, h.line, "generated", "At a glance is out of date; run `ipq.py fix`")


def heading_path(d, line):
    """The chain of headings that governs `line`. An anchor just above a heading belongs to that heading."""
    nxt = next((i for i in range(line + 1, len(d.clean)) if d.clean[i].strip()), None)
    if nxt is not None and any(h.line == nxt for h in d.headings):
        line = nxt
    chain = [h for h in d.headings if h.line <= line < h.end and h.level > 1]
    return " › ".join(plain(h.text).strip() for h in sorted(chain, key=lambda h: h.level))


def anchor_table(ds):
    """{file#anchor: heading path} for every explicit anchor in every Markdown file under DOCS."""
    out = {}
    for path in sorted(ds.root.rglob("*.md")):
        if OVERRIDES.parts[0] in path.relative_to(ds.root).parts:
            continue
        d = Doc(path, None)
        for a in sorted(d.anchors, key=d.anchors.get):
            out[f"{ds.rel(path)}#{a}"] = heading_path(d, d.anchors[a])
    return out


def anchors(ds):
    """Every explicit anchor, mapped or not, with the heading path that governs it."""
    return [f"{k}\t{v}" if v else k for k, v in anchor_table(ds).items()]


def check_kept_anchors(ds, report, listing):
    have = anchor_table(ds)
    by_id = {}
    for entry in have:
        f, _, a = entry.partition("#")
        by_id.setdefault(a, []).append(f)
    for n, line in enumerate(Path(listing).read_text(encoding="utf-8").splitlines()):
        entry, _, old_path = line.strip().partition("\t")
        if not entry:
            continue
        f, _, a = entry.partition("#")
        if entry in have:
            if old_path and have[entry] != old_path.strip():
                report.warn(ds.root / f, 0, "context",
                            f"anchor {a!r} was under {old_path.strip()!r} and is now under {have[entry] or 'the title'!r}; "
                            "check that what it points to still reads with the same scope")
            continue
        moved = by_id.get(a)
        hint = f"; it is now in {', '.join(moved)} — leave the anchor where links point, or update every link" if moved else ""
        report.error(ds.root / f, 0, "kept-anchor", f"anchor {a!r} is gone{hint} (listed at {listing}:{n + 1})")


def links_to(ds, target):
    """Every link under DOCS that points at `target` (`file#anchor`, or a bare anchor), with its line."""
    tfile, _, tfrag = target.rpartition("#") if "#" in target else ("", "", target)
    out = []
    for path in sorted(ds.root.rglob("*.md")):
        d = Doc(path, None)
        for i, line in enumerate(d.clean):
            for _, t in LINK.findall(line):
                lpath, _, frag = t.partition("#")
                dest = (path.parent / lpath).resolve() if lpath else path.resolve()
                if frag == tfrag and (not tfile or dest == (ds.root / tfile).resolve()):
                    out.append(f"{ds.rel(path)}:{i + 1}: {d.raw[i].strip()}")
    return out


# ---------------------------------------------------------------- generated sections

def render_contents(d):
    out = []
    for h in d.h2s:
        if h.text == "Contents":
            continue
        recs = [r for r in d.records if d.section_of(r.line) == h.text]
        line = f"- [{plain(h.text)}](#{h.slug})"
        if recs:
            line += f" · {len(recs)} {'entry' if len(recs) == 1 else 'entries'}"
        out.append(line)
        rec_lines = {r.line for r in recs}
        for s in d.headings:
            if s.level == 3 and h.line < s.line < h.end and s.line not in rec_lines:
                out.append(f"  - [{plain(s.text)}](#{s.slug})")
    return "\n" + "\n".join(out) + "\n"


def milestones(ds):
    """Each milestone with its work and verification counts, in roadmap order."""
    ms = []
    for r in ds.records("roadmap", "heading"):
        if not MILESTONE.fullmatch(r.id):
            continue
        f = {k.lower(): plain(v).strip() for k, (v, _) in r.fields.items()}
        ms.append(dict(id=r.id, title=r.title, status=f.get("status", "planned").lower(),
                       target=f.get("target", "TBD") or "TBD",
                       depends=[m for m in MILESTONE.findall(f.get("depends on", "")) if m != r.id],
                       work={"done": 0, "now": 0, "next": 0, "blocked": 0, "later": 0},
                       revision=f.get("revision", "") if f.get("revision", "").lower() not in EMPTY else "",
                       blocked=[], checks=0, evidenced=0, deltas=[], out_of_scope=[]))
    by_id = {m["id"]: m for m in ms}
    unassigned = 0
    for d in ds.docs:
        if d.role != "backlog" or d.supporting:
            continue
        for r in d.records:
            src = r.text if r.form == "condensed" else r.fields.get("Milestone", ("", 0))[0]
            ids = [m for m in MILESTONE.findall(plain(src)) if m in by_id]
            if not ids:
                unassigned += 1
                continue
            m = by_id[ids[0]]
            state = "done" if r.form == "condensed" else (r.section or "").lower()
            if state in m["work"]:
                m["work"][state] += 1
            if state == "blocked":
                m["blocked"].append(r.id)
    for d in ds.docs:
        if d.role != "qa":
            continue
        for r in d.records:
            if r.form != "table":
                continue
            ids = [m for m in MILESTONE.findall(plain(r.fields.get("milestone", ("", 0))[0])) if m in by_id]
            if not ids:
                continue
            m = by_id[ids[0]]
            m["checks"] += 1
            evidenced, in_scope, found = evidence_scope(ds, d, r, m["revision"])
            if in_scope:
                m["evidenced"] += 1
            elif evidenced:
                m["out_of_scope"].append((r.id, sorted(found), d, r.line))
    for d in ds.docs:
        if d.role != "delta" or d.supporting:
            continue
        for r in d.records:
            if r.form == "heading":
                for mid in set(MILESTONE.findall(plain(r.fields.get("Blocks", ("", 0))[0]))):
                    if mid in by_id:
                        by_id[mid]["deltas"].append(r.id)
    return ms, unassigned


def evidence_scope(ds, doc, r, revision):
    """Whether a qa row's evidence counts for a milestone judged at `revision`.

    Returns (evidenced, in_scope, found): evidenced when the row cites any evidence;
    in_scope when no revision is set, or a cited run record names that revision;
    found is the set of revisions the cited runs name ("none" for a run or cell
    that names no revision).
    """
    cell = r.fields.get("evidence", ("", 0))[0]
    if plain(cell).strip().lower() in EMPTY:
        return False, False, set()
    if not revision:
        return True, True, set()
    found = set()
    for _, t in LINK.findall(cell):
        ev = ds.evidence_doc((doc.path.parent / t.partition("#")[0]).resolve())
        found.add((ev.field("revision") if ev else None) or "none")
    if not found:
        found.add("none")
    return True, revision in found, found


MARK = {"done": "[x]", "active": "[>]", "planned": "[ ]", "cut": "[-]"}
STATUSES = tuple(MARK)


def replace_body(d, name, body):
    h = d.section(name)
    if not h:
        return False
    end = d.body_end(h)
    old = "\n".join(d.raw[h.line + 1:end]).strip()
    if old == body.strip():
        return False
    new = d.raw[:h.line + 1] + body.rstrip("\n").split("\n") + [""] + d.raw[end:]
    d.path.write_text("\n".join(new) + "\n", encoding="utf-8")
    return True


def glance_update(ds, d, today):
    """The At a glance body fix should write, or None to leave it; and any findings."""
    current = d.raw_body("At a glance")
    stamp = visuals.stamp_of(current)
    fresh, findings = visuals.render_glance(ds, d.role, today)
    if findings:
        return None, findings
    if stamp and stamp != today:
        # Keep the old stamp when nothing but the date would change, so fix does not churn daily.
        old, _ = visuals.render_glance(ds, d.role, stamp)
        if old.strip() == current.strip() and fresh.replace(str(today), str(stamp)) == old:
            return None, []
    return fresh, []


def fix(root, today=None):
    """Regenerate every generated section. Returns (changed, problems)."""
    today = today or dt.date.today()
    changed, problems = [], []
    paths = [d.path for d in DocSet(root).docs]
    for path in paths:
        ds = DocSet(root)  # reread each time: a rewrite moves lines
        d = next(x for x in ds.docs if x.path == path)
        if not d.supporting and d.section("At a glance") is not None:
            body, findings = glance_update(ds, d, today)
            problems += [f"{ds.rel(d.path)}: At a glance kept as it was: {f}" for f in findings]
            if body is not None and replace_body(d, "At a glance", body):
                changed.append(f"{ds.rel(d.path)}: At a glance")
    for path in paths:
        ds = DocSet(root)
        d = next(x for x in ds.docs if x.path == path)
        if replace_body(d, "Contents", render_contents(d)):
            changed.append(f"{ds.rel(d.path)}: Contents")
    return changed, problems


# ---------------------------------------------------------------- init, template, and the web view

def skeleton(ds, role, product, optional=False):
    """A role's template as a document to fill: directives gone, links to this project's filenames."""
    text = ds.specs[role].path.read_text(encoding="utf-8")
    text = SCHEMA.sub("", DIRECTIVE.sub("", text))
    if not optional:
        # Optional sections are left out; an author adds one, in template order, when it has content.
        text = re.sub(r"^## [^\n]*\n[ \t]*<!--\s*ipq:optional\s*-->.*?(?=^## |\Z)", "", text, flags=re.S | re.M)
    text = re.sub(r"[ \t]*<!--\s*ipq:(generated|optional)\s*-->[ \t]*\n", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).replace("{{product}}", product)
    for other in ROLES:
        if ds.files[other] != DEFAULT_FILES[other]:  # link to the files this project actually has
            text = re.sub(rf"\]\({re.escape(DEFAULT_FILES[other])}(?=[#)])", f"]({ds.files[other]}", text)
    return text


def init(root, product):
    root.mkdir(parents=True, exist_ok=True)
    made = []
    ds = DocSet(root)
    for role in ROLES:
        dest = root / ds.files[role]
        if dest.exists():
            continue
        dest.write_text(skeleton(ds, role, product), encoding="utf-8")
        made.append(dest.name)
    fix(root)
    return made


def adapt(root, role):
    src = TEMPLATES / "supporting.md" if role == "supporting" else template_path(role)
    dest = root / OVERRIDES / f"{role}.md"
    if dest.exists():
        return f"{dest} already exists; edit it"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return f"copied the {role} template to {dest}; edit it, and check holds it to the IPQ floor"


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{ --bg:#fafaf9; --fg:#1c1917; --muted:#78716c; --card:#fff; --line:#e7e5e4;
  --track:#e7e5e4; --done:#15803d; --active:#1d4ed8; --planned:#a8a29e; --cut:#b91c1c; --warn:#b45309; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#1c1917; --fg:#f5f5f4; --muted:#a8a29e;
  --card:#292524; --line:#44403c; --track:#44403c; --done:#4ade80; --active:#60a5fa;
  --planned:#78716c; --cut:#f87171; --warn:#fbbf24; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; padding:24px 16px; background:var(--bg); color:var(--fg);
  font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width:1100px; margin:0 auto; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
.sub {{ color:var(--muted); margin:0 0 24px; }}
.track {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:16px; }}
.m {{ background:var(--card); border:1px solid var(--line); border-top:4px solid var(--c);
  border-radius:8px; padding:14px 16px; }}
.m.cut {{ opacity:.6; border-style:dashed; }}
.id {{ font-weight:700; }} .t {{ font-weight:600; }}
.meta {{ color:var(--muted); font-size:13px; margin:2px 0 12px; }}
.pill {{ display:inline-block; padding:0 8px; border-radius:99px; font-size:12px;
  font-weight:600; color:var(--card); background:var(--c); }}
.row {{ font-size:13px; margin:8px 0 2px; display:flex; justify-content:space-between; }}
.bar {{ height:8px; background:var(--track); border-radius:4px; overflow:hidden; }}
.bar i {{ display:block; height:100%; background:var(--c); }}
.note {{ font-size:13px; margin-top:10px; color:var(--warn); }}
.dep {{ font-size:13px; color:var(--muted); margin-top:10px; }}
</style></head><body><main>
<h1>{title}</h1>
<p class="sub">{subtitle}</p>
<div class="track">{cards}</div>
</main></body></html>
"""


def render_html(ds):
    ms, unassigned = milestones(ds)
    cards = []
    for m in ms:
        w = m["work"]
        total = sum(w.values())

        def meter(label, done, of):
            pct = 100 * done / of if of else 0
            return (f'<div class="row"><span>{label}</span><span>{done}/{of}</span></div>'
                    f'<div class="bar"><i style="width:{pct:.0f}%"></i></div>')

        notes = []
        if m["blocked"]:
            notes.append(f"{len(m['blocked'])} blocked: {', '.join(m['blocked'])}")
        if m["deltas"]:
            notes.append(f"{len(m['deltas'])} open delta{'s' * (len(m['deltas']) != 1)}: {', '.join(m['deltas'])}")
        status = m["status"] if m["status"] in STATUSES else "planned"
        cards.append(
            f'<section class="m {status}" style="--c:var(--{status})">'
            f'<div><span class="id">{html.escape(m["id"])}</span> '
            f'<span class="t">{html.escape(m["title"])}</span></div>'
            f'<div class="meta"><span class="pill">{html.escape(m["status"])}</span> '
            f'· {html.escape(m["target"])}</div>'
            + meter("Work done", w["done"], total) + meter("Checks with evidence", m["evidenced"], m["checks"])
            + (f'<div class="dep">After {", ".join(m["depends"])}</div>' if m["depends"] else "")
            + "".join(f'<div class="note">{html.escape(n)}</div>' for n in notes)
            + "</section>")
    title = "Roadmap"
    if "roadmap" in ds.by_role:
        h1 = next((h.text for h in ds.by_role["roadmap"].headings if h.level == 1), title)
        title = plain(h1)
    sub = f"{len(ms)} milestones"
    if unassigned:
        sub += f" · {unassigned} backlog item{'s' * (unassigned != 1)} with no milestone"
    return PAGE.format(title=html.escape(title), subtitle=html.escape(sub), cards="".join(cards))


# ---------------------------------------------------------------- command line

def main(argv=None):
    ap = argparse.ArgumentParser(prog="ipq.py", description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--version", action="version", version=f"ipq {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "fix", "init", "roadmap", "anchors", "template", "skeleton", "links-to"):
        p = sub.add_parser(name)
        if name in ("template", "skeleton"):
            p.add_argument("role", choices=ROLES + ["supporting"])
        if name == "links-to":
            p.add_argument("target", help="file#anchor, or a bare anchor")
        p.add_argument("docs", nargs="?", default="docs", type=Path)
        if name == "check":
            p.add_argument("--errors-only", action="store_true")
            p.add_argument("--advice", nargs="?", const="summary", choices=["summary", "all"])
            p.add_argument("--keep-anchors", type=Path, metavar="FILE",
                           help="error on any anchor listed in FILE (from `ipq.py anchors`) that is gone")
            p.add_argument("--fresh", nargs="?", const="today", metavar="DATE",
                           help="also warn about age, judged at DATE (default today); never an error")
        if name == "init":
            p.add_argument("--product", required=True)
        if name == "skeleton":
            p.add_argument("--product", default="{{product}}", help="the name to put in the title")
        if name == "roadmap":
            p.add_argument("--html", type=Path, help="write the roadmap as a web page to this file")
    a = ap.parse_args(argv)

    if a.cmd == "init":
        made = init(a.docs, a.product)
        print("created " + ", ".join(made) if made else "every document already exists; nothing created")
        return 0
    if not a.docs.is_dir():
        print(f"{a.docs}: not a directory", file=sys.stderr)
        return 2
    if a.cmd == "template":
        print(adapt(a.docs, a.role))
        return 0
    ds = DocSet(a.docs)
    if a.cmd == "skeleton":
        print(skeleton(ds, a.role, a.product, optional=True), end="")
        return 0
    if a.cmd == "check":
        report = Report(ds)
        fresh = None
        if a.fresh:
            fresh = dt.date.today() if a.fresh == "today" else dt.date.fromisoformat(a.fresh)
        check(ds, report, a.keep_anchors, fresh)
        return 1 if report.print(a.errors_only, a.advice) else 0
    if a.cmd == "fix":
        changed, problems = fix(a.docs)
        print("\n".join(f"regenerated {c}" for c in changed) or "generated sections are current")
        for p in problems:
            print(p)
        return 1 if problems else 0
    if a.cmd == "anchors":
        print("\n".join(anchors(ds)))
        return 0
    if a.cmd == "links-to":
        found = links_to(ds, a.target)
        print("\n".join(found) or f"nothing under {a.docs} links to {a.target}")
        return 0
    if a.cmd == "roadmap":
        if a.html:
            a.html.write_text(render_html(ds), encoding="utf-8")
            print(f"wrote {a.html}")
            return 0
        d = ds.by_role.get("roadmap")
        body = d.raw_body("At a glance") if d else None
        if not body:
            print("the roadmap has no At a glance section; run `ipq.py fix`", file=sys.stderr)
            return 1
        print(re.sub(r"<!--.*?-->\s*", "", body, flags=re.S).replace("```text\n", "").replace("```\n", "").strip())
        return 0


if __name__ == "__main__":
    sys.exit(main())
