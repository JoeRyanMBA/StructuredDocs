import os
import subprocess
import tempfile
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parent / ".github/workflows/promote-environment.yml"


def script_for(step_name):
    step = WORKFLOW.read_text().split(f"      - name: {step_name}\n", 1)[1]
    # Stop at the next job, preserving the shell block's relative indentation.
    lines = []
    for line in step.split("        run: |\n", 1)[1].splitlines():
        if line and not line.startswith("          "):
            break
        lines.append(line[10:])
    return "\n".join(lines)


class PromoteEnvironmentWorkflowTests(unittest.TestCase):
    def run_script(self, step_name, extra_env=None, prelude=""):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            env = {
                **os.environ,
                "GITHUB_OUTPUT": str(output),
                "GITHUB_STEP_SUMMARY": str(output),
                "RUNNER_TEMP": directory,
                "GITHUB_SERVER_URL": "https://github.com",
                "GITHUB_REPOSITORY": "example/repo",
                "GH_REPO": "example/repo",
                "GITHUB_ACTOR": "operator",
                "GITHUB_RUN_ID": "123",
                "SOURCE": "dev",
                "TARGET": "staging",
                **(extra_env or {}),
            }
            result = subprocess.run(
                ["bash", "-c", prelude + "\n" + script_for(step_name)],
                env=env, capture_output=True, text=True,
            )
            return result, output.read_text() if output.exists() else ""

    def test_only_sequential_promotions_are_allowed(self):
        for source in ("dev", "staging", "production", "", "dev; exit 0"):
            for target in ("dev", "staging", "production", ""):
                with self.subTest(source=source, target=target):
                    result, output = self.run_script(
                        "Validate promotion and resolve branches",
                        {"SOURCE_ENV": source, "TARGET_ENV": target},
                    )
                    expected = {
                        ("dev", "staging"): "source=dev\ntarget=staging\n",
                        ("staging", "production"): "source=staging\ntarget=main\n",
                    }.get((source, target))
                    self.assertEqual(result.returncode, 0 if expected else 1)
                    self.assertEqual(output, expected or "")

    def test_pr_creation_reuse_and_no_changes(self):
        mock = """
gh() {
  case "$1 $2" in
    "pr list")
      local jq_filter=
      while (($#)); do
        if [[ "$1" == "--jq" ]]; then
          jq_filter=$2
          break
        fi
        shift
      done
      printf '%s' "$PR_DATA" | jq -r "$jq_filter" ;;
    "api "*) echo "$AHEAD" ;;
    "pr create") printf 'CREATE'; printf ' <%s>' "$@"; echo ;;
    *) return 99 ;;
  esac
}
"""
        for pr_data, ahead, expected in (
            (
                '[{"url":"https://github.com/example/repo/pull/1",'
                '"headRepository":{"nameWithOwner":"example/repo"}}]',
                "1",
                "Reusing promotion PR",
            ),
            (
                '[{"url":"https://github.com/example/repo/pull/2",'
                '"headRepository":{"nameWithOwner":"contributor/repo"}}]',
                "2",
                "CREATE",
            ),
            ("[]", "0", "no PR needed"),
        ):
            with self.subTest(pr_data=pr_data, ahead=ahead):
                result, _ = self.run_script(
                    "Create or reuse promotion pull request",
                    {"PR_DATA": pr_data, "AHEAD": ahead}, mock,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, result.stdout)
                if expected == "CREATE":
                    self.assertIn("<--base> <staging> <--head> <dev>", result.stdout)
                else:
                    self.assertNotIn("CREATE", result.stdout)

    def test_force_sync_lease_noop_and_rejection(self):
        mock = """
gh() { [[ "$*" == "auth setup-git" ]]; }
git() {
  case "$1" in
    init|remote|fetch) return 0 ;;
    rev-parse)
      if [[ "$2" == "refs/remotes/origin/dev" ]]; then
        echo "$SOURCE_SHA"
      else
        echo old-target
      fi ;;
    push) printf 'PUSH'; printf ' <%s>' "$@"; echo; return "$PUSH_STATUS" ;;
    *) return 99 ;;
  esac
}
"""
        for sha, status in (("new-source", "0"), ("old-target", "0"), ("new-source", "1")):
            with self.subTest(sha=sha, status=status):
                result, summary = self.run_script(
                    "Force-align target with an explicit lease",
                    {"SOURCE_SHA": sha, "PUSH_STATUS": status}, mock,
                )
                self.assertEqual(result.returncode, int(status), result.stderr)
                if sha == "old-target":
                    self.assertNotIn("PUSH", result.stdout)
                else:
                    self.assertIn(
                        "<--force-with-lease=refs/heads/staging:old-target> "
                        "<origin> <new-source:refs/heads/staging>", result.stdout,
                    )
                if status == "1":
                    self.assertIn("::error::Force sync refused", result.stdout)
                    self.assertEqual(summary, "")
                elif sha != "old-target":
                    self.assertIn("Previous target: `old-target`", summary)


if __name__ == "__main__":
    unittest.main()
