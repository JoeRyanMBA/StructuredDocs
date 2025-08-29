#!/usr/bin/env bash

# Safely sync backend files to PythonAnywhere using rsync over SSH.
# Requires SSH key access already configured on your machine/VS Code environment.

set -euo pipefail

REMOTE_USER="JoeRyanMBA"
REMOTE_HOST="ssh.pythonanywhere.com"
REMOTE_DIR="/home/${REMOTE_USER}/StructuredDocs"

echo "=== Sync backend -> PythonAnywhere ==="
echo "Source: $(pwd)/backend"
echo "Dest  : ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/backend/"

# Ensure remote directories exist
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}/backend/routes ${REMOTE_DIR}/backend/utils ${REMOTE_DIR}/backend/static" || true

# Rsync backend with delete protection via backup dir
BACKUP_DIR="${REMOTE_DIR}/.rsync_backups/backend_$(date +%Y%m%d_%H%M%S)"
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${BACKUP_DIR}"

rsync -avz \
  --delete \
  --backup \
  --backup-dir="${BACKUP_DIR}" \
  --exclude "__pycache__/" \
  --exclude "*.pyc" \
  backend/ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/backend/

echo "✅ Sync complete. Backup of deleted/changed files: ${BACKUP_DIR}"

echo "Reloading web app (manual step in PA UI)."
echo "Open: https://www.pythonanywhere.com/user/${REMOTE_USER}/webapps/ and click Reload."
