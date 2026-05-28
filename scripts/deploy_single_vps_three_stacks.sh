#!/usr/bin/env bash
# Deploy Single VPS three-stack environments in promotion order with health checks.
#
# Default order: dev -> staging -> production
# Stops immediately on first failure.
#
# Usage examples:
#   ./scripts/deploy_single_vps_three_stacks.sh
#   ./scripts/deploy_single_vps_three_stacks.sh --base-dir /opt/structureddocs --pull
#   ./scripts/deploy_single_vps_three_stacks.sh --start-env staging --stop-after production
#   ./scripts/deploy_single_vps_three_stacks.sh --env production --no-build

set -euo pipefail

BASE_DIR="/opt/structureddocs"
HEALTH_ENDPOINT="/api/health"
HEALTH_TIMEOUT=120
PULL_FIRST=0
NO_BUILD=0
SKIP_HEALTH=0
SKIP_SMOKE=0
START_ENV="dev"
STOP_AFTER="production"
SINGLE_ENV=""
IMAGE_TAG=""
IMAGE_REPO=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMOKE_SCRIPT_DEFAULT="$SCRIPT_DIR/smoke_check_env.sh"
SMOKE_SCRIPT="$SMOKE_SCRIPT_DEFAULT"

# Override ports if your deployment does not use defaults.
DEV_PORT="${DEV_PORT:-${TRAINING_PORT:-18080}}"
STAGING_PORT="${STAGING_PORT:-${TEST_PORT:-28080}}"
PRODUCTION_PORT="${PRODUCTION_PORT:-38080}"

usage() {
  cat <<'USAGE'
Usage: deploy_single_vps_three_stacks.sh [options]

Options:
  --base-dir <path>        Base directory containing dev/staging/production stacks
                           (default: /opt/structureddocs)
  --env <name>             Deploy only one environment: dev|staging|production
  --start-env <name>       Start promotion sequence at: dev|staging|production
                           (default: dev)
  --stop-after <name>      Stop promotion sequence after: dev|staging|production
                           (default: production)
  --pull                   Run docker compose pull before up
  --no-build               Do not use --build on docker compose up
  --skip-health            Skip health endpoint checks
  --skip-smoke             Skip smoke script execution
  --smoke-script <path>    Smoke script path (default: scripts/smoke_check_env.sh)
  --image-tag <tag>        Promote immutable image tag across all target environments
  --image-repo <repo>      Image repository override when using --image-tag
  --health-endpoint <path> Health endpoint path (default: /api/health)
  --health-timeout <sec>   Max wait time per env health check (default: 120)
  -h, --help               Show help

Environment variable overrides for ports:
  DEV_PORT, STAGING_PORT, PRODUCTION_PORT
  Legacy aliases also supported: TEST_PORT, TRAINING_PORT
USAGE
}

is_valid_env() {
  [[ "$1" == "dev" || "$1" == "staging" || "$1" == "production" || "$1" == "test" || "$1" == "training" ]]
}

normalize_env_name() {
  case "$1" in
    test)
      echo "staging"
      ;;
    training)
      echo "dev"
      ;;
    *)
      echo "$1"
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    --env)
      SINGLE_ENV="$2"
      shift 2
      ;;
    --start-env)
      START_ENV="$2"
      shift 2
      ;;
    --stop-after)
      STOP_AFTER="$2"
      shift 2
      ;;
    --pull)
      PULL_FIRST=1
      shift
      ;;
    --no-build)
      NO_BUILD=1
      shift
      ;;
    --skip-health)
      SKIP_HEALTH=1
      shift
      ;;
    --skip-smoke)
      SKIP_SMOKE=1
      shift
      ;;
    --smoke-script)
      SMOKE_SCRIPT="$2"
      shift 2
      ;;
    --image-tag)
      IMAGE_TAG="$2"
      shift 2
      ;;
    --image-repo)
      IMAGE_REPO="$2"
      shift 2
      ;;
    --health-endpoint)
      HEALTH_ENDPOINT="$2"
      shift 2
      ;;
    --health-timeout)
      HEALTH_TIMEOUT="$2"
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

if ! [[ "$HEALTH_TIMEOUT" =~ ^[0-9]+$ ]]; then
  echo "--health-timeout must be an integer number of seconds" >&2
  exit 1
fi

if [[ -n "$SINGLE_ENV" ]]; then
  SINGLE_ENV="$(normalize_env_name "$SINGLE_ENV")"
  if ! is_valid_env "$SINGLE_ENV"; then
    echo "Invalid --env value: $SINGLE_ENV" >&2
    exit 1
  fi
fi

START_ENV="$(normalize_env_name "$START_ENV")"
if ! is_valid_env "$START_ENV"; then
  echo "Invalid --start-env value: $START_ENV" >&2
  exit 1
fi

STOP_AFTER="$(normalize_env_name "$STOP_AFTER")"
if ! is_valid_env "$STOP_AFTER"; then
  echo "Invalid --stop-after value: $STOP_AFTER" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required but not found in PATH" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required but not found in PATH" >&2
  exit 1
fi

if [[ "$SKIP_SMOKE" -ne 1 ]]; then
  if [[ ! -x "$SMOKE_SCRIPT" ]]; then
    echo "Smoke script is not executable or missing: $SMOKE_SCRIPT" >&2
    echo "Use --skip-smoke or provide --smoke-script <path>" >&2
    exit 1
  fi
fi

if [[ -n "$IMAGE_TAG" ]]; then
  PULL_FIRST=1
  NO_BUILD=1
fi

declare -a ALL_ENVS=(dev staging production)
declare -A PORT_BY_ENV=(
  [dev]="$DEV_PORT"
  [staging]="$STAGING_PORT"
  [production]="$PRODUCTION_PORT"
)

deploy_env() {
  local env_name="$1"
  local env_dir="$BASE_DIR/$env_name"
  local env_file="$env_dir/.env"
  local compose_file="$env_dir/docker-compose.single.yml"
  local port="${PORT_BY_ENV[$env_name]}"
  local project_name="structureddocs_${env_name}"

  echo ""
  echo "===== Deploying $env_name ====="
  echo "Directory: $env_dir"
  echo "Project:   $project_name"
  echo "Port:      $port"

  if [[ ! -d "$env_dir" ]]; then
    echo "Missing environment directory: $env_dir" >&2
    return 1
  fi
  if [[ ! -f "$env_file" ]]; then
    echo "Missing env file: $env_file" >&2
    return 1
  fi
  if [[ ! -f "$compose_file" ]]; then
    echo "Missing compose file: $compose_file" >&2
    return 1
  fi

  pushd "$env_dir" >/dev/null

  local -a compose_cmd=(docker compose -p "$project_name" -f "$compose_file" --env-file "$env_file")
  local -a compose_env=()
  if [[ -n "$IMAGE_TAG" ]]; then
    compose_env+=(IMAGE_TAG="$IMAGE_TAG")
  fi
  if [[ -n "$IMAGE_REPO" ]]; then
    compose_env+=(IMAGE_REPO="$IMAGE_REPO")
  fi

  if [[ "$PULL_FIRST" -eq 1 ]]; then
    echo "Pulling image updates for $env_name..."
    if [[ "${#compose_env[@]}" -gt 0 ]]; then
      env "${compose_env[@]}" "${compose_cmd[@]}" pull
    else
      "${compose_cmd[@]}" pull
    fi
  fi

  echo "Applying compose changes for $env_name..."
  if [[ "$NO_BUILD" -eq 1 ]]; then
    if [[ "${#compose_env[@]}" -gt 0 ]]; then
      env "${compose_env[@]}" "${compose_cmd[@]}" up -d
    else
      "${compose_cmd[@]}" up -d
    fi
  else
    if [[ "${#compose_env[@]}" -gt 0 ]]; then
      env "${compose_env[@]}" "${compose_cmd[@]}" up -d --build
    else
      "${compose_cmd[@]}" up -d --build
    fi
  fi

  popd >/dev/null

  if [[ "$SKIP_HEALTH" -eq 1 ]]; then
    echo "Skipping health check for $env_name"
    return 0
  fi

  local health_url="http://127.0.0.1:${port}${HEALTH_ENDPOINT}"
  local started_at
  started_at="$(date +%s)"

  echo "Checking health: $health_url (timeout ${HEALTH_TIMEOUT}s)"
  while true; do
    if curl -fsS "$health_url" >/dev/null 2>&1; then
      echo "Health check passed for $env_name"
      break
    fi

    local now elapsed
    now="$(date +%s)"
    elapsed="$((now - started_at))"
    if [[ "$elapsed" -ge "$HEALTH_TIMEOUT" ]]; then
      echo "Health check timed out for $env_name after ${HEALTH_TIMEOUT}s" >&2
      return 1
    fi
    sleep 2
  done

  if [[ "$SKIP_SMOKE" -eq 0 ]]; then
    local base_url="http://127.0.0.1:${port}"
    echo "Running smoke checks for $env_name via $base_url"
    "$SMOKE_SCRIPT" "$base_url"
  fi
}

build_target_env_list() {
  if [[ -n "$SINGLE_ENV" ]]; then
    TARGET_ENVS=("$SINGLE_ENV")
    return
  fi

  local start_idx=-1
  local stop_idx=-1

  for i in "${!ALL_ENVS[@]}"; do
    if [[ "${ALL_ENVS[$i]}" == "$START_ENV" ]]; then
      start_idx="$i"
    fi
    if [[ "${ALL_ENVS[$i]}" == "$STOP_AFTER" ]]; then
      stop_idx="$i"
    fi
  done

  if [[ "$start_idx" -lt 0 || "$stop_idx" -lt 0 || "$start_idx" -gt "$stop_idx" ]]; then
    echo "Invalid range: start=$START_ENV stop=$STOP_AFTER" >&2
    exit 1
  fi

  TARGET_ENVS=()
  for ((i=start_idx; i<=stop_idx; i++)); do
    TARGET_ENVS+=("${ALL_ENVS[$i]}")
  done
}

build_target_env_list

echo "Base directory: $BASE_DIR"
echo "Target environments: ${TARGET_ENVS[*]}"
echo "Promotion mode: stop on first failure"
if [[ -n "$IMAGE_TAG" ]]; then
  echo "Image promotion tag: $IMAGE_TAG"
  if [[ -n "$IMAGE_REPO" ]]; then
    echo "Image repository: $IMAGE_REPO"
  fi
fi

for env_name in "${TARGET_ENVS[@]}"; do
  if ! deploy_env "$env_name"; then
    echo ""
    echo "Deployment halted at $env_name (failure)." >&2
    exit 1
  fi
done

echo ""
echo "All requested environments deployed successfully: ${TARGET_ENVS[*]}"
