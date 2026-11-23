"""Offline regression checks for commit and push protection."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_secrets.py"

class CredentialGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.run_git("init", "-q")
        self.run_git("config", "user.name", "Credential Guard Test")
        self.run_git("config", "user.email", "test@example.invalid")

    def tearDown(self):
        self.temp.cleanup()

    def run_git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def guard(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.repo, capture_output=True, text=True)

    def test_blocks_secret_in_index_without_echoing_it(self):
        secret = "AIza" + "A" * 35
        (self.repo / "config.js").write_text("const key = '" + secret + "';\n")
        self.run_git("add", "config.js")
        result = self.guard()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(secret, result.stdout + result.stderr)

    def test_blocks_dotenv_even_when_force_added(self):
        (self.repo / ".env").write_text("GEMINI_API_KEY=\n")
        self.run_git("add", ".env")
        self.assertEqual(self.guard().returncode, 1)

    def test_allows_empty_env_example(self):
        (self.repo / ".env.example").write_text("GEMINI_API_KEY=\n")
        self.run_git("add", ".env.example")
        self.assertEqual(self.guard().returncode, 0)

    def test_blocks_secret_removed_from_latest_commit_but_left_in_history(self):
        path = self.repo / "config.js"
        path.write_text("AIza" + "B" * 35)
        self.run_git("add", "config.js")
        self.run_git("commit", "-qm", "Add configuration")
        path.write_text("Use environment variables")
        self.run_git("add", "config.js")
        self.run_git("commit", "-qm", "Remove configuration")
        self.assertEqual(self.guard().returncode, 0)
        self.assertEqual(self.guard("--history").returncode, 1)

if __name__ == "__main__":
    unittest.main()
