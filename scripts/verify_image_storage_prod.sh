#!/usr/bin/env bash
set -euo pipefail

HOST=${1:-}
USER_NAME=${2:-root}

if [[ -z "${HOST}" ]]; then
  echo "Usage: $0 <host-or-ip> [user]"
  exit 1
fi

SSH_OPTS=(
  -o StrictHostKeyChecking=accept-new
  -o ConnectTimeout=12
)

ssh "${SSH_OPTS[@]}" "${USER_NAME}@${HOST}" 'bash -s' <<'REMOTE'
set -euo pipefail

echo "=== Host ==="
hostname
uname -a

echo "=== Docker Containers ==="
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

APP_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "structureddocs|app" | head -n1 || true)
if [[ -z "$APP_CONTAINER" ]]; then
  echo "No app container found"
  exit 1
fi

echo "Using container: $APP_CONTAINER"

echo "=== App Env in Container ==="
docker exec "$APP_CONTAINER" sh -lc 'echo IMAGE_STORAGE_ROOT=$IMAGE_STORAGE_ROOT; echo ENABLE_BLUEPRINTS=$ENABLE_BLUEPRINTS; echo ENABLE_BLUEPRINTS_FILE=$ENABLE_BLUEPRINTS_FILE; echo FRONTEND_URL=$FRONTEND_URL; echo PORT=$PORT'

echo "=== Blueprint File ==="
docker exec "$APP_CONTAINER" sh -lc 'ls -la /app/.enable_blueprints; cat /app/.enable_blueprints'

echo "=== Storage Paths ==="
docker exec "$APP_CONTAINER" sh -lc '
  echo "-- /app/data/images --"; ls -la /app/data/images 2>/dev/null || true;
  echo "-- /app/data/images/imports --"; ls -la /app/data/images/imports 2>/dev/null || true;
  echo "-- /app/backend/static/images --"; ls -la /app/backend/static/images 2>/dev/null || true;
  echo "-- /app/backend/static/images/imports --"; ls -la /app/backend/static/images/imports 2>/dev/null || true;
'

echo "=== Check doc folder 114 ==="
docker exec "$APP_CONTAINER" sh -lc '
  for p in /app/data/images/imports/114 /app/backend/static/images/imports/114 /app/frontend/public/images/imports/114; do
    echo "PATH: $p";
    if [ -d "$p" ]; then ls -la "$p" | head -n 40; else echo "(missing)"; fi;
  done
'

echo "=== API checks from inside container ==="
docker exec "$APP_CONTAINER" sh -lc '
  set -e
  (curl -sS -I http://127.0.0.1:8080/api/health || true) | head -n 5
  (curl -sS http://127.0.0.1:8080/api/images | head -c 400; echo) || true
  (curl -sS -I http://127.0.0.1:8080/images/imports/114/image64_98638151.png || true) | head -n 10
'

echo "=== Recent image logs (if available) ==="
docker logs --tail 200 "$APP_CONTAINER" 2>&1 | grep -E "Image request|Image not found|/images/imports/114|IMAGE_STORAGE_ROOT" || true
REMOTE
