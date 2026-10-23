import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKFLOW = ROOT / ".github/workflows/deploy-staging.yml"


@unittest.skipUnless(shutil.which("docker"), "Docker Compose is required")
class StagingDeployWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            ["docker", "compose", "version"], capture_output=True, text=True
        )
        if result.returncode:
            raise unittest.SkipTest("Docker Compose is required")

    def test_build_override_preserves_server_configuration(self):
        workflow = WORKFLOW.read_text()
        compose_function = workflow.split("            compose() {\n", 1)[1]
        compose_function = compose_function.split("            }\n", 1)[0]
        command = (
            "set -euo pipefail\n"
            "DC=(docker compose)\n"
            "compose() {\n" + compose_function + "}\n"
            "compose config --format json\n"
        )
        builds = (
            "    build: .\n",
            '    build: "."\n',
            "    build:\n      context: ./\n",
            "    build: ./source\n",
            "    build:\n      context: ./source\n"
            "      dockerfile: source/Dockerfile\n      args:\n        APP_VERSION: staging\n",
            "",
        )
        for build in builds:
            with self.subTest(build=build), tempfile.TemporaryDirectory() as directory:
                staging = Path(directory)
                server_config = (
                    "services:\n  app:\n"
                    + build
                    + "    image: structureddocs-backend:staging\n"
                    "    environment:\n      APP_ENV: staging\n"
                    "    ports:\n      - '28080:8080'\n"
                    "    volumes:\n      - ./data/images:/app/data/images\n"
                    "    extra_hosts:\n      - 'host.docker.internal:host-gateway'\n"
                )
                server_file = staging / "docker-compose.single.yml"
                server_file.write_text(server_config)
                (staging / ".env").touch()
                shutil.copy(ROOT / "docker-compose.staging-build.yml", staging)
                result = subprocess.run(
                    ["bash", "-c", command],
                    cwd=staging,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                config = json.loads(result.stdout)
                app = config["services"]["app"]
                self.assertEqual(config["name"], "staging")
                self.assertEqual(app["build"]["context"], str(staging))
                self.assertEqual(app["build"]["dockerfile"], "Dockerfile")
                self.assertEqual(app["environment"]["APP_ENV"], "staging")
                self.assertEqual(app["ports"][0]["published"], "28080")
                self.assertEqual(app["volumes"][0]["source"], str(staging / "data/images"))
                hosts = json.dumps(app["extra_hosts"])
                self.assertIn("host.docker.internal", hosts)
                self.assertIn("host-gateway", hosts)
                self.assertEqual(server_file.read_text(), server_config)
                if "args:" in build:
                    self.assertEqual(app["build"]["args"]["APP_VERSION"], "staging")

    def test_preflight_does_not_require_literal_build_shorthand(self):
        preflight = WORKFLOW.read_text().split(
            "      - name: Sync source and deploy staging stack", 1
        )[0]
        self.assertNotIn("build:", preflight)


if __name__ == "__main__":
    unittest.main()
