#!/usr/bin/env bash
set -euo pipefail

# Simple Docker deploy: build multi-stage image and run via compose prod file.
# Usage:
#  ./deploy_docker.sh                # build and up -d
#  ./deploy_docker.sh --rebuild      # force no-cache rebuild
#  ./deploy_docker.sh --down         # stop and remove

REBUILD=0
DOWN=0
for arg in "$@"; do
  case "$arg" in
    --rebuild) REBUILD=1 ;;
    --down) DOWN=1 ;;
  esac
done

if [[ $DOWN -eq 1 ]]; then
  echo "Stopping and removing containers..."
  docker compose -f docker-compose.base.yml -f docker-compose.prod.yml down
  exit 0
fi

if [[ $REBUILD -eq 1 ]]; then
  echo "Building image without cache..."
  docker compose -f docker-compose.base.yml -f docker-compose.prod.yml build --no-cache
else
  echo "Building image (with cache)..."
  docker compose -f docker-compose.base.yml -f docker-compose.prod.yml build
fi

echo "Starting containers..."
docker compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d

echo "Waiting for app to become healthy..."
sleep 3
docker compose -f docker-compose.base.yml -f docker-compose.prod.yml ps

echo "Done. App should be reachable on port 8080 of this host."
