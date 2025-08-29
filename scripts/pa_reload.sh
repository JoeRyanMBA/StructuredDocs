#!/usr/bin/env bash

# Touch the PythonAnywhere WSGI file to trigger a reload.
# Usage: ./scripts/pa_reload.sh [PA_USER]

set -euo pipefail

PA_USER="${1:-JoeRyanMBA}"
PA_HOST="ssh.pythonanywhere.com"

echo "=== 🔁 Triggering WSGI reload for ${PA_USER} ==="

ssh "${PA_USER}@${PA_HOST}" bash -s <<'REMOTE'
set -euo pipefail
WSGI_FILE=$(ls -1 /var/www/*wsgi.py 2>/dev/null | head -n1 || true)
if [[ -z "${WSGI_FILE}" ]]; then
  echo "No WSGI file found under /var/www/" >&2
  exit 1
fi
echo "Touching: ${WSGI_FILE}"
touch "${WSGI_FILE}"
echo "Done."
REMOTE
