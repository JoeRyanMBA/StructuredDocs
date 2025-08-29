#!/usr/bin/env bash

# Update PythonAnywhere WSGI file(s) to import the desired Flask app entrypoint.
# Default target: from app_final_with_notifications_fix import create_app
# Usage: ./scripts/pa_update_wsgi_app.sh [PA_USER] [MODULE:FUNC]

set -euo pipefail

PA_USER="${1:-JoeRyanMBA}"
TARGET_IMPORT="${2:-app_final_with_notifications_fix:create_app}"
# Optional explicit WSGI file path (e.g., /var/www/structureddocs_joe-ryan_mba_wsgi.py)
WSGI_PATH_OVERRIDE="${3:-}"
PA_HOST="ssh.pythonanywhere.com"

MODULE_NAME="${TARGET_IMPORT%%:*}"
FUNC_NAME="${TARGET_IMPORT##*:}"

echo "=== 📝 Updating WSGI to use ${MODULE_NAME}:${FUNC_NAME} for ${PA_USER}@${PA_HOST} ==="

ssh "${PA_USER}@${PA_HOST}" bash -s -- "${MODULE_NAME}" "${FUNC_NAME}" "${WSGI_PATH_OVERRIDE}" <<'REMOTE'
set -e

TARGET_MODULE="${1:-}"
TARGET_FUNC="${2:-}"
WSGI_FILE="${3:-}"

if [[ -z "${WSGI_FILE}" ]]; then
  WSGI_FILE=
  for w in /var/www/*wsgi.py; do
    if [[ -e "\$w" ]]; then WSGI_FILE="\$w"; break; fi
  done
fi

if [[ -z "\$WSGI_FILE" || ! -f "\$WSGI_FILE" ]]; then
  echo "No WSGI file found" >&2
  exit 1
fi

echo "-- Using WSGI: \$WSGI_FILE"
head -n 30 "\$WSGI_FILE" | sed -n '1,30p'

ts=\$(date +%Y%m%d_%H%M%S)
cp -a "\$WSGI_FILE" "\$WSGI_FILE.bak_\$ts"

python3 - "\$WSGI_FILE" "\$TARGET_MODULE" "\$TARGET_FUNC" <<'PY'
import sys, re
path, mod, func = sys.argv[1:4]
src = open(path, 'r', encoding='utf-8').read()

# 1) Replace specific backend.app import if present
src, n1 = re.subn(r"from\s+backend\.app\s+import\s+create_app", f"from {mod} import {func}", src, count=1)

# 2) Ensure we import target if not already present
if not re.search(rf"from\s+{re.escape(mod)}\s+import\s+{re.escape(func)}", src):
    lines = src.splitlines()
    # insert after shebang and docstring/comments
    insert_idx = 0
    for i, line in enumerate(lines[:50]):
        if line.startswith('#!') or line.strip().startswith('"""') or line.strip().startswith("'''") or not line.strip() or line.strip().startswith('#'):
            insert_idx = i + 1
            continue
        insert_idx = i + 1
        break
    lines.insert(insert_idx, f"from {mod} import {func}")
    src = "\n".join(lines)

# 3) Normalize application assignment to use target factory
patterns = [
    r"application\s*=\s*create_app\(\)",
    r"application\s*=\s*[A-Za-z_][A-Za-z0-9_]*\(\)",
    r"application\s*=\s*[A-Za-z_][A-Za-z0-9_]*",
]
replaced = False
for pat in patterns:
    new_src, n = re.subn(pat, f"application = {func}()", src, count=1)
    if n:
        src = new_src
        replaced = True
        break

if not replaced:
    src += f"\n\n# Injected by pa_update_wsgi_app.sh\napplication = {func}()\n"

open(path, 'w', encoding='utf-8').write(src)
print("Patched:", path)
PY

echo "Done patching WSGI file."
REMOTE

echo "Tip: run ./scripts/pa_reload.sh to apply changes."
