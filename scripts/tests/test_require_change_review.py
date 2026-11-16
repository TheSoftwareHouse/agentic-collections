import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "require-change-review.py"


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


class RequireChangeReviewTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sh(self.repo, "git", "init", "-q", "-b", "main")
        sh(self.repo, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init")
        sh(self.repo, "git", "checkout", "-q", "-b", "feat/x")

    def tearDown(self):
        self._tmp.cleanup()

    def run_hook(self, command, cwd=None):
        event = {"tool_name": "Bash", "tool_input": {"command": command}}
        return subprocess.run(
            [sys.executable, str(HOOK)], cwd=cwd or self.repo, input=json.dumps(event),
            capture_output=True, text=True,
        )

    def mark(self, repo=None):
        repo = repo or self.repo
        d = repo / ".git" / "change-review"
        d.mkdir(parents=True, exist_ok=True)
        (d / "feat%2Fx").write_text("sha\n", encoding="utf-8")

    def test_blocks_pr_create_without_review(self):
        result = self.run_hook("gh pr create --base main --fill")
        self.assertEqual(result.returncode, 2)
        self.assertIn("change-reviewer", result.stderr)

    def test_allows_pr_create_after_review(self):
        self.mark()
        self.assertEqual(self.run_hook("gh pr create --base main --fill").returncode, 0)

    def test_marker_survives_later_commits(self):
        self.mark()
        sh(self.repo, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "fix")
        self.assertEqual(self.run_hook("gh pr create").returncode, 0)

    def test_blocks_chained_pr_create(self):
        self.assertEqual(self.run_hook("git push -u origin feat/x && gh pr create --fill").returncode, 2)

    def test_ignores_other_commands(self):
        for command in ("git push origin feat/x", "gh pr view 28", "gh pr edit 28 --body-file b.md", "echo done",
                        'git commit -m "docs: run gh pr create later"', 'echo "then; gh pr create"',
                        "gh pr create --help", "grep -r 'gh pr create' ."):
            self.assertEqual(self.run_hook(command).returncode, 0, command)

    def test_blocks_other_spellings(self):
        for command in ("gh pr new --fill", "gh -R o/r pr create", "gh --repo o/r pr create", "gh --repo=o/r pr create",
                        "/opt/homebrew/bin/gh pr create", "GH_TOKEN=x gh pr create", "gh  pr  create",
                        "git push\ngh pr create --fill", "(gh pr create)"):
            self.assertEqual(self.run_hook(command).returncode, 2, command)

    def test_uses_the_event_cwd_not_the_process_cwd(self):
        self.mark()
        other = Path(tempfile.mkdtemp())
        try:
            sh(other, "git", "init", "-q", "-b", "main")
            sh(other, "git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i")
            sh(other, "git", "checkout", "-q", "-b", "feat/x")
            event = {"cwd": str(other), "tool_input": {"command": "gh pr create"}}
            result = subprocess.run([sys.executable, str(HOOK)], cwd=self.repo, input=json.dumps(event),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
        finally:
            shutil.rmtree(other)

    def test_branches_that_differ_only_in_slash_do_not_share_a_marker(self):
        self.mark()
        sh(self.repo, "git", "checkout", "-q", "-b", "feat-x")
        self.assertEqual(self.run_hook("gh pr create").returncode, 2)

    def test_malformed_input_is_allowed(self):
        for raw in ("not json", "[]", '{"tool_input": []}', '{"tool_input": {"command": 5}}'):
            result = subprocess.run([sys.executable, str(HOOK)], cwd=self.repo, input=raw, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, raw)

    def test_linked_worktree_uses_its_own_marker(self):
        wt = self.repo.parent / (self.repo.name + "-wt")
        sh(self.repo, "git", "worktree", "add", "-q", str(wt), "-b", "feat/y")
        try:
            self.assertEqual(self.run_hook("gh pr create", cwd=wt).returncode, 2)
            marker = subprocess.run(["git", "rev-parse", "--git-path", "change-review"], cwd=wt,
                                    capture_output=True, text=True).stdout.strip()
            path = (wt / marker) if not Path(marker).is_absolute() else Path(marker)
            path.mkdir(parents=True, exist_ok=True)
            (path / "feat%2Fy").write_text("sha\n", encoding="utf-8")
            self.assertEqual(self.run_hook("gh pr create", cwd=wt).returncode, 0)
        finally:
            sh(self.repo, "git", "worktree", "remove", "--force", str(wt))


if __name__ == "__main__":
    unittest.main()
