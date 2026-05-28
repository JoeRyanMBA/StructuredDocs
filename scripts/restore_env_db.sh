#!/usr/bin/env bash
# Restore DATABASE_URL for one single-VPS environment stack from a pg_dump custom file.
#
# Usage:
#   ./scripts/restore_env_db.sh --env test --file /opt/structureddocs/test/backups/test_*.dump

set -euo pipefail

BASE_DIR="/opt/structureddocs"
ENV_NAME=""
DUMP_FILE=""

usage() {
  cat <<'USAGE'
Usage: restore_env_db.sh --env <test|training|production> --file <backup.dump> [options]

Options:
  --env <name>       Environment name (required)
  --file <path>      Backup file created by pg_dump --format=custom (required)
  --base-dir <path>  Base directory (default: /opt/structureddocs)
  --yes              Skip confirmation prompt
USAGE
}

ASSUME_YES=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="$2"
      shift 2
      ;;
    --file)
      DUMP_FILE="$2"
      shift 2
      ;;
    --base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    --yes)
      ASSUME_YES=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$ENV_NAME" != "test" && "$ENV_NAME" != "training" && "$ENV_NAME" != "production" ]]; then
  echo "--env must be one of: test, training, production" >&2
  exit 1
fi

if [[ -z "$DUMP_FILE" || ! -f "$DUMP_FILE" ]]; then
  echo "--file must point to an existing dump file" >&2
  exit 1
fi

if ! command -v pg_restore >/dev/null 2>&1; then
  echo "pg_restore is required (install postgresql-client)" >&2
  exit 1
fi

ENV_DIR="$BASE_DIR/$ENV_NAME"
ENV_FILE="$ENV_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

DATABASE_URL="$(grep -E '^DATABASE_URL=' "$ENV_FILE" | tail -n1 | sed 's/^DATABASE_URL=//')"
if [[ -z "$DATABASE_URL" ]]; then
  echo "DATABASE_URL missing in $ENV_FILE" >&2
  exit 1
fi

if [[ "$ASSUME_YES" -ne 1 ]]; then
  echo "This will DROP and recreate objects in the '$ENV_NAME' database from: $DUMP_FILE"
  read -r -p "Type 'restore' to continue: " confirm
  if [[ "$confirm" != "restore" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

echo "Restoring $ENV_NAME database from $DUMP_FILE"
PGCONNECT_TIMEOUT=10 pg_restore --clean --if-exists --no-owner --no-privileges --dbname="$DATABASE_URL" "$DUMP_FILE"

echo "Restore complete."
