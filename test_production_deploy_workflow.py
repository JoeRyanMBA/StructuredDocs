import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKFLOW = ROOT / ".github/workflows/deploy-production.yml"


class ProductionPreflightTests(unittest.TestCase):
    def run_preflight(self, directory):
        workflow = WORKFLOW.read_text()
        script = workflow.split(
            '"PRODUCTION_DIR=\'${PRODUCTION_DIR}\' bash -s" <<\'EOF\'\n', 1
        )[1].split("          EOF\n", 1)[0]
        return subprocess.run(
            ["bash", "-c", script],
            env={**os.environ, "PRODUCTION_DIR": str(directory)},
            capture_output=True,
            text=True,
        )

    def test_writable_directory_passes_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            production = Path(directory)
            (production / ".env").write_text("DATABASE_URL=example\nADMIN_API_KEY=example\n")
            (production / "docker-compose.single.yml").write_text("services:\n  app:\n    build: .\n")
            (production / ".enable_blueprints").touch()
            result = self.run_preflight(production)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unwritable_directory_reports_repair_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            production = Path(directory)
            production.chmod(0o555)
            try:
                if os.access(production, os.W_OK):
                    self.skipTest("Current user bypasses directory permissions")
                result = self.run_preflight(production)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Cannot write to or access", result.stdout)
                self.assertIn("docs/single-vps-three-stacks.md section 8", result.stdout)
            finally:
                production.chmod(0o700)

    def test_missing_directory_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_preflight(Path(directory) / "missing")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing", result.stdout)

    def test_unsearchable_directory_reports_repair_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            production = Path(directory)
            production.chmod(0o600)
            try:
                if os.access(production, os.X_OK):
                    self.skipTest("Current user bypasses directory permissions")
                result = self.run_preflight(production)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Cannot write to or access", result.stdout)
            finally:
                production.chmod(0o700)


if __name__ == "__main__":
    unittest.main()
