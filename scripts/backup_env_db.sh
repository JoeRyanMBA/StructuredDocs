#!/usr/bin/env bash
# Backup DATABASE_URL for one single-VPS environment stack.
#
# Usage:
#   ./scripts/backup_env_db.sh --env dev --base-dir /opt/structureddocs

set -euo pipefail

BASE_DIR="/opt/structureddocs"
ENV_NAME=""
OUT_DIR=""

usage() {
  cat <<'USAGE'
Usage: backup_env_db.sh --env <dev|staging|production> [options]

Options:
  --env <name>       Environment name (required)
  --base-dir <path>  Base directory (default: /opt/structureddocs)
  --out-dir <path>   Output directory (default: <env-dir>/backups)
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="$2"
      shift 2
      ;;
    --base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
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

if [[ "$ENV_NAME" == "test" ]]; then
  ENV_NAME="staging"
elif [[ "$ENV_NAME" == "training" ]]; then
  ENV_NAME="dev"
fi

if [[ "$ENV_NAME" != "dev" && "$ENV_NAME" != "staging" && "$ENV_NAME" != "production" ]]; then
  echo "--env must be one of: dev, staging, production" >&2
  exit 1
fi

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump is required (install postgresql-client)" >&2
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

if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$ENV_DIR/backups"
fi
mkdir -p "$OUT_DIR"

ts="$(date -u +%Y%m%dT%H%M%SZ)"
out_file="$OUT_DIR/${ENV_NAME}_${ts}.dump"

echo "Backing up $ENV_NAME database to $out_file"
PGCONNECT_TIMEOUT=10 pg_dump --format=custom --file="$out_file" "$DATABASE_URL"

echo "Backup complete: $out_file"
