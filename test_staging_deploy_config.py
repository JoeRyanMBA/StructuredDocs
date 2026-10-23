import os
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml


@pytest.fixture
def staging_preflight(tmp_path):
    if not shutil.which("docker") or subprocess.run(
        ["docker", "compose", "version"], capture_output=True
    ).returncode:
        pytest.skip("Docker Compose is required")

    workflow = yaml.safe_load(
        (Path(__file__).parent / ".github/workflows/deploy-staging.yml").read_text()
    )
    step = next(
        step for step in workflow["jobs"]["deploy"]["steps"]
        if step.get("name") == "Check staging stack configuration"
    )
    script = step["run"].split("<<'EOF'\n", 1)[1].rsplit("EOF", 1)[0]
    (tmp_path / ".env").write_text(
        "DATABASE_URL=sqlite:///test.db\nADMIN_API_KEY=unused-test-value\n"
    )
    (tmp_path / ".enable_blueprints").touch()

    def run(compose):
        (tmp_path / "docker-compose.single.yml").write_text(compose)
        return subprocess.run(
            ["bash", "-c", script],
            env={**os.environ, "STAGING_DIR": str(tmp_path)},
            capture_output=True,
            text=True,
        )

    return run


@pytest.mark.parametrize("build", [
    "build: .",
    'build: "."',
    "build: {context: .}",
    "build:\n      context: .",
    "build: . # local source",
])
def test_staging_preflight_accepts_equivalent_build_syntax(staging_preflight, build):
    result = staging_preflight(f"services:\n  app:\n    {build}\n")
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("services", [
    "  app:\n    build: ./source\n",
    "  app:\n    build: ..\n",
    "  app:\n    image: example/app:latest\n",
    "  worker:\n    build: .\n",
    "  app:\n    build: ./source\n  worker:\n    build: .\n",
])
def test_staging_preflight_rejects_wrong_app_context(staging_preflight, services):
    result = staging_preflight(f"services:\n{services}")
    assert result.returncode != 0
    assert "app must build from the environment directory" in result.stderr


def test_staging_preflight_rejects_invalid_compose(staging_preflight):
    result = staging_preflight("services: [\n")
    assert result.returncode != 0
