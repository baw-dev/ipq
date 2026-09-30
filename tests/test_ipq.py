"""Tests for skill/tools/ipq.py and ipq_visuals.py. Run: python3 -m unittest discover tests"""
import contextlib
import datetime as dt
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "skill" / "tools"))
import ipq  # noqa: E402
import ipq_visuals as visuals  # noqa: E402

ACME = REPO / "tests" / "fixtures" / "acme" / "docs"
EXAMPLE = REPO / "examples" / "jinkieslist" / "docs"  # the fuller set the README quotes
STAMP = dt.date(2026, 9, 29)  # the as-of date the fixture's At a glance sections carry


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ipq.main([str(a) for a in argv])
    return code, out.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.docs = self.tmp / "docs"
        shutil.copytree(ACME, self.docs)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, name, old, new):
        p = self.docs / name
        text = p.read_text()
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1))

    def config(self, **cfg):
        (self.docs / "ipq.json").write_text(json.dumps(cfg))

    def findings(self):
        report = ipq.Report(ipq.DocSet(self.docs))
        ipq.check(ipq.DocSet(self.docs), report)
        return report.items

    def rules(self):
        return {(level, rule) for level, _, _, rule, _ in self.findings()}

    def fix(self, today=STAMP):
        return ipq.fix(self.docs, today)

    def glance(self, role, today=STAMP):
        return visuals.render_glance(ipq.DocSet(self.docs), role, today)

    def blocks(self, role, today=STAMP):
        body, findings = self.glance(role, today)
        self.assertEqual(findings, [])
        return re.findall(r"```text\n(.*?)```\n\n([^\n]+)", body, re.S)


class Conforming(Base):
    def test_fixture_is_clean(self):
        code, out = run("check", ACME)
        self.assertEqual(code, 0, out)
        self.assertIn("0 errors, 0 warnings", out)

    def test_example_is_clean(self):
        code, out = run("check", EXAMPLE)
        self.assertEqual(code, 0, out)
        self.assertIn("0 errors, 0 warnings", out)

    def test_quoted_blocks_match_the_example(self):
        """Every chart the README and VISUALS.md quote is an in-order excerpt of a block the tool
        generated for JinkiesList, so a layout change cannot leave a stale quote behind. The
        size chart comes from `check --advice`, not a document, and is marked illustrative."""
        fence = re.compile(r"```text\n(.*?)```", re.S)
        title = lambda block: block.splitlines()[0].split(" · as of")[0]
        generated = {}  # several documents can carry a block with the same title
        for path in sorted(EXAMPLE.rglob("*.md")):
            for block in fence.findall(path.read_text(encoding="utf-8")):
                generated.setdefault(title(block), []).append(block.rstrip("\n").splitlines())

        def excerpt(quote, block):
            lines = iter(block)
            return [l for l in quote if not any(l == g for g in lines)]
        for name in ("README.md", "VISUALS.md"):
            for block in fence.findall((REPO / name).read_text(encoding="utf-8")):
                if title(block).startswith("Lines per document"):
                    continue  # illustrative: check --advice output, not embedded in a document
                with self.subTest(document=name, block=title(block)):
                    self.assertIn(title(block), generated, "no generated block with this title")
                    quote = block.rstrip("\n").splitlines()
                    misses = [excerpt(quote, g) for g in generated[title(block)]]
                    self.assertIn([], misses, f"quoted lines not in any generated block, in order: {min(misses, key=len)}")

    def test_versions_agree(self):
        """A release changes __version__, opens CHANGES.md with it under its permanent anchor,
        and names its major and minor in SKILL.md; the example pins the same major and minor."""
        v = ipq.__version__
        changes = (REPO / "CHANGES.md").read_text(encoding="utf-8")
        first = re.search(r'^<a id="v(\d+\.\d+\.\d+)"></a>\n## (\d+\.\d+\.\d+):', changes, re.M)
        assert first is not None, "CHANGES.md needs an anchored entry: <a id=\"vX.Y.Z\"></a> then ## X.Y.Z:"
        self.assertEqual(first.group(1), v)
        self.assertEqual(first.group(2), v)
        major_minor = ".".join(v.split(".")[:2])
        skill = (REPO / "skill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(f"IPQ {major_minor}.", skill)
        pin = json.loads((EXAMPLE / "ipq.json").read_text(encoding="utf-8"))["ipq"]
        self.assertEqual(pin, major_minor)

    def test_init_is_clean(self):
        fresh = self.tmp / "fresh"
        run("init", fresh, "--product", "Fresh")
        code, out = run("check", fresh)
        self.assertEqual(code, 0, out)
        self.assertNotIn("{{", "".join(p.read_text() for p in fresh.glob("*.md")))

    def test_init_never_overwrites(self):
        before = (self.docs / "prd.md").read_text()
        run("init", self.docs, "--product", "Other")
        self.assertEqual((self.docs / "prd.md").read_text(), before)

    def test_fix_is_idempotent(self):
        before = {p.name: p.read_text() for p in self.docs.glob("*.md")}
        changed, problems = self.fix()
        self.assertEqual((changed, problems), ([], []))
        self.assertEqual(before, {p.name: p.read_text() for p in self.docs.glob("*.md")})

    def test_check_is_stable_across_days(self):
        # check redraws with the stamped date, so a passing day alone never makes a block stale
        self.assertNotIn(("error", "generated"), self.rules())

    def test_version(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()) as out:
            ipq.main(["--version"])
        self.assertIn(ipq.__version__, out.getvalue())
        self.config(ipq="0.9")  # any major.minor other than the tool's
        self.assertIn(("warning", "version"), self.rules())


class Setup(Base):
    """The paths a new user takes: install into a project, start fresh, migrate."""

    def test_install_into_a_project(self):
        import subprocess
        repo = self.tmp / "repo"
        repo.mkdir()
        out = subprocess.run(["sh", str(REPO / "install.sh"), "--project", str(repo)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        tool = repo / ".claude" / "skills" / "ipq" / "tools" / "ipq.py"
        self.assertTrue(tool.exists())
        subprocess.run([sys.executable, str(tool), "init", str(repo / "docs"), "--product", "Repo"], capture_output=True)
        run_check = subprocess.run([sys.executable, str(tool), "check", str(repo / "docs")], capture_output=True, text=True)
        self.assertEqual(run_check.returncode, 0, run_check.stdout)
        self.assertFalse(list((repo / ".claude").rglob("__pycache__")))
        again = subprocess.run(["sh", str(REPO / "install.sh"), "--check", "--project", str(repo)], capture_output=True, text=True)
        self.assertEqual(again.returncode, 0, again.stdout)

    def test_init_uses_the_projects_filenames(self):
        fresh = self.tmp / "mapped"
        fresh.mkdir()
        (fresh / "ipq.json").write_text(json.dumps({"files": {"prd": "requirements.md"}}))
        (fresh / "requirements.md").write_text("# Old requirements\n")
        run("init", fresh, "--product", "Mapped")
        self.assertFalse((fresh / "prd.md").exists())
        self.assertIn("](requirements.md", (fresh / "roadmap.md").read_text())
        self.assertNotIn("](prd.md", (fresh / "roadmap.md").read_text())

    def test_skeleton_prints_every_section(self):
        _, out = run("skeleton", "roadmap", self.docs, "--product", "Acme")
        self.assertIn("# Acme — Roadmap", out)
        self.assertIn("## Iterations", out)
        self.assertNotIn("ipq:", out)

    def test_anchors_cover_unmapped_files(self):
        (self.docs / "notes.md").write_text('# Notes\n\n<a id="old-decision"></a>\nWe chose Postgres.\n')
        _, out = run("anchors", self.docs)
        self.assertIn("notes.md#old-decision", out)
        (self.docs / "tdd").mkdir()
        (self.docs / "notes.md").rename(self.docs / "tdd" / "notes.md")
        listing = self.tmp / "anchors.txt"
        listing.write_text(out)
        report = ipq.Report(ipq.DocSet(self.docs))
        ipq.check(ipq.DocSet(self.docs), report, listing)
        moved = [m for _, _, _, rule, m in report.items if rule == "kept-anchor"]
        self.assertTrue(moved and "tdd/notes.md" in moved[0], moved)

    def test_missing_sections_are_one_finding(self):
        self.edit("prd.md", "## Users", "## Userz")
        self.edit("prd.md", "## Scope", "## Scopez")
        msgs = [m for _, _, _, rule, m in self.findings() if rule == "sections" and m.startswith("missing")]
        self.assertEqual(msgs, ["missing required sections: Users, Scope"])


class Accuracy(Base):
    """The critique's adversarial cases, and the checks that answer them."""

    def run_record(self, name, revision=None):
        runs = self.docs / "qa" / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        (runs / name).write_text("# Run\n\n" + (f"- **Revision:** {revision}\n" if revision else ""))

    def test_a_passing_test_for_the_wrong_revision(self):
        self.run_record("2026-09-24-import.md", revision="1.3.0")
        self.edit("qa.md", "| 2026-09-24 run |", "| [run](qa/runs/2026-09-24-import.md) |")
        self.edit("roadmap.md", "- **Target:** 2026-11-30\n", "- **Target:** 2026-11-30\n- **Revision:** 1.4.0\n")
        warnings = [m for level, _, _, rule, m in self.findings() if rule == "evidence-scope"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("evidence is for 1.3.0; M1 is judged at revision 1.4.0", warnings[0])
        m1 = ipq.milestones(ipq.DocSet(self.docs))[0][0]
        self.assertEqual((m1["evidenced"], m1["checks"]), (0, 2))  # not counted
        self.run_record("2026-09-24-import.md", revision="1.4.0")
        self.assertEqual(ipq.milestones(ipq.DocSet(self.docs))[0][0]["evidenced"], 1)

    def test_complete_links_with_obsolete_evidence(self):
        report = ipq.Report(ipq.DocSet(self.docs))
        ipq.check(ipq.DocSet(self.docs), report, fresh=dt.date(2027, 3, 1))
        stale = [m for level, _, _, rule, m in report.items if rule == "stale"]
        self.assertTrue(any("QA-CORE-01: its newest evidence is" in m for m in stale), stale)
        self.assertTrue(any("At a glance was drawn" in m for m in stale))
        self.assertEqual(report.count("error"), 0)  # freshness warns; it never fails conformance

    def test_an_unresolved_conflict_with_no_decider(self):
        self.edit("delta.md", "- **Decides:** product\n", "")
        self.assertIn(("warning", "decider"), self.rules())
        self.edit("delta.md", "- **Found:** 2026-09-14\n", "- **Found:** 2026-09-14\n- **Escalate by:** 2026-09-20\n")
        report = ipq.Report(ipq.DocSet(self.docs))
        ipq.check(ipq.DocSet(self.docs), report, fresh=STAMP)
        self.assertTrue(any("past its escalation date" in m for _, _, _, _, m in report.items))

    def test_freshness_is_off_unless_asked(self):
        self.assertNotIn(("warning", "stale"), self.rules())

    def test_delta_freshness_without_at_a_glance(self):
        run("template", "delta", self.docs)
        for path in (self.docs / ".ipq" / "templates" / "delta.md", self.docs / "delta.md"):
            path.write_text(re.sub(r"^## At a glance\n.*?(?=^## )", "", path.read_text(), flags=re.M | re.S))
        self.fix()
        code, out = run("check", self.docs, "--fresh", "2026-11-01")
        self.assertEqual(code, 0, out)
        self.assertIn("D-001 has been open 48 days", out)
        self.edit("delta.md", "- **Found:** 2026-09-14", "- **Found:** 2026-09-14\n- **Escalate by:** 2026-09-20")
        code, out = run("check", self.docs, "--fresh", "2026-11-01")
        self.assertEqual(code, 0, out)
        self.assertIn("D-001 is past its escalation date, 2026-09-20", out)


class Schema(Base):
    def test_an_adapted_template_behind_upstream_warns(self):
        run("template", "prd", self.docs)
        p = self.docs / ".ipq" / "templates" / "prd.md"
        p.write_text(p.read_text().replace('<!-- ipq:schema version="2" -->\n', ""))
        self.assertIn(("warning", "schema"), self.rules())

    def test_at_a_glance_is_not_in_the_floor(self):
        run("template", "prd", self.docs)
        p = self.docs / ".ipq" / "templates" / "prd.md"
        p.write_text(p.read_text().replace("## At a glance\n<!-- ipq:generated -->\n", ""))
        self.edit("prd.md", "## At a glance\n", "## Glance gone\n")
        self.edit("prd.md", "## Glance gone\n", "")
        self.fix()
        self.assertNotIn(("error", "template"), self.rules())
        self.assertNotIn(("error", "sections"), self.rules())


class Context(Base):
    def test_a_moved_anchor_reports_its_new_governing_heading(self):
        listing = self.tmp / "anchors.txt"
        listing.write_text(run("anchors", self.docs)[1])
        self.assertIn("tdd.md#t-store\tComponents › T-STORE — Ledger store", listing.read_text())
        self.edit("tdd.md", '<a id="t-store"></a>\n### T-STORE — Ledger store', '### T-STORE-X — Ledger store')
        self.edit("tdd.md", "## Decision records\n", '## Decision records\n\n<a id="t-store"></a>\nThe store.\n')
        report = ipq.Report(ipq.DocSet(self.docs))
        ipq.check(ipq.DocSet(self.docs), report, listing)
        msgs = [m for _, _, _, rule, m in report.items if rule == "context"]
        self.assertTrue(msgs and "now under 'Decision records'" in msgs[0], msgs)

    def test_links_to(self):
        _, out = run("links-to", "prd.md#r-core-02", self.docs)
        self.assertIn("backlog.md:", out)
        self.assertIn("qa.md:", out)


class Violations(Base):
    def test_unknown_section(self):
        self.edit("prd.md", "## Scope", "## Sprint notes\n\nx\n\n## Scope")
        self.assertIn(("error", "sections"), self.rules())

    def test_missing_section(self):
        self.edit("prd.md", "## Users", "## Userz")
        self.assertIn(("error", "sections"), self.rules())

    def test_missing_anchor(self):
        self.edit("tdd.md", '<a id="t-store"></a>\n', "")
        self.assertIn(("error", "anchor"), self.rules())

    def test_broken_link(self):
        self.edit("backlog.md", "(tdd.md#t-ingest)", "(tdd.md#t-nowhere)")
        self.assertIn(("error", "link"), self.rules())

    def test_bad_enum(self):
        self.edit("roadmap.md", "- **Status:** active", "- **Status:** in flight")
        self.assertIn(("error", "fields"), self.rules())

    def test_trace_link_goes_to_owner(self):
        self.edit("backlog.md", "- **Requirement:** [R-CORE-02](prd.md#r-core-02)",
                  "- **Requirement:** [T-INGEST](tdd.md#t-ingest)")
        self.assertIn(("error", "trace"), self.rules())

    def test_long_summary_is_still_an_error(self):
        self.edit("prd.md", "## Contents", "word " * 160 + "\n\n## Contents")
        self.assertIn(("error", "summary"), self.rules())

    def test_full_record_in_history_section(self):
        self.edit("backlog.md", '- <a id="b-001"></a>**B-001** Set up the ledger store — [R-CORE-01](prd.md#r-core-01) · [M1](roadmap.md#m1) · done 2026-09-18',
                  '<a id="b-001"></a>\n### B-001 — Set up the ledger store\n\n- **Milestone:** [M1](roadmap.md#m1)')
        self.assertIn(("error", "placement"), self.rules())

    def test_condensed_line_needs_its_date(self):
        self.edit("backlog.md", " · done 2026-09-18", "")
        self.assertIn(("error", "dates"), self.rules())

    def test_duplicate_id(self):
        self.edit("tdd.md", '<a id="t-store"></a>\n### T-STORE', '<a id="t-ingest"></a>\n### T-INGEST')
        rules = self.rules()
        self.assertIn(("error", "duplicate"), rules)
        self.assertIn(("error", "anchor"), rules)

    def test_stale_generated_sections(self):
        self.edit("backlog.md", "## Next\n", "## Next\n\n### A new subsection\n")
        self.edit("qa.md", "| none |", "| 2026-09-25 run |")
        self.assertIn(("error", "generated"), self.rules())
        self.fix()
        self.assertNotIn(("error", "generated"), self.rules())

    def test_placeholder(self):
        self.edit("ux.md", "TBD.", "{{screens}}")
        self.assertIn(("error", "placeholder"), self.rules())

    def test_placeholder_braces_inside_code_are_not_placeholders(self):
        self.edit("ux.md", "TBD.", "The literal `[]Boundary{{…}}` and ``a`{{b}}`` are code, not placeholders.")
        self.assertNotIn(("error", "placeholder"), self.rules())

    def test_placeholder_outside_code_on_a_line_with_code_still_fails(self):
        self.edit("ux.md", "TBD.", "See `x` and {{screens}}.")
        self.assertIn(("error", "placeholder"), self.rules())


class Advice(Base):
    def test_sizes_are_advice_and_hidden(self):
        self.edit("tdd.md", "The ingest component", "word " * 130 + "\n\nThe ingest component")
        levels = {(level, rule) for level, _, _, rule, _ in self.findings() if rule == "paragraph"}
        self.assertEqual(levels, {("advice", "paragraph")})
        code, out = run("check", self.docs)
        self.assertEqual(code, 0, out)
        self.assertNotIn("[paragraph]", out)
        self.assertIn("1 advice (show with --advice)", out)
        _, out = run("check", self.docs, "--advice")
        self.assertIn("Lines per document against the budget", out)
        self.assertIn("tdd.md: advice — 1 long paragraph", out)
        _, out = run("check", self.docs, "--advice=all")
        self.assertIn("advice [paragraph]", out)


class Templates(Base):
    def adapt(self, role, old, new):
        run("template", role, self.docs)
        p = self.docs / ".ipq" / "templates" / f"{role}.md"
        text = p.read_text()
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1))

    def test_adapted_template_adds_a_section_and_a_field(self):
        self.adapt("backlog", "## Blocked\n", "## Readiness track\n<!-- ipq:optional -->\n\n## Blocked\n")
        self.adapt("backlog", "Blocked by; Done when*", "Blocked by; Track; Done when*")
        self.edit("backlog.md", "## Blocked", "## Readiness track\n\nWork that makes M2 possible.\n\n## Blocked")
        self.edit("backlog.md", "- **Blocked by:**", "- **Track:** readiness\n- **Blocked by:**")
        self.fix()
        rules = self.rules()
        self.assertIn(("warning", "adapted"), rules)
        self.assertFalse({r for r in rules if r[0] == "error"}, self.findings())
        self.assertNotIn(("warning", "fields"), rules)

    def test_adapted_template_cannot_drop_the_floor(self):
        self.adapt("prd", "## Summary\n", "## Overview\n")
        self.assertIn(("error", "template"), self.rules())

    def test_adapted_template_cannot_drop_a_required_field(self):
        self.adapt("backlog", "Requirement*@prd; ", "")
        self.assertIn(("error", "template"), self.rules())

    def test_adapted_template_may_make_a_required_field_optional_with_a_warning(self):
        self.adapt("backlog", "Requirement*@prd", "Requirement@prd")
        path = self.docs / "backlog.md"
        path.write_text(re.sub(r"^- \*\*Requirement:\*\*.*\n", "", path.read_text(), flags=re.M))
        run("fix", self.docs)  # the trace block changes once the links are gone
        code, out = run("check", self.docs)
        self.assertEqual(code, 0, out)
        self.assertNotIn("error [template]", out)
        self.assertIn("warning [relaxed]", out)
        self.assertIn("make Requirement optional", out)


class Extensions(Base):
    def test_custom_generated_block(self):
        script = self.tmp / "velocity.py"
        script.write_text("print('```text\\nOur own velocity\\n```')\n")
        self.config(generated={"roadmap.md#velocity": f"{sys.executable} {script}"})
        self.fix()
        self.assertIn("Our own velocity", (self.docs / "roadmap.md").read_text())
        self.assertNotIn(("error", "generated"), self.rules())
        script.write_text("print('```text\\nOur new velocity\\n```')\n")
        self.assertIn(("error", "generated"), self.rules())

    def test_failing_custom_block_keeps_the_old_one(self):
        self.config(generated={"roadmap.md#velocity": f"{sys.executable} -c 'raise SystemExit(3)'"})
        before = (self.docs / "roadmap.md").read_text()
        _, problems = self.fix()
        self.assertTrue(problems)
        self.assertEqual((self.docs / "roadmap.md").read_text(), before)
        self.assertIn(("error", "visual"), self.rules())

    def test_custom_checks(self):
        script = self.tmp / "extra.py"
        script.write_text("print('prd.md:3: warning [house-style] say household, not family')\n")
        self.config(checks=[f"{sys.executable} {script}", f"{sys.executable} -c 'raise SystemExit(2)'"])
        rules = self.rules()
        self.assertIn(("warning", "house-style"), rules)
        self.assertIn(("error", "checks"), rules)

    def test_failed_custom_check_with_non_error_findings_still_fails(self):
        script = self.tmp / "extra.py"
        self.config(checks=[f"{sys.executable} {script}"])
        for level in ("warning", "advice", "error"):
            with self.subTest(level=level):
                script.write_text(f"print('prd.md:3: {level} [custom] a finding')\nraise SystemExit(2)\n")
                code, out = run("check", self.docs, "--advice=all")
                self.assertEqual(code, 1, out)
                self.assertIn(f"{level} [custom] a finding", out)
                self.assertEqual("error [checks]" in out, level != "error", out)

    def test_archive_history(self):
        self.config(history="archive")
        self.assertIn(("warning", "archive"), self.rules())  # B-001 is done but not archived
        (self.docs / "backlog").mkdir()
        (self.docs / "backlog" / "archive.md").write_text(
            "# Acme — Backlog archive\n\n**Answers:** the full text of finished items.\n\n"
            "## Summary\n\nFinished items.\n\n## Contents\n\n## Items\n\n"
            '<a id="b-001"></a>\n### B-001 — Set up the ledger store\n\n'
            "- **Milestone:** [M1](../roadmap.md#m1)\n- **Requirement:** [R-CORE-01](../prd.md#r-core-01)\n"
            "- **Design:** [T-STORE](../tdd.md#t-store)\n- **Owner:** Sam\n- **Done when:** the store accepts writes\n"
            "\n*Corrected 2026-09-19: the store was Postgres, not SQLite.*\n")
        self.fix()
        rules = self.rules()
        self.assertNotIn(("warning", "archive"), rules)
        self.assertNotIn(("error", "duplicate"), rules)

    def test_evidence_links_are_checked(self):
        runs = self.docs / "qa" / "runs"
        runs.mkdir(parents=True)
        (runs / "2026-09-24-import.md").write_text("# Import run\n\nVerifies [QA-CORE-01](../../qa.md#qa-core-99).\n")
        self.assertIn(("error", "link"), self.rules())

    def test_kept_anchors(self):
        listing = self.tmp / "anchors.txt"
        _, out = run("anchors", self.docs)
        self.assertIn("tdd.md#t-store", out)
        listing.write_text(out)
        self.edit("tdd.md", '<a id="t-store"></a>\n### T-STORE — Ledger store', "### Ledger store")
        report = ipq.Report(ipq.DocSet(self.docs))
        ipq.check(ipq.DocSet(self.docs), report, listing)
        self.assertIn("kept-anchor", {rule for _, _, _, rule, _ in report.items})


class AnchorAboveHeading(Base):
    """An anchor line directly above the heading after a generated section belongs to that heading,
    as heading_path reads it; fix keeps it when it rewrites the generated section (2.1.1)."""

    # where: the document, the heading after its generated section, that section, and an edit
    # that puts the section out of date
    CONTENTS = ("README.md", "## Find an answer\n", "Contents",
                ("- [Glossary](#glossary)\n", "- [Glossary](#stale)\n"))
    GLANCE = ("prd.md", "## Problem\n", "At a glance",
              ("0 of 2 accepted requirements fully traced\n", "0 of 9 accepted requirements fully traced\n"))

    def keeps(self, where, anchors):
        name, heading, section, stale = where
        self.edit(name, heading, anchors + heading)
        self.edit(name, *stale)  # the generated section out of date, so fix must rewrite it
        listing = self.tmp / "anchors.txt"
        _, out = run("anchors", self.docs)
        for a in re.findall(r'id="([^"]+)"', anchors):
            self.assertIn(f"{name}#{a}", out)
        listing.write_text(out)
        changed, problems = self.fix()
        self.assertIn(f"{name}: {section}", changed)
        self.assertEqual(problems, [])
        text = (self.docs / name).read_text()
        self.assertIn("\n\n" + anchors + heading, text)       # the anchors kept, directly above the heading
        self.assertNotIn("\n\n\n" + anchors, text)            # one blank line above them, not two
        report = ipq.Report(ipq.DocSet(self.docs))
        ipq.check(ipq.DocSet(self.docs), report, listing)
        rules = {(level, rule) for level, _, _, rule, _ in report.items}
        self.assertNotIn(("error", "kept-anchor"), rules)
        self.assertNotIn(("error", "generated"), rules)
        self.assertNotIn(("error", "visual"), rules)             # the glance really draws
        before = (self.docs / name).read_bytes()
        self.assertEqual(self.fix(), ([], []))
        self.assertEqual((self.docs / name).read_bytes(), before)

    def test_after_contents(self):
        self.keeps(self.CONTENTS, '<a id="x"></a>\n')

    def test_after_contents_with_a_blank_line_before_the_heading(self):
        self.keeps(self.CONTENTS, '<a id="x"></a>\n\n')

    def test_after_contents_two_anchors(self):
        self.keeps(self.CONTENTS, '<a id="x"></a>\n<a id="y"></a>\n')

    def test_after_at_a_glance(self):
        self.keeps(self.GLANCE, '<a id="x"></a>\n')

    def test_after_at_a_glance_with_a_blank_line_before_the_heading(self):
        self.keeps(self.GLANCE, '<a id="x"></a>\n\n')

    def test_after_at_a_glance_two_anchors(self):
        self.keeps(self.GLANCE, '<a id="x"></a>\n<a id="y"></a>\n')


class Visuals(Base):
    def test_every_block_fits_uses_glyphs_and_has_a_fallback(self):
        for role in visuals.BLOCKS_BY_ROLE:
            for block, fallback in self.blocks(role):
                for line in block.splitlines():
                    self.assertLessEqual(len(line), visuals.WIDTH, line)
                    self.assertFalse(set(line) - visuals.GLYPHS, (role, line))
                self.assertTrue(fallback.strip())
                self.assertFalse(set(fallback) - visuals.GLYPHS - set("’—–"), fallback)

    def test_milestones(self):
        ms, _ = ipq.milestones(ipq.DocSet(self.docs))
        m1, m2 = ms
        self.assertEqual((m1["work"]["done"], sum(m1["work"].values())), (1, 3))
        self.assertEqual((m1["evidenced"], m1["checks"]), (1, 2))
        self.assertEqual((m2["blocked"], m2["deltas"]), (["B-004"], ["D-001"]))
        block, fallback = self.blocks("roadmap")[0]
        self.assertIn("M1 ──▶ M2", block)
        self.assertIn("1 of 3 backlog items done", fallback)

    def test_velocity_by_week_and_sprint(self):
        block, fallback = self.blocks("roadmap")[1]
        self.assertIn("by week", block)
        self.assertIn("week W39: 1", fallback)
        self.config(period={"unit": "sprint", "start": "2026-09-07", "days": 7, "quiet": {"4": "documents-only"}})
        block, fallback = self.blocks("roadmap")[1]
        self.assertIn("by sprint", block)
        self.assertIn("· a quiet sprint: documents-only", block)
        rows = dict(l.split(None, 1) for l in block.splitlines() if l.strip().startswith(("sprint", "checks")))
        self.assertEqual(rows["sprint"].split(), ["3", "4"])
        self.assertEqual(rows["checks"].split(), ["1", "·"])
        self.config(period={"unit": "sprint", "start": "2026-09-07", "days": 7, "quiet": {"3": "documents-only"}})
        _, findings = self.glance("roadmap")
        self.assertTrue(any("declared quiet" in f for f in findings))

    def test_calendar_units(self):
        p = visuals.Calendar
        d = dt.date(2026, 9, 24)
        self.assertEqual([p({"unit": u}).label(p({"unit": u}).of(d)) for u in ("day", "week", "month", "quarter")],
                         ["09-24", "W39", "2026-09", "2026Q3"])
        month = p({"unit": "month"})
        self.assertEqual([month.label(k) for k in month.window([month.of(dt.date(2026, 11, 3))], dt.date(2027, 1, 9))],
                         ["2026-11", "2026-12", "2027-01"])
        self.config(period={"unit": "fortnight"})
        _, findings = self.glance("roadmap")
        self.assertTrue(any("period unit 'fortnight'" in f for f in findings))


class Iterations(Base):
    """Periods bounded by the closing lines the documents hold."""

    def setUp(self):
        super().setUp()
        runs = self.docs / "qa" / "runs"
        runs.mkdir(parents=True)
        for name in ("2026-09-24-import.md", "2026-09-26-edit.md"):
            (runs / name).write_text(f"# Run {name}\n")
        self.edit("qa.md", "| 2026-09-24 run |", "| [run](qa/runs/2026-09-24-import.md) |")
        self.config(period={"unit": "iteration", "name": "sprint"})

    def iterations(self, *lines):
        text = (self.docs / "roadmap.md").read_text().rstrip("\n")
        (self.docs / "roadmap.md").write_text(text + "\n\n## Iterations\n\n" + "\n".join(lines) + "\n")

    def velocity(self, today=STAMP):
        body, findings = self.glance("roadmap", today)
        if findings:
            return findings
        block = body.split("QA checks first evidenced", 1)[1].split("```", 1)[0]
        return {l.split()[0]: l.split()[1:] for l in block.splitlines() if l.strip().startswith(("sprint", "checks"))}

    def test_link_decides_even_on_a_busy_day(self):
        self.iterations(
            '- <a id="sprint-3"></a>**SPRINT-3** Editing — closed 2026-09-24',
            '- <a id="sprint-2"></a>**SPRINT-2** Import — [run](qa/runs/2026-09-24-import.md) · closed 2026-09-24',
            '- <a id="sprint-1"></a>**SPRINT-1** Documents only — closed 2026-09-20')
        rows = self.velocity()
        self.assertEqual(rows["sprint"], ["1", "2", "3"])
        self.assertEqual(rows["checks"], ["·", "1", "·"])  # sprints 1 and 3 linked no run: quiet, not 0
        self.assertNotIn(("error", "visual"), self.rules())

    def test_a_date_shared_by_two_closes_needs_a_link(self):
        self.edit("qa.md", "[run](qa/runs/2026-09-24-import.md)", "2026-09-24 run")
        self.iterations('- <a id="sprint-3"></a>**SPRINT-3** Editing — closed 2026-09-24',
                        '- <a id="sprint-2"></a>**SPRINT-2** Import — closed 2026-09-24')
        findings = self.velocity()
        self.assertTrue(any("close date of SPRINT-2, SPRINT-3" in f for f in findings), findings)

    def test_unlinked_evidence_falls_to_the_next_close_and_iterations_vary_in_length(self):
        self.iterations('- <a id="sprint-2"></a>**SPRINT-2** Edit — closed 2026-09-28',
                        '- <a id="sprint-1"></a>**SPRINT-1** Setup — closed 2026-09-10')
        self.assertEqual(self.velocity()["checks"], ["·", "1"])

    def test_evidence_after_the_last_close_is_the_open_iteration(self):
        self.iterations('- <a id="sprint-1"></a>**SPRINT-1** Setup — closed 2026-09-10')
        rows = self.velocity()
        self.assertEqual((rows["sprint"], rows["checks"]), (["1", "open"], ["·", "1"]))

    def test_a_run_can_name_its_iteration(self):
        (self.docs / "qa" / "runs" / "2026-09-24-import.md").write_text("# Run\n\n- **Period:** sprint 1\n")
        self.iterations('- <a id="sprint-2"></a>**SPRINT-2** Edit — closed 2026-09-28',
                        '- <a id="sprint-1"></a>**SPRINT-1** Import — closed 2026-09-10')
        self.assertEqual(self.velocity()["checks"], ["1", "·"])
        (self.docs / "qa" / "runs" / "2026-09-24-import.md").write_text("# Run\n\n- **Period:** sprint 9\n")
        self.assertTrue(any("names no closed sprint" in f for f in self.velocity()))

    def test_a_run_belongs_to_one_iteration(self):
        self.iterations('- <a id="sprint-2"></a>**SPRINT-2** Again — [run](qa/runs/2026-09-24-import.md) · closed 2026-09-25',
                        '- <a id="sprint-1"></a>**SPRINT-1** Import — [run](qa/runs/2026-09-24-import.md) · closed 2026-09-24')
        self.assertTrue(any("linked by both" in f for f in self.velocity()))

    def test_a_closing_line_needs_its_date(self):
        self.iterations('- <a id="sprint-1"></a>**SPRINT-1** Import — [run](qa/runs/2026-09-24-import.md)')
        self.assertIn(("error", "dates"), self.rules())

    def test_backlog_done_lines_as_iterations(self):
        self.config(period={"unit": "iteration", "from": "backlog", "name": "sprint", "match": "sprint"})
        self.edit("backlog.md", "Set up the ledger store — ", "Set up the ledger store, sprint — ")
        rows = self.velocity()
        self.assertEqual(rows["sprint"], ["1", "open"])  # B-001 closes sprint 1; the run came after it

    def test_flow_attributes_by_link(self):
        self.iterations('- <a id="sprint-3"></a>**SPRINT-3** Later — closed 2026-09-14',
                        '- <a id="sprint-2"></a>**SPRINT-2** Import — closed 2026-09-14',
                        '- <a id="sprint-1"></a>**SPRINT-1** Setup — closed 2026-09-01')
        _, findings = self.glance("delta")
        self.assertTrue(any("D-001 found" in f for f in findings), findings)
        self.edit("delta.md", "- **Found:** 2026-09-14", "- **Found:** 2026-09-14, in [sprint 3](roadmap.md#sprint-3)")
        body, findings = self.glance("delta")
        self.assertEqual(findings, [])
        flow = body.split("opened and closed", 1)[1].split("```", 1)[0]
        rows = {l.split()[0]: l.split()[1:] for l in flow.splitlines() if l.strip()[:6] in ("sprint", "opened")}
        self.assertEqual(rows["opened"][rows["sprint"].index("3")], "1")
        self.config(period={"unit": "iteration"}, flow={"unit": "day"})
        self.assertIn("by day", self.glance("delta")[0])


class EvidenceLayout(Base):
    def populate(self, count, checks=1):
        roadmap = self.docs / "roadmap.md"
        qa = self.docs / "qa.md"
        milestones, rows = [], []
        for i in range(1, count + 1):
            milestones.append(
                f'<a id="m{i}"></a>\n### M{i} — Milestone {i}\n\n'
                '- **Status:** planned\n- **Target:** TBD\n- **Depends on:** none\n'
                '- **Includes:** [R-CORE-01](prd.md#r-core-01)\n- **Exit criteria:** TBD\n')
            for j in range(checks):
                rid = f"QA-CORE-{(i - 1) * checks + j + 1:03d}"
                evidence = "2026-09-24 run" if j == 0 else "none"
                rows.append(f'| <a id="{rid.lower()}"></a>{rid} | [R-CORE-01](prd.md#r-core-01) | '
                            f'Test | e2e | [M{i}](roadmap.md#m{i}) | {evidence} |')
        roadmap.write_text(roadmap.read_text().split("## Milestones\n")[0] + "## Milestones\n\n" + "\n".join(milestones))
        qa.write_text(qa.read_text().split("## Coverage\n")[0] + "## Coverage\n\n"
                      "| ID | Verifies | Check | Level | Milestone | Evidence |\n"
                      "|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n")

    def test_many_milestones_finish_fix_and_check_and_fit_in_bands(self):
        self.populate(21)
        for command in ("fix", "check"):
            result = subprocess.run([sys.executable, "-B", str(REPO / "skill/tools/ipq.py"),
                                     command, str(self.docs)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        block = visuals.evidence_block(visuals.Ctx(ipq.DocSet(self.docs), STAMP))
        for line in block.lines:
            self.assertLessEqual(len(line), visuals.WIDTH, line)
        headers = [line.split()[:-1] for line in block.lines if line.lstrip().startswith("M")]
        self.assertGreater(len(headers), 1)
        self.assertEqual([mid for band in headers for mid in band], [f"M{i}" for i in range(1, 22)])
        totals = [line.split()[-1] for line in block.lines if line.lstrip().startswith("total ")]
        self.assertEqual(sum(int(t.split("/")[1]) for t in totals), 21)
        self.assertIn("Totals within each band; all milestones: 21/21", block.lines)
        for i in range(1, 22):
            self.assertIn(f"M{i}: CORE 1 of 1.", block.fallback)

    def test_dense_evidence_scales_and_retains_exact_counts(self):
        self.populate(2, checks=120)
        block = visuals.evidence_block(visuals.Ctx(ipq.DocSet(self.docs), STAMP))
        for line in block.lines:
            self.assertLessEqual(len(line), visuals.WIDTH, line)
        self.assertIn("each mark ≈", "\n".join(block.lines))
        self.assertIn("1/120", "\n".join(block.lines))
        self.assertIn("2/240", "\n".join(block.lines))
        self.assertEqual(block.fallback, "M1: CORE 1 of 120. M2: CORE 1 of 120.")


class MoreVisuals(Base):
    def test_undated_evidence_gives_a_partial_view(self):
        self.edit("qa.md", "| none |", "| 2026-09-25 run |")
        self.edit("qa.md", "2026-09-24 run", "passed")
        body, findings = self.glance("roadmap")
        self.assertEqual(findings, [])
        velocity = body.split("QA checks first evidenced", 1)[1]
        self.assertIn("partial: 1 left out", velocity)
        self.assertIn("Left out for missing data: QA-CORE-01.", velocity)

    def test_a_contradiction_still_refuses(self):
        self.config(period={"unit": "week", "quiet": {"W39": "documents-only"}})
        _, findings = self.glance("roadmap")
        self.assertTrue(any("declared quiet" in f for f in findings))
        self.assertIn(("error", "visual"), self.rules())

    def test_every_block_states_its_measure(self):
        for role in visuals.BLOCKS_BY_ROLE:
            for block, _ in self.blocks(role):
                title, measure = block.splitlines()[:2]
                self.assertTrue(measure.strip(), (role, title))

    def test_waiting_and_awaiting(self):
        block, fallback = self.blocks("roadmap")[2]
        self.assertIn("M2   ▲", block)
        self.assertIn("D-001, waiting on a decision", fallback)
        _, awaiting = self.blocks("delta")
        self.assertIn("15+    ▲  1", awaiting[0])
        self.assertIn("D-001 (15 days, decided by product)", awaiting[1])
        self.edit("delta.md", "- **Waits on:** decision\n", "")
        body, findings = self.glance("roadmap")
        self.assertEqual(findings, [])
        self.assertNotIn("Open delta entries blocking", body)  # the only entry is left out, so nothing to draw

    def test_trace(self):
        block, fallback = self.blocks("prd")[0]
        self.assertIn("0 of 2 accepted requirements fully traced", block)
        self.assertIn("R-CORE-02 lacks ux, tdd, evidence.", fallback)
        self.edit("prd.md", "- **Users:** household member", "- **Users:** household member\n- **Trace:** no ux")
        self.edit("prd.md", "category\n\n- **Priority:** must", "category\n\n- **Priority:** must\n- **Trace:** no ux")
        block, _ = self.blocks("prd")[0]
        self.assertIn("1 of 2 accepted requirements fully traced", block)
        self.assertIn("R-CORE-02  −", block)
        self.assertNotIn("R-CORE-01", block)

    def test_flow_leaves_out_undated_entries(self):
        self.edit("delta.md", "- **Found:** 2026-09-14", "- **Found:** last week")
        body, findings = self.glance("delta")
        self.assertEqual(findings, [])
        self.assertNotIn("opened and closed", body)  # the only entry has no date: nothing left to draw

    def test_states(self):
        self.edit("ux.md", "## Screen inventory", "## Screen inventory\n\nOne screen.\n\n## Screens\n\n"
                  '<a id="scr-01"></a>\n### SCR-01 — List\n\n- **Purpose:** buy things\n'
                  "- **Requirements:** [R-CORE-01](prd.md#r-core-01)\n- **States:** default, empty, offline n/a\n\n"
                  "- **Default:** the items.\n- **Empty:** nothing to buy.\n\n## Screen inventoryx")
        self.edit("ux.md", "## Screen inventoryx", "## Flows")
        text = (self.docs / "ux.md").read_text()
        self.assertIn("## Screens", text)
        block, fallback = self.blocks("ux")[0]
        self.assertRegex(block, r"SCR-01 List\s+▓\s+▓\s+░\s+░\s+−")
        self.assertIn("SCR-01 lacks loading, error.", fallback)

    def test_size_block(self):
        block = visuals.size_block(ipq.DocSet(self.docs))
        self.assertIn("┆", "\n".join(block.lines))
        for line in block.lines:
            self.assertLessEqual(len(line), visuals.WIDTH)

    def test_html(self):
        out = self.tmp / "roadmap.html"
        run("roadmap", self.docs, "--html", out)
        page = out.read_text()
        self.assertIn("Import and review", page)
        self.assertIn("prefers-color-scheme: dark", page)


if __name__ == "__main__":
    unittest.main()
