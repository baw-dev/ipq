"""ipq_visuals: the monospace blocks in each document's At a glance section.

Every block is generated from records the documents already hold. A block
function takes a Ctx and returns a Block, None when it has nothing to show, or
a list of findings when records are missing or contradict each other. A
finding means the block is not drawn: nothing plausible is ever rendered in
place of evidence.

Rules every block keeps (SKILL.md, "At a glance"):
- the title names the measure
- exact counts are printed beside or under the marks; an observed zero is 0
  and a quiet period is ·
- no forecasts, trend lines, net-direction arrows or completion dates, and no
  past percentage against today's denominator
- lines fit in WIDTH columns; a block that would not fit scales, and its
  caption says "each ▓ ≈ N"
- a plain-text fallback line follows every block, outside its code fence
- only GLYPHS are used
"""
import datetime as dt
import math
import re
import string
import textwrap
from collections import Counter

import ipq

WIDTH = 78

# Glyphs measured on 2026-09-29 for one-column width: canvas measureText in
# Chromium for Menlo, Monaco, Courier New, Andale Mono and PT Mono, and the
# hmtx advance widths of SF-Mono-Regular.otf, Menlo.ttc and Monaco.ttf.
# Every glyph below is exactly one column in each, or absent from Monaco and
# drawn one column wide by its fallback. Excluded: ▒ (0.833 columns in
# Monaco's own glyph) and ◆ (missing from SF Mono, GitHub's first choice on a
# Mac). A project may still choose ▒ for "done" in ipq.json.
GLYPHS = set(string.printable) - set("\t\r\x0b\x0c") | set("░▓█·−○×┆▲▶─≈")

MARKS = {
    "done": "▓",       # done, evidenced, linked, specified, accepted, work
    "none": "░",       # not yet, missing, proposed
    "na": "−",         # not required, not applicable, rejected
    "quiet": "·",      # a period of a different kind, or none planned
    "decision": "▲",   # waits on a decision
    "external": "○",   # waits on someone outside the team
    "superseded": "×",
    "other": "█",      # a project-defined status
    "budget": "┆",
}

DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
BLOCKS_BY_ROLE = {
    "roadmap": ["milestones", "velocity", "waiting"],
    "prd": ["trace", "decisions"],
    "ux": ["states", "decisions"],
    "tdd": ["decisions"],
    "qa": ["evidence", "decisions"],
    "delta": ["flow", "awaiting"],
}
STAMP = re.compile(r"as of (\d{4}-\d{2}-\d{2})")


class Block:
    """A chart. `measures` says what is counted, over what, and what is left out;
    `excluded` names records the chart could not use, so a partial view says so."""

    def __init__(self, name, title, lines, fallback, measures="", excluded=()):
        self.name, self.title, self.lines, self.fallback = name, title, lines, fallback
        self.measures, self.excluded = measures, list(excluded)

    def render(self):
        head = [self.title] + (textwrap.wrap(self.measures, WIDTH) if self.measures else [])
        lines = list(self.lines)
        fallback = self.fallback
        if self.excluded:
            ids = ", ".join(self.excluded)
            lines += [""] + textwrap.wrap(f"partial: {len(self.excluded)} left out, see below", WIDTH)
            fallback += f" Left out for missing data: {ids}."
        return "\n".join(["```text"] + head + [""] + lines + ["```", "", fallback])


class Ctx:
    def __init__(self, ds, as_of):
        self.ds, self.as_of = ds, as_of
        self.cfg = ds.cfg
        self.marks = dict(MARKS, **self.cfg.get("glyphs", {}))
        cfg = self.cfg.get("period", {"unit": "week"})
        self.period = make_period(ds, cfg)
        flow = self.cfg.get("flow")
        self.flow_period = make_period(ds, flow) if flow else self.period

    def m(self, name):
        return self.marks[name]


# ---------------------------------------------------------------- periods

def make_period(ds, cfg):
    unit = cfg.get("unit", "week")
    if unit == "iteration":
        return Iterations(ds, cfg)
    if unit in Calendar.UNITS:
        return Calendar(cfg)
    raise ValueError(f"period unit {unit!r}: use one of {', '.join(Calendar.UNITS + ('iteration',))}")


class Calendar:
    """Periods cut from the calendar: a day, week, month, quarter, or a fixed-length sprint.

    Keys sort in time order; labels are what a reader sees. Every period
    exists whether or not anything happened in it, so an empty one shows 0.
    """
    UNITS = ("day", "week", "month", "quarter", "sprint")

    def __init__(self, cfg):
        self.unit = cfg.get("unit", "week")
        self.name = self.unit
        self.quiet = {str(k): v for k, v in cfg.get("quiet", {}).items()}
        self.findings = []
        if self.unit == "sprint":
            self.start = dt.date.fromisoformat(cfg.get("start", "1970-01-05"))
            self.days = int(cfg.get("days", 14))

    def of(self, d):
        if self.unit == "day":
            return d.toordinal()
        if self.unit == "week":
            y, w, _ = d.isocalendar()
            return (y, w)
        if self.unit == "month":
            return (d.year, d.month)
        if self.unit == "quarter":
            return (d.year, (d.month - 1) // 3 + 1)
        return (d - self.start).days // self.days + 1

    def next(self, k):
        if self.unit == "week":
            y, w, _ = (dt.date.fromisocalendar(k[0], k[1], 1) + dt.timedelta(days=7)).isocalendar()
            return (y, w)
        if self.unit == "month":
            return (k[0] + k[1] // 12, k[1] % 12 + 1)
        if self.unit == "quarter":
            return (k[0] + k[1] // 4, k[1] % 4 + 1)
        return k + 1

    def parse(self, label):
        """A key from a run record's Period field, or None."""
        label = str(label).strip()
        forms = {
            "day": (r"(\d{4}-\d{2}-\d{2})", lambda m: dt.date.fromisoformat(m.group(1)).toordinal()),
            "week": (r"(\d{4})-?W(\d{1,2})", lambda m: (int(m.group(1)), int(m.group(2)))),
            "month": (r"(\d{4})-(\d{2})", lambda m: (int(m.group(1)), int(m.group(2)))),
            "quarter": (r"(\d{4})-?Q([1-4])", lambda m: (int(m.group(1)), int(m.group(2)))),
            "sprint": (r"(?:sprint\s*)?(\d+)", lambda m: int(m.group(1))),
        }
        pattern, key = forms[self.unit]
        m = re.fullmatch(pattern, label, re.I)
        return key(m) if m else None

    def label(self, k):
        if self.unit == "day":
            return dt.date.fromordinal(k).strftime("%m-%d")
        if self.unit == "week":
            return f"W{k[1]:02d}"
        if self.unit == "month":
            return f"{k[0]}-{k[1]:02d}"
        if self.unit == "quarter":
            return f"{k[0]}Q{k[1]}"
        return str(k)

    def attribute(self, day=None, links=(), label=None):
        """The period of one event: its Period label if it has one, else its date."""
        if label:
            k = self.parse(label)
            return k if k is not None else f"Period {label!r} is not a {self.unit}"
        return self.of(day) if day else None

    def window(self, keys, as_of):
        keys = list(keys)
        last = max(keys + [self.of(as_of)])
        out, k = [], min(keys)
        while k <= last:
            out.append(k)
            k = self.next(k)
        return out

    def now(self, as_of):
        return self.of(as_of)

    def is_quiet(self, k, count):
        return self.label(k) in self.quiet and not count

    def quiet_captions(self, keys):
        return sorted({f"a quiet {self.name}: {self.quiet[self.label(k)]}" for k in keys if self.label(k) in self.quiet})


class Iterations:
    """Periods bounded by the one-line record written when each iteration closes.

    Nothing is declared before an iteration starts. An iteration becomes a
    period when its closing line is written: roadmap Iterations lines (the
    default), or backlog Done lines when every iteration is one backlog item.
    Iterations sort by close date, then by the number in their identifier,
    so several may close on one day. Each covers whatever happened after the
    previous one closed, so iterations may be any length.

    An event belongs to an iteration by link first: a run the closing line
    links, or a link to the closing line itself. Only an unlinked event falls
    back to its date, and only when one iteration fits that date. Anything
    after the last close belongs to the open iteration.
    """

    def __init__(self, ds, cfg):
        self.unit = "iteration"
        self.name = cfg.get("name", "iteration")
        source = cfg.get("from", "roadmap")
        section = {"roadmap": "Iterations", "backlog": "Done"}.get(source)
        if not section:
            raise ValueError(f'iterations come "from" roadmap or backlog, not {source!r}')
        match = cfg.get("match")
        self.items, self.findings = [], []
        for d in ds.docs:
            if d.role != source or d.supporting:
                continue
            for r in d.records:
                if r.form != "condensed" or r.section != section:
                    continue
                text = ipq.plain(r.text)
                if match and not re.search(rf"\b{re.escape(match)}\b", text, re.I):
                    continue
                m = re.search(r"\b(?:closed|done) (\d{4}-\d{2}-\d{2})\b", text)
                if not m:
                    self.findings.append(f"{r.id}: its closing line has no `closed YYYY-MM-DD`")
                    continue
                digits = re.findall(r"\d+", r.id)
                links = set()
                for _, t in ipq.LINK.findall(r.text):
                    path, _, frag = t.partition("#")
                    links.add(((d.path.parent / path).resolve() if path else d.path.resolve(), frag))
                self.items.append(dict(id=r.id, label=str(int(digits[-1])) if digits else r.id,
                                       close=dt.date.fromisoformat(m.group(1)), num=int(digits[-1]) if digits else 0,
                                       anchor=(d.path.resolve(), r.anchor),
                                       runs={p for p, frag in links if not frag and ds.evidence_doc(p)}))
        self.items.sort(key=lambda it: (it["close"], it["num"]))
        self.open = len(self.items)
        self.by_run, self.by_anchor = {}, {}
        for i, it in enumerate(self.items):
            self.by_anchor[it["anchor"]] = i
            for run in it["runs"]:
                if run in self.by_run:
                    other = self.items[self.by_run[run]]["id"]
                    self.findings.append(f"{run.name} is linked by both {other} and {it['id']}; a run belongs to one {self.name}")
                self.by_run.setdefault(run, i)
        labels = Counter(it["label"] for it in self.items)
        self.findings += [f"two {self.name}s are labelled {lab}" for lab, n in labels.items() if n > 1]

    def label(self, k):
        return self.items[k]["label"] if k < self.open else "open"

    def attribute(self, day=None, links=(), label=None):
        for link in links:
            if link in self.by_anchor:
                return self.by_anchor[link]
            if link[0] in self.by_run:
                return self.by_run[link[0]]
        if label:
            wanted = re.sub(r"^\D*", "", str(label).strip()).lstrip("0") or "0"
            hit = [i for i, it in enumerate(self.items) if it["label"] == wanted or it["id"] == label]
            return hit[0] if hit else f"Period {label!r} names no closed {self.name}"
        if not day:
            return None
        same = [i for i, it in enumerate(self.items) if it["close"] == day]
        if len(same) > 1:
            names = [self.items[i]["id"] for i in same]
            ids = ", ".join(names) if len(names) <= 4 else f"{len(names)} {self.name}s ({names[0]} to {names[-1]})"
            return (f"{day} is the close date of {ids}; link the evidence from its {self.name}'s closing line, "
                    f"or link the closing line from the record")
        if same:
            return same[0]
        return next((i for i, it in enumerate(self.items) if it["close"] > day), self.open)

    def window(self, keys, as_of):
        return list(range(self.open)) + ([self.open] if self.open in keys else [])

    def now(self, as_of):
        return self.open

    def is_quiet(self, k, count):
        return k < self.open and not count and not self.items[k]["runs"]

    def quiet_captions(self, keys):
        return [f"a {self.name} that linked no run"] if any(self.is_quiet(k, 0) for k in keys) else []


def date(text):
    m = DATE.search(text or "")
    return dt.date.fromisoformat(m.group(1)) if m else None


def fit(text, width=WIDTH):
    return text if len(text) <= width else text[:width - 1] + "~"


def plural(n, word, many=None):
    return f"{n} {word if n == 1 else (many or word + 's')}"


def columns(rows, keys, colw, prefix, width=WIDTH):
    """Lay out labelled rows of per-key cells in bands that fit `width`."""
    per = max(1, (width - len(prefix)) // colw)
    out = []
    for i in range(0, len(keys), per):
        band = keys[i:i + per]
        for name, cell in rows:
            out.append((f"{name:<{len(prefix)}}" + "".join(f"{cell(k):>{colw}}" for k in band)).rstrip())
        out.append("")
    return out[:-1]


# ---------------------------------------------------------------- shared data

def field(r, name):
    for k, (v, _) in r.fields.items():
        if k.lower() == name.lower():
            return v
    return ""


def links_into(ds, doc, text, role):
    """Anchors in `role`'s documents that `text` in `doc` links to."""
    out = set()
    for _, t in ipq.LINK.findall(text):
        path, _, frag = t.partition("#")
        dest = (doc.path.parent / path) if path else doc.path
        if frag and ds.role_of(dest) == role:
            out.add(frag)
    return out


def event_links(doc, text):
    """(resolved path, fragment) for every link in `text`."""
    out = set()
    for _, t in ipq.LINK.findall(text or ""):
        path, _, frag = t.partition("#")
        out.add(((doc.path.parent / path).resolve() if path else doc.path.resolve(), frag))
    return out


def evidence_key(ctx, doc, r):
    """The period of a qa row's earliest evidence, None if it has none, or a finding."""
    cell = field(r, "evidence")
    if ipq.plain(cell).strip().lower() in ipq.EMPTY:
        return None
    p, keys = ctx.period, []
    for link in event_links(doc, cell):
        ev = ctx.ds.evidence_doc(link[0])
        k = p.attribute(day=date(link[0].name), links={link}, label=ev.period_field() if ev else None)
        if isinstance(k, str):
            return f"{r.id}: {k}"
        if k is not None:
            keys.append(k)
    for d in DATE.findall(ipq.LINK.sub("", cell)):
        k = p.attribute(day=dt.date.fromisoformat(d))
        if isinstance(k, str):
            return f"{r.id}: {k}"
        keys.append(k)
    if not keys:
        return f"{r.id}: its evidence names no date, dated run record, or Period"
    return min(keys)


# ---------------------------------------------------------------- the blocks

def milestones_block(ctx):
    ms, unassigned = ipq.milestones(ctx.ds)
    if not ms:
        return None
    done, none, quiet = ctx.m("done"), ctx.m("none"), ctx.m("quiet")
    bar_w = 24

    def bar(n, total):
        if not total:
            return quiet * bar_w + "  none planned"
        k = round(bar_w * n / total)
        return done * k + none * (bar_w - k) + f"  {n}/{total}"

    counts = Counter(m["status"] for m in ms)
    lines = [fit(f"{plural(len(ms), 'milestone')} · " + " · ".join(
        f"{counts[s]} {s}" for s in ipq.STATUSES if counts[s]))]
    order = [m["id"] for m in ms]
    if len(ms) > 1 and all(m["depends"] == [order[i - 1]] for i, m in enumerate(ms) if i):
        lines += ["", fit(" ──▶ ".join(order))]
    lines.append("")
    title_w = min(28, max(len(m["title"]) for m in ms))
    fallback = []
    for m in ms:
        w = m["work"]
        total = sum(w.values())
        after = f"after {', '.join(m['depends'])}" if m["depends"] else ""
        lines.append(fit(f"{ipq.MARK.get(m['status'], '[?]')} {m['id']:<4} {fit(m['title'], title_w):<{title_w}}  "
                         f"{m['status']:<8} {m['target']:<10}  {after}".rstrip()))
        lines.append(f"         work    {bar(w['done'], total)}")
        lines.append(f"         checks  {bar(m['evidenced'], m['checks'])}")
        notes = []
        if m["blocked"]:
            notes.append(f"{len(m['blocked'])} blocked: {', '.join(m['blocked'])}")
        if m["deltas"]:
            notes.append(f"{plural(len(m['deltas']), 'open delta')}: {', '.join(m['deltas'])}")
        if m["out_of_scope"]:
            notes.append(f"{plural(len(m['out_of_scope']), 'check')} with evidence for another revision")
        if notes:
            lines.append(fit("         ! " + " · ".join(notes)))
        if m["revision"]:
            lines.append(fit(f"         judged at revision {m['revision']}"))
        lines.append("")
        work = f"{w['done']} of {total} backlog items done" if total else "no backlog items"
        checks = f"{m['evidenced']} of {m['checks']} checks with evidence" if m["checks"] else "no checks planned"
        if m["revision"]:
            checks += f" at revision {m['revision']}"
        fallback.append(f"{m['id']} {m['title']} ({m['status']}, {m['target']}): {work}, {checks}.")
    lines.append(f"[x] done  [>] active  [ ] planned  [-] cut   {done} done  {none} not yet")
    if unassigned:
        lines.append(f"{plural(unassigned, 'backlog item')} name no milestone")
    return Block("milestones", "Milestones: backlog items done and qa checks with evidence", lines,
                 " ".join(fallback),
                 measures="Work: the milestone's backlog items that are done, of all of them. Checks: its qa rows "
                          "that cite evidence, for its Revision when one is set, of all of them. Unweighted: "
                          "every item and every check counts one.")


def velocity_block(ctx):
    p = ctx.period
    findings, first, excluded = list(p.findings), Counter(), []
    for d in ctx.ds.docs:
        if d.role != "qa":
            continue
        for r in d.records:
            if r.form != "table":
                continue
            k = evidence_key(ctx, d, r)
            if isinstance(k, str):
                if "names no date" in k:
                    excluded.append(r.id)  # incomplete, not contradictory: draw the rest
                else:
                    findings.append(k)
            elif k is not None:
                first[k] += 1
    if findings:
        return findings
    if not first:
        return None
    unit, now = p.name, p.now(ctx.as_of)
    for k in first:
        if isinstance(p, Calendar) and p.label(k) in p.quiet:
            findings.append(f"{unit} {p.label(k)} is declared quiet ({p.quiet[p.label(k)]}) "
                            f"but {plural(first[k], 'check')} were first evidenced in it")
        if k > now:
            findings.append(f"{plural(first[k], 'check')} are evidenced in {unit} {p.label(k)}, after the as-of date")
    if findings:
        return findings
    keys = p.window(first, ctx.as_of)
    colw = max(3, max(len(p.label(k)) for k in keys) + 1)
    prefix = f"  {unit:<{max(7, len(unit))}} "
    fits = (WIDTH - len(prefix)) // colw  # one band, so the bars read as one chart
    earlier = 0
    if len(keys) > fits:
        earlier = sum(first[k] for k in keys[:-fits])
        keys = keys[-fits:]
    top = max(first[k] for k in keys) or 1
    scale = math.ceil(top / 8)
    levels = math.ceil(top / scale)
    done, quiet = ctx.m("done"), ctx.m("quiet")
    bars = [(" ", (lambda k, lv=lv: done if (first[k] + scale - 1) // scale >= lv else ""))
            for lv in range(levels, 0, -1)]

    def count(k):
        return quiet if p.is_quiet(k, first[k]) else str(first[k])

    rows = bars + [(f"  {unit}", p.label), ("  checks", count)]
    lines = columns(rows, keys, colw, prefix)
    caption = f"each {done} is " + ("one check" if scale == 1 else f"≈ {scale} checks")
    lines += ["", fit(f"{caption} first evidenced in that {unit}")]
    lines += [fit(f"{quiet} {c}") for c in p.quiet_captions(keys)]
    if earlier:
        lines.append(f"{plural(earlier, 'check')} first evidenced before {unit} {p.label(keys[0])}")
    total = sum(first.values())
    recent = "; ".join(f"{unit} {p.label(k)}: " + ("quiet" if p.is_quiet(k, first[k]) else str(first[k]))
                       for k in keys[-6:])
    return Block("velocity", f"QA checks first evidenced, by {unit} · as of {ctx.as_of}", lines,
                 f"{plural(total, 'check')} {'has' if total == 1 else 'have'} first evidence. "
                 f"Checks first evidenced, most recent {unit} last: {recent}.",
                 measures=f"Counts qa rows by the {unit} of their earliest cited evidence; a row counts once, so "
                          "rerunning a check adds nothing. Unweighted: every check counts one.",
                 excluded=excluded)


def open_deltas(ctx):
    return [(d, r) for d in ctx.ds.docs if d.role == "delta" and not d.supporting
            for r in d.records if r.form == "heading"]


def waits_on(ctx, r):
    v = ipq.plain(field(r, "Waits on")).strip().lower()
    return v if v in ("decision", "work", "external") else None


def waiting_block(ctx):
    ms, _ = ipq.milestones(ctx.ds)
    order = {m["id"]: i for i, m in enumerate(ms)}
    by_m, excluded = {}, []
    for _, r in open_deltas(ctx):
        blocks = [x for x in ipq.MILESTONE.findall(ipq.plain(field(r, "Blocks"))) if x in order]
        if blocks and not waits_on(ctx, r):
            excluded.append(r.id)
            continue
        for mid in blocks:
            by_m.setdefault(mid, []).append(r)
    if not by_m:
        return None
    mark = {"decision": ctx.m("decision"), "work": ctx.m("done"), "external": ctx.m("external")}
    kinds = ("decision", "work", "external")
    widest = max(len(v) for v in by_m.values())
    scale = math.ceil(widest / 30)
    lines, fallback = [], []
    for mid in sorted(by_m, key=lambda x: order[x]):
        c = Counter(waits_on(ctx, r) for r in by_m[mid])
        marks = "".join(mark[k] * math.ceil(c[k] / scale) for k in kinds)
        counts = " · ".join(f"{c[k]} {k}" for k in kinds if c[k])
        lines.append(fit(f"  {mid:<4} {marks:<{math.ceil(widest / scale) + 2}}{counts}"))
        who = {"decision": "a decision", "work": "work", "external": "someone outside the team"}
        fallback.append(f"{mid} is blocked by " + "; ".join(
            f"{', '.join(r.id for r in by_m[mid] if waits_on(ctx, r) == k)}, waiting on {who[k]}"
            for k in kinds if c[k]) + ".")
    lines += ["", f"{mark['decision']} a decision · {mark['work']} work · {mark['external']} someone outside the team"]
    if scale > 1:
        lines.append(f"each mark ≈ {scale} entries")
    return Block("waiting", "Open delta entries blocking each milestone, by who has to act", lines, " ".join(fallback),
                 measures="Open delta entries whose Blocks names the milestone, by their Waits on.",
                 excluded=excluded)


def trace_block(ctx):
    ds = ctx.ds
    reqs = [(d, r) for d in ds.docs if d.role == "prd" for r in d.records
            if r.form == "heading" and ipq.plain(field(r, "Status")).strip().lower() == "accepted"]
    if not reqs:
        return None
    linked = {role: set() for role in ("ux", "tdd", "backlog")}
    for d in ds.docs:
        if d.role in linked:
            linked[d.role] |= links_into(ds, d, "\n".join(d.clean), "prd")
    qa, evidenced = set(), set()
    for d in ds.docs:
        if d.role != "qa":
            continue
        for r in d.records:
            if r.form == "table":
                got = links_into(ds, d, field(r, "verifies"), "prd")
                qa |= got
                if ipq.plain(field(r, "evidence")).strip().lower() not in ipq.EMPTY:
                    evidenced |= got
    cols = [("ux", linked["ux"]), ("tdd", linked["tdd"]), ("backlog", linked["backlog"]),
            ("qa", qa), ("evidence", evidenced)]
    done, none, na = ctx.m("done"), ctx.m("none"), ctx.m("na")
    gaps = []
    for _, r in reqs:
        skip = set(re.findall(r"\bno (ux|tdd|backlog|qa|evidence)\b", ipq.plain(field(r, "Trace")).lower()))
        cells = [(name, na if name in skip else done if r.id.lower() in have else none) for name, have in cols]
        if any(c == none for _, c in cells):
            gaps.append((r.id, cells))
    full = len(reqs) - len(gaps)
    lines = [f"{full} of {plural(len(reqs), 'accepted requirement')} fully traced"]
    if gaps:
        idw = max(len(i) for i, _ in gaps) + 2
        lines += ["", " " * (idw + 2) + "".join(f"{n:<9}" for n, _ in cols).rstrip()]
        for rid, cells in gaps:
            lines.append((f"  {rid:<{idw}}" + "".join(f"{c:<9}" for _, c in cells)).rstrip())
        lines += ["", f"{done} linked · {none} missing · {na} not required (the requirement's Trace field)"]
    fallback = (f"All {len(reqs)} accepted requirements are fully traced." if not gaps else
                f"{full} of {len(reqs)} accepted requirements are fully traced. " + " ".join(
                    f"{rid} lacks {', '.join(n for n, c in cells if c == none)}." for rid, cells in gaps))
    return Block("trace", "Accepted requirements traced through ux, tdd, backlog, qa, and evidence", lines, fallback,
                 measures="Linked means a document of that kind links the requirement, not that it is correct. "
                          "Evidence means a qa row verifying it cites evidence. Accepted requirements only.")


def evidence_block(ctx):
    ms, _ = ipq.milestones(ctx.ds)
    order = [m["id"] for m in ms]
    cells, unplaced = {}, 0
    for d in ctx.ds.docs:
        if d.role != "qa":
            continue
        for r in d.records:
            if r.form != "table":
                continue
            mid = next((x for x in ipq.MILESTONE.findall(ipq.plain(field(r, "milestone"))) if x in order), None)
            if not mid:
                unplaced += 1
                continue
            parts = r.id.split("-")
            cls = parts[1] if len(parts) >= 3 else "-"
            revision = next(m["revision"] for m in ms if m["id"] == mid)
            ev = ipq.evidence_scope(ctx.ds, d, r, revision)[1]
            c = cells.setdefault((cls, mid), [0, 0])
            c[0] += ev
            c[1] += 1
    if not cells:
        return None
    classes = sorted({c for c, _ in cells})
    mids = [m for m in order if any(k[1] == m for k in cells)]
    labw = max(7, max(len(c) for c in classes) + 4)
    e_all = sum(v[0] for v in cells.values())
    t_all = sum(v[1] for v in cells.values())
    room = WIDTH - labw - max(8, len(f"{e_all}/{t_all}"))
    widest = {m: max(cells.get((c, m), [0, 0])[1] for c in classes) for m in mids}

    def total(m):
        e, t = map(sum, zip(*[cells.get((c, m), [0, 0]) for c in classes]))
        return f"{e}/{t}"

    minimum = {m: max(len(m), len(total(m)), 3) + 2 for m in mids}
    if any(w > room for w in minimum.values()):
        return ["class labels, milestone IDs, or counts leave too little room for an evidence column"]

    def widths(scale):
        return {m: max(math.ceil(widest[m] / scale) + 2, minimum[m]) for m in mids}

    # Scale into one band when possible. Otherwise fit individual columns and
    # wrap them into bands: labels and exact counts cannot shrink with scale.
    single_band = sum(minimum.values()) <= room
    scale = 1
    while (sum(widths(scale).values()) if single_band else max(widths(scale).values())) > room:
        scale += 1
    done, none = ctx.m("done"), ctx.m("none")

    def cell(c, m):
        e, t = cells.get((c, m), [0, 0])
        if not t:
            return ""
        marks_e = math.ceil(e / scale) if e else 0
        marks_t = max(math.ceil(t / scale), marks_e)
        return done * marks_e + none * (marks_t - marks_e)

    colw = widths(scale)
    bands, band, used = [], [], 0
    for m in mids:
        if used + colw[m] > room:
            bands.append(band)
            band, used = [], 0
        band.append(m)
        used += colw[m]
    bands.append(band)
    lines = []
    for band in bands:
        if lines:
            lines.append("")
        lines.append(" " * labw + "".join(f"{m:<{colw[m]}}" for m in band) + "total")
        for c in classes:
            e = sum(cells.get((c, m), [0, 0])[0] for m in band)
            t = sum(cells.get((c, m), [0, 0])[1] for m in band)
            lines.append(f"  {c:<{labw - 2}}" + "".join(f"{cell(c, m):<{colw[m]}}" for m in band) + f"{e}/{t}")
        e = sum(cells.get((c, m), [0, 0])[0] for c in classes for m in band)
        t = sum(cells.get((c, m), [0, 0])[1] for c in classes for m in band)
        lines.append(f"  {'total':<{labw - 2}}" + "".join(f"{total(m):<{colw[m]}}" for m in band) + f"{e}/{t}")
    if len(bands) > 1:
        lines += ["", f"Totals within each band; all milestones: {e_all}/{t_all}"]
    lines += ["", f"{done} evidenced · {none} none yet · one mark per check" if scale == 1
              else f"{done} evidenced · {none} none yet · each mark ≈ {scale} checks"]
    if unplaced:
        lines.append(f"{plural(unplaced, 'check')} name no milestone")
    fallback = " ".join(
        f"{m}: " + ", ".join(f"{c} {cells[(c, m)][0]} of {cells[(c, m)][1]}" for c in classes if (c, m) in cells) + "."
        for m in mids)
    return Block("evidence", "QA checks with evidence, by class and milestone", lines, fallback,
                 measures="Qa rows by the class in their ID and their milestone. Evidenced means evidence is cited, "
                          "for the milestone's Revision when one is set. Unweighted.")


def closed_dates(r):
    text = ipq.plain(r.text)
    f = re.search(r"\bfound (\d{4}-\d{2}-\d{2})", text)
    c = re.search(r"\bclosed (\d{4}-\d{2}-\d{2})", text)
    return (dt.date.fromisoformat(f.group(1)) if f else None, dt.date.fromisoformat(c.group(1)) if c else None)


def flow_block(ctx):
    p = ctx.flow_period
    events, findings, excluded = [], list(p.findings), []

    def key(day, doc, text, what, rid):
        k = p.attribute(day=day, links=event_links(doc, text))
        if isinstance(k, str):
            findings.append(f"{rid} {what}: {k}")
        return k

    for d in ctx.ds.docs:
        if d.role != "delta" or d.supporting:
            continue
        for r in d.records:
            if r.form == "heading":
                found = field(r, "Found")
                f = date(ipq.plain(found))
                if not f:
                    excluded.append(r.id)
                    continue
                events.append((key(f, d, found, "found", r.id), None))
            elif r.form == "condensed":
                f, c = closed_dates(r)
                if not (f and c):
                    excluded.append(r.id)
                elif c < f:
                    findings.append(f"{r.id}: closed {c} is before found {f}")
                else:
                    # A link from a Closed line to an iteration dates the close, never the find.
                    events.append((key(f, d, "", "found", r.id), key(c, d, r.text, "closed", r.id)))
    if findings:
        return findings
    if not events:
        return None
    unit = p.name
    opened = Counter(o for o, _ in events)
    closed = Counter(c for _, c in events if c is not None)
    keys = p.window(list(opened) + list(closed), ctx.as_of)
    colw = max(4, max(len(p.label(k)) for k in keys[-12:]) + 1)
    keys = keys[-min(12, (WIDTH - len("  open at end ")) // colw):]

    def live(k):
        return sum(v for kk, v in opened.items() if kk <= k) - sum(v for kk, v in closed.items() if kk <= k)

    rows = [(f"  {unit}", p.label), ("  opened", lambda k: str(opened[k])),
            ("  closed", lambda k: str(closed[k])), ("  open at end", lambda k: str(live(k)))]
    lines = columns(rows, keys, colw, "  open at end ")
    last = keys[-1]
    return Block("flow", f"Delta entries opened and closed, by {unit} · as of {ctx.as_of}", lines,
                 f"{plural(live(last), 'entry', 'entries')} open at the end of {unit} {p.label(last)}. "
                 f"In that {unit}: {opened[last]} opened, {closed[last]} closed.",
                 measures=f"Entries by the {unit} of their Found date and of their close; open at end is the "
                          "running difference. Counts entries, not their size or severity.",
                 excluded=excluded)


def awaiting_block(ctx):
    waiting, findings, excluded = [], [], []
    for _, r in open_deltas(ctx):
        if waits_on(ctx, r) != "decision":
            continue
        f = date(ipq.plain(field(r, "Found")))
        if not f:
            excluded.append(r.id)
            continue
        age = (ctx.as_of - f).days
        if age < 0:
            findings.append(f"{r.id}: found {f}, after the as-of date")
            continue
        waiting.append((r.id, age, ipq.plain(field(r, "Decides")).strip()))
    if findings:
        return findings
    if not waiting:
        return None
    buckets = [("0-2", 0, 2), ("3-7", 3, 7), ("8-14", 8, 14), ("15+", 15, 10 ** 6)]
    mark = ctx.m("decision")
    counts = [sum(1 for _, a, _ in waiting if lo <= a <= hi) for _, lo, hi in buckets]
    scale = math.ceil(max(counts) / 40) or 1
    lines = [f"  {name:<6} {(mark * math.ceil(n / scale)) or ctx.m('quiet'):<{math.ceil(max(counts) / scale) + 2}}{n}"
             for (name, _, _), n in zip(buckets, counts)]
    lines += ["", f"{mark} one open entry that waits on a decision" if scale == 1 else f"each {mark} ≈ {scale} entries",
              "days counted from each entry's Found date"]
    return Block("awaiting", f"Delta entries waiting on a decision, by days open · as of {ctx.as_of}", lines,
                 f"{plural(len(waiting), 'entry', 'entries')} {'waits' if len(waiting) == 1 else 'wait'} on a decision: " +
                 ", ".join(f"{i} ({plural(a, 'day')}" + (f", decided by {who}" if who else ", no one named to decide") + ")"
                           for i, a, who in sorted(waiting, key=lambda x: -x[1])) + ".",
                 measures="Open delta entries whose Waits on is decision, by whole days since their Found date.",
                 excluded=excluded)


DECISION_ORDER = ["accepted", "proposed", "rejected", "superseded"]


def decisions_block(ctx, role):
    recs = [r for d in ctx.ds.docs if d.role == role for r in d.records
            if r.form == "heading" and r.section == "Decision records"
            or (r.form == "heading" and d.supporting and re.match(r"^(ADR|DEC)-", r.id))]
    if not recs:
        return None
    mark = {"accepted": ctx.m("done"), "proposed": ctx.m("none"), "rejected": ctx.m("na"),
            "superseded": ctx.m("superseded")}
    c = Counter(ipq.plain(field(r, "Status")).strip().lower() or "unset" for r in recs)
    statuses = [s for s in DECISION_ORDER if c[s]] + sorted(s for s in c if s not in DECISION_ORDER)
    strip = "".join(mark.get(s, ctx.m("other")) * c[s] for s in statuses)
    per = 60
    lines = [f"  {strip[i:i + per]}" for i in range(0, len(strip), per)]
    lines += ["", fit("  " + " · ".join(f"{mark.get(s, ctx.m('other'))} {s} {c[s]}" for s in statuses))]
    return Block("decisions", "Decision records by status", lines,
                 f"{plural(len(recs), 'decision record')}: " + ", ".join(f"{c[s]} {s}" for s in statuses) + ".",
                 measures="Every decision record in this document, by its Status.")


def screen_states(r):
    """{state: True if specified, False if not applicable} from a screen's States field."""
    out = {}
    for tok in ipq.plain(field(r, "States")).split(","):
        tok = tok.strip().lower()
        if tok:
            na = bool(re.search(r"\bn/?a$", tok))
            out[re.sub(r"\s*\bn/?a$", "", tok).strip()] = not na
    return out


def states_block(ctx):
    screens = [r for d in ctx.ds.docs if d.role == "ux" for r in d.records
               if r.form == "heading" and r.id.startswith("SCR-")]
    if not screens:
        return None
    states = [s.lower() for s in ctx.cfg.get("ux_states", ["default", "empty", "loading", "error", "offline"])]
    done, none, na = ctx.m("done"), ctx.m("none"), ctx.m("na")
    labw = min(22, max(len(f"{r.id} {r.title}") for r in screens)) + 4
    colw = max(len(s) for s in states) + 1
    lines = [" " * labw + "".join(f"{s:<{colw}}" for s in states).rstrip()]
    fallback = []
    for r in screens:
        have = screen_states(r)
        cells = [done if have.get(s) else na if have.get(s) is False else none for s in states]
        lines.append((f"  {fit(f'{r.id} {r.title}', labw - 2):<{labw - 2}}" +
                      "".join(f"{c:<{colw}}" for c in cells)).rstrip())
        missing = [s for s, c in zip(states, cells) if c == none]
        if missing:
            fallback.append(f"{r.id} lacks {', '.join(missing)}.")
    lines += ["", f"{done} specified · {none} missing · {na} not applicable"]
    return Block("states", "Screen states specified", lines,
                 " ".join(fallback) or f"Every screen specifies every state in {', '.join(states)}.",
                 measures="Specified means the screen's States field lists the state and its body describes it; "
                          "nobody has reviewed the design by this measure.")


BUILDERS = {
    "milestones": milestones_block, "velocity": velocity_block, "waiting": waiting_block,
    "trace": trace_block, "evidence": evidence_block, "flow": flow_block,
    "awaiting": awaiting_block, "states": states_block,
}


# ---------------------------------------------------------------- the section

def blocks_for(ds, role):
    names = list(ds.cfg.get("visuals", {}).get(role, BLOCKS_BY_ROLE.get(role, [])))
    doc = ds.files.get(role)
    for key in ds.cfg.get("generated", {}):
        f, _, name = key.partition("#")
        if f == doc and name not in names:
            names.append(name)
    return names


def render_glance(ds, role, as_of):
    """The At a glance body for `role`, and findings that stop it being drawn."""
    try:
        ctx = Ctx(ds, as_of)
    except (ValueError, TypeError) as e:
        return "\n" + "Nothing to show yet." + "\n", [f"ipq.json period: {e}"]
    parts, findings = [], []
    custom = ds.cfg.get("generated", {})
    for name in blocks_for(ds, role):
        cmd = custom.get(f"{ds.files[role]}#{name}")
        if cmd:
            ok, out = ipq.run_command(cmd, ds.root)
            if ok:
                parts.append(out.strip())
            else:
                findings.append(f"{name}: `{cmd}` failed: {out.strip().splitlines()[-1] if out.strip() else 'no output'}")
            continue
        if name == "decisions":
            got = decisions_block(ctx, role)
        elif name in BUILDERS:
            got = BUILDERS[name](ctx)
        else:
            findings.append(f"{name}: no such block; blocks are {', '.join(sorted(BUILDERS) + ['decisions'])}")
            continue
        if isinstance(got, list):
            findings += [f"{name}: {f}" for f in got]
        elif got is not None:
            parts.append(got.render())
    head = (f"<!-- Generated by `ipq.py fix` as of {as_of} from the records in this set. "
            "Edit the records, not this. -->")
    body = "\n\n".join([head] + (parts or ["Nothing to show yet."]))
    return "\n" + body + "\n", findings


def stamp_of(body):
    m = STAMP.search(body or "")
    return dt.date.fromisoformat(m.group(1)) if m else None


def size_block(ds):
    budget = ds.budgets["doc_lines"]
    docs = sorted(((len(d.raw), d) for d in ds.docs), key=lambda x: -x[0])
    if not docs:
        return None
    step = max(1, budget // 10)
    namew = max(len(str(d.path.relative_to(ds.root))) for _, d in docs) + 2
    room = WIDTH - namew - 12
    scale = 1
    while math.ceil(docs[0][0] / (step * scale)) + 1 > room:
        scale += 1
    unit = step * scale
    mark, edge = MARKS["done"], MARKS["budget"]
    cut = math.ceil(budget / unit)
    lines = []
    for n, d in docs:
        k = max(1, round(n / unit)) if n else 0
        bar = mark * k
        bar = (bar[:cut] + edge + bar[cut:]) if k > cut else bar.ljust(cut) + edge
        lines.append(f"  {str(d.path.relative_to(ds.root)):<{namew}}{bar:<{room + 1}} {n:>6,}".rstrip())
    return Block("sizes", f"Lines per document against the budget of {budget:,}",
                 lines + ["", f"each {mark} ≈ {unit:,} lines · {edge} the budget"],
                 " ".join(f"{d.path.name}: {n:,} lines." for n, d in docs if n > budget)
                 or "Every document is within the budget.")
