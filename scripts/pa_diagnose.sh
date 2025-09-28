#!/usr/bin/env bash

# Diagnose what's currently deployed on PythonAnywhere for StructuredDocs
# Usage: ./scripts/pa_diagnose.sh [PA_USER] [REMOTE_DIR]
# Defaults: PA_USER=JoeRyanMBA, REMOTE_DIR=/home/$(PA_USER)/StructuredDocs

set -euo pipefail

PA_USER="${1:-JoeRyanMBA}"
REMOTE_DIR="${2:-/home/${PA_USER}/StructuredDocs}"
PA_HOST="ssh.pythonanywhere.com"

echo "=== 🩺 PythonAnywhere Diagnose: ${PA_USER}@${PA_HOST} :: ${REMOTE_DIR} ==="

ssh "${PA_USER}@${PA_HOST}" bash -s <<'REMOTE'
set -euo pipefail

echo "\n[info] Hostname and time:" && hostname && date

PROJECT_DIR="/home/${USER}/StructuredDocs"
if [[ ! -d "${PROJECT_DIR}" ]]; then
  echo "[error] Project directory not found: ${PROJECT_DIR}" >&2
  exit 1
fi

cd "${PROJECT_DIR}"
echo "\n[info] PWD: $(pwd)"

echo "\n[info] Python version:" && python3 --version || true

echo "\n[info] sys.path (first 5):"
python3 - <<'PY'
#!/usr/bin/env bash
# Legacy placeholder script.

set -euo pipefail

echo "This helper no longer performs any actions. Consult the deployment documentation instead."
echo "\n[info] Git status (if repo exists on server):"
if [[ -d .git ]]; then
  git --no-pager log --oneline -n 3 || true
  git --no-pager status || true
else
  echo "(no .git directory present)"
fi

echo "\n[done] Diagnosis complete."
REMOTE

