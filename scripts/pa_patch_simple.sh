#!/usr/bin/env bash

# Simple WSGI patcher for PythonAnywhere
# Usage: ./pa_patch_simple.sh [PA_USER] [WSGI_PATH] [MODULE] [FUNC]

set -euo pipefail

PA_USER="${1:-JoeRyanMBA}"
WSGI_PATH="${2:-/var/www/structureddocs_joe-ryan_mba_wsgi.py}"
MODULE="${3:-app_final_with_notifications_fix}"
FUNC="${4:-create_app}"
PA_HOST="ssh.pythonanywhere.com"

echo "=== 📝 Simple WSGI Patch: ${WSGI_PATH} -> ${MODULE}:${FUNC} ==="

# Create a temporary patch script
cat > /tmp/patch_wsgi.py <<EOF
import sys, re

path = "$WSGI_PATH"
mod = "$MODULE"
func = "$FUNC"

print(f"Patching {path} to use {mod}:{func}")

src = open(path, 'r', encoding='utf-8').read()
print("Original content (first 200 chars):")
print(repr(src[:200]))

# Replace backend.app import if present
src = re.sub(r"from\s+backend\.app\s+import\s+create_app", f"from {mod} import {func}", src)

# Ensure import exists
if f"from {mod} import {func}" not in src:
    lines = src.splitlines()
    # Insert after sys.path setup
    insert_idx = 0
    for i, line in enumerate(lines):
        if 'sys.path' in line or 'project_home' in line:
            insert_idx = i + 1
        elif line.strip() and not line.strip().startswith('#'):
            break
    lines.insert(insert_idx, f"from {mod} import {func}")
    src = "\n".join(lines)

# Replace application assignment
src = re.sub(r"application\s*=\s*create_app\(\)", f"application = {func}()", src)

open(path, 'w', encoding='utf-8').write(src)
print(f"Patched {path}")
EOF

# Upload and run the patch script
scp /tmp/patch_wsgi.py "${PA_USER}@${PA_HOST}:/tmp/"
ssh "${PA_USER}@${PA_HOST}" "python3 /tmp/patch_wsgi.py && rm /tmp/patch_wsgi.py"

echo "✅ WSGI patched successfully"
