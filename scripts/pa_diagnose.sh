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
import sys
print("\n".join(sys.path[:10]))
PY

echo "\n[info] Listing key paths:"
ls -la . | sed -n '1,50p'
ls -la backend | sed -n '1,200p' || true

echo "\n[info] Show recent mtimes for backend files:"
find backend -type f -maxdepth 2 -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\n' | sort -r | head -n 25 || true

echo "\n[info] Check for .env and important config files:"
for f in .env wsgi.py pythonanywhere_wsgi_content.py app_final.py app_final_with_notifications_fix.py; do
  if [[ -f "${f}" ]]; then
    echo "found: ${f}"
  else
    echo "missing: ${f}"
  fi
done

echo "\n[info] Try to import the Flask app (non-fatal):"
python3 - <<'PY'
try:
    from app_final_with_notifications_fix import create_app
    app = create_app()
    print("Flask app import OK from app_final_with_notifications_fix")
except Exception as e:
    print("Import from app_final_with_notifications_fix failed:", e)
    try:
        import importlib.util, os, sys
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
        from app import create_app as create_backend_app
        app = create_backend_app()
        print("Flask app import OK from backend/app.py")
    except Exception as e2:
        print("Import from backend/app.py failed:", e2)
PY

echo "\n[info] Attempt to locate WSGI file(s):"
for w in /var/www/*wsgi.py; do
  [[ -e "$w" ]] || continue
  echo "--- ${w} (head) ---"
  sed -n '1,80p' "$w" || true
done

echo "\n[info] SQLite files present (if any):"
find . -maxdepth 2 -name '*.db' -printf '%p (%s bytes)\n' || true

echo "\n[info] Git status (if repo exists on server):"
if [[ -d .git ]]; then
  git --no-pager log --oneline -n 3 || true
  git --no-pager status || true
else
  echo "(no .git directory present)"
fi

echo "\n[done] Diagnosis complete."
REMOTE

