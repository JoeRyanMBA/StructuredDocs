import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


WORKFLOW = Path(__file__).parent / ".github" / "workflows" / "deploy-staging.yml"


@pytest.mark.skipif(shutil.which("docker") is None, reason="Docker Compose is required")
@pytest.mark.parametrize(
    ("app_build", "expected_success"),
    [
        ("build: .", True),
        ('build: "." # local source', True),
        ("build:\n      context: .\n      dockerfile: Dockerfile", True),
        ("build: {context: .}", True),
        ("build: ./source", False),
        ("build: ..", False),
        ("", False),
    ],
)
def test_staging_build_context_validation(tmp_path, app_build, expected_success):
    workflow = yaml.safe_load(WORKFLOW.read_text())
    steps = workflow["jobs"]["deploy"]["steps"]
    preflight = next(step["run"] for step in steps if step.get("name") == "Check staging stack configuration")
    assert "build:" not in preflight

    deploy = next(step["run"] for step in steps if step.get("name") == "Sync source and deploy staging stack")
    validation = deploy[deploy.index("  compose config -q"):deploy.index("  if ! grep -Fq")]
    (tmp_path / ".env").write_text("")
    (tmp_path / "Dockerfile").write_text("FROM scratch\n")
    (tmp_path / "source").mkdir()
    (tmp_path / "docker-compose.single.yml").write_text(
        f"services:\n  app:\n    image: staging-test\n    {app_build}\n"
        "  unrelated:\n    build: .\n"
    )

    result = subprocess.run(
        [
            "bash",
            "-euc",
            'set -o pipefail\n'
            'compose() { docker compose -p staging -f docker-compose.single.yml --env-file .env "$@"; }\n'
            + validation,
        ],
        cwd=tmp_path,
        env={**os.environ, "STAGING_DIR": str(tmp_path)},
        capture_output=True,
        text=True,
    )
    assert (result.returncode == 0) == expected_success, result.stdout + result.stderr
    if not expected_success:
        assert "Staging app must build from the environment directory" in result.stdout
