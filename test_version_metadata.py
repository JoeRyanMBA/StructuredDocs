import json
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path

import pytest

from backend.app import _load_version_metadata


ROOT = Path(__file__).resolve().parent


@pytest.fixture
def version_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in ("APP_VERSION", "GIT_COMMIT", "BUILD_TIME"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: b"abc123\n")
    backend = tmp_path / "backend"
    backend.mkdir()
    return backend / "version.json"


def test_release_version_comes_from_version_file(version_directory):
    version_directory.write_text(json.dumps({"version": "0.3.0"}))

    metadata = _load_version_metadata()

    assert metadata["version"] == "0.3.0"
    assert metadata["commit"] == "abc123"
    assert metadata["build_time"] is None


def test_environment_metadata_takes_precedence(version_directory, monkeypatch):
    version_directory.write_text(json.dumps({
        "version": "0.2.0",
        "commit": "oldcommit",
        "build_time": "2025-01-01T00:00:00Z",
    }))
    monkeypatch.setenv("APP_VERSION", "0.3.0")
    monkeypatch.setenv("GIT_COMMIT", "newcommit")
    monkeypatch.setenv("BUILD_TIME", "2026-11-09T12:00:00Z")

    assert _load_version_metadata() == {
        "version": "0.3.0",
        "commit": "newcommit",
        "build_time": "2026-11-09T12:00:00Z",
    }


def test_recorded_build_time_is_preserved(version_directory):
    version_directory.write_text(json.dumps({
        "version": "0.3.0",
        "build_time": "2026-11-09T12:00:00Z",
    }))

    assert _load_version_metadata()["build_time"] == "2026-11-09T12:00:00Z"


def test_missing_metadata_does_not_invent_build_time(version_directory):
    metadata = _load_version_metadata()

    assert metadata["version"] is None
    assert metadata["build_time"] is None


def test_ci_reads_release_version_from_json(tmp_path, monkeypatch):
    workflow = (ROOT / ".github/workflows/backend-ci.yml").read_text()
    step = workflow.split("      - name: Derive version metadata\n", 1)[1]
    step = step.split("      - name:", 1)[0]
    command = textwrap.dedent(step.split("        run: |\n", 1)[1])
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "version.json").write_text(json.dumps({"version": "0.4.1"}))
    output = tmp_path / "outputs"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    result = subprocess.run(
        ["bash", "-c", "set -euo pipefail\ngit() { printf 'abc123\\n'; }\n" + command],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    metadata = dict(line.split("=", 1) for line in output.read_text().splitlines())
    assert metadata["app_version"] == "0.4.1"
    assert metadata["commit"] == "abc123"
    assert datetime.fromisoformat(metadata["build_time"].replace("Z", "+00:00")).tzinfo