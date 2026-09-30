"""Installer integration tests; all installations live in temporary projects."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
TARGETS = {"claude": ".claude", "chatgpt": ".agents"}


class Installer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / "project with spaces"
        self.project.mkdir()
        self.source = self.root / "source with spaces"
        self.source.mkdir()
        shutil.copyfile(REPO / "install.sh", self.source / "install.sh")
        shutil.copytree(REPO / "skill", self.source / "skill",
                        ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"))

    def install(self, *args):
        return subprocess.run(["sh", str(self.source / "install.sh"), *map(str, args)],
                              cwd=self.project, capture_output=True, text=True, timeout=20)

    def snapshot(self, root):
        return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_both_targets_coexist_and_tools_run(self):
        expected = self.snapshot(self.source / "skill")
        for target, folder in TARGETS.items():
            with self.subTest(target=target):
                sibling = self.project / folder / "skills" / "other" / "keep.txt"
                sibling.parent.mkdir(parents=True)
                sibling.write_text("unrelated skill")
                result = self.install(target, "--project", self.project)
                self.assert_ok(result)
                dest = self.project / folder / "skills" / "ipq"
                self.assertIn(f"target: {target}", result.stdout)
                self.assertIn(f"destination: {dest}", result.stdout)
                self.assertIn(f'python3 "{dest}/tools/ipq.py" --help', result.stdout)
                self.assertEqual(self.snapshot(dest), expected)
                for command in (("init", "--product", "Example"), ("check",)):
                    self.assert_ok(subprocess.run(
                        [sys.executable, "-B", str(dest / "tools/ipq.py"), *command],
                        cwd=self.project, capture_output=True, text=True, timeout=10))
                self.assert_ok(self.install(target, "--check", "--project", self.project))
                self.assertEqual(sibling.read_text(), "unrelated skill")
        for folder in TARGETS.values():
            self.assertEqual(self.snapshot(self.project / folder / "skills/ipq"), expected)

    def test_default_target_preserves_legacy_project_commands(self):
        self.assert_ok(self.install("--project", self.project))
        self.assertTrue((self.project / ".claude/skills/ipq/SKILL.md").is_file())
        self.assertFalse((self.project / ".agents").exists())
        self.assert_ok(self.install("--check", "--project", self.project))

    def test_checks_report_missing_changed_and_extra_files_without_writing(self):
        for target, folder in TARGETS.items():
            with self.subTest(target=target):
                before = self.snapshot(self.project)
                self.assertNotEqual(self.install(target, "--check", "--project", self.project).returncode, 0)
                self.assertEqual(self.snapshot(self.project), before)
                self.assertFalse((self.project / folder).exists())
                self.assert_ok(self.install(target, "--project", self.project))
                dest = self.project / folder / "skills/ipq"
                for change in ("modified", "missing", "extra"):
                    with self.subTest(change=change):
                        if change == "modified":
                            (dest / "SKILL.md").write_text("different")
                        elif change == "missing":
                            (dest / "SKILL.md").unlink()
                        else:
                            (dest / "extra.txt").write_text("unexpected")
                        before = self.snapshot(self.project)
                        result = self.install(target, "--check", "--project", self.project)
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn("DIFFERS", result.stdout)
                        self.assertEqual(self.snapshot(self.project), before)
                        self.assert_ok(self.install(target, "--project", self.project))

    def test_reinstall_changes_only_selected_target_and_excludes_generated_files(self):
        for target in TARGETS:
            self.assert_ok(self.install(target, "--project", self.project))
        skill = self.source / "skill"
        with (skill / "SKILL.md").open("a") as f:
            f.write("\nUpdated instructions.\n")
        (skill / ".DS_Store").write_text("metadata")
        cache = skill / "tools/__pycache__"
        cache.mkdir(exist_ok=True)
        (cache / "ipq.pyc").write_bytes(b"bytecode")
        for target, folder in TARGETS.items():
            with self.subTest(target=target):
                other = self.project / (".agents" if target == "claude" else ".claude")
                before = self.snapshot(other)
                self.assert_ok(self.install(target, "--project", self.project))
                self.assertEqual(self.snapshot(other), before)
                dest = self.project / folder / "skills/ipq"
                self.assertEqual((dest / "SKILL.md").read_bytes(), (skill / "SKILL.md").read_bytes())
                self.assertFalse((dest / ".DS_Store").exists())
                self.assertFalse((dest / "tools/__pycache__").exists())

    def test_invalid_arguments_do_not_change_installations(self):
        for target in TARGETS:
            self.assert_ok(self.install(target, "--project", self.project))
        before = self.snapshot(self.project)
        cases = [
            ("unknown",), ("claude", "chatgpt"), ("chatgpt", "--unknown"),
            ("chatgpt", "--project"), ("chatgpt", "--project", ""),
            ("chatgpt", "--project", "--check"),
            ("chatgpt", "--project", self.root / "missing"),
            ("chatgpt", "--project", self.source),
            ("chatgpt", "--project", self.project, "--project", self.project),
            ("chatgpt", "--check", "--check", "--project", self.project),
            ("chatgpt", "--project", self.project, "unexpected"),
        ]
        for args in cases:
            with self.subTest(args=args):
                self.assertNotEqual(self.install(*args).returncode, 0)
                self.assertEqual(self.snapshot(self.project), before)


if __name__ == "__main__":
    unittest.main()
