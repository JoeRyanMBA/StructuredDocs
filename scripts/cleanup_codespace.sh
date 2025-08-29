#!/usr/bin/env bash
set -euo pipefail

# Safe cleanup tool for this Codespace
# - Supports --dry-run (default) and --yes (no prompts)
# - Groups deletions by category with clear prompts
# - Only removes files within the repo root

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

DRY_RUN=1
ASSUME_YES=0

usage() {
  cat <<EOF
Usage: $(basename "$0") [--dry-run] [--yes]

Options:
  --dry-run   Preview actions without deleting (default)
  --yes       Do not prompt; proceed with deletions for default-safe categories

Categories cleaned (with prompts):
  - Build/package artifacts (*.tar.gz)
  - Temp/workspace folders (tmp/, .workspace_tmp/)
  - Redundant virtualenv (backend_venv/)
  - Frontend dist backups (frontend/dist_backup/)
  - Local SQLite databases (backend/knowledge_base.db, instance/structured_docs.db) [optional]
  - Root-level Alembic migrations (migrations/) if backend/migrations exists [optional]
  - node_modules/ [optional]

Always review with --dry-run before using --yes.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift;;
    --yes) DRY_RUN=0; ASSUME_YES=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 1;;
  esac
done

confirm() {
  local prompt="$1"
  if [[ "$ASSUME_YES" -eq 1 ]]; then
    return 0
  fi
  read -r -p "$prompt [y/N] " ans || true
  [[ "${ans:-}" =~ ^[Yy]$ ]]
}

delete_path() {
  local p="$1"
  if [[ ! -e "$p" ]]; then return 0; fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "[DRY-RUN] Would remove: $p"
  else
    echo "Removing: $p"
    rm -rf -- "$p"
  fi
}

echo "Repo root: $ROOT_DIR"
echo "Mode: $([[ $DRY_RUN -eq 1 ]] && echo DRY-RUN || echo LIVE)"

# 1) Build/package artifacts
ARTIFACTS=(
  "backend_package.tar.gz"
  "frontend_package.tar.gz"
  "frontend_deploy_*.tar.gz"
  "backend_clean_*.tar.gz"
)
FOUND=()
for pat in "${ARTIFACTS[@]}"; do
  while IFS= read -r -d '' f; do FOUND+=("$f"); done < <(find . -maxdepth 1 -type f -name "$pat" -print0 2>/dev/null || true)
done
if [[ ${#FOUND[@]} -gt 0 ]]; then
  echo "Found package artifacts:"; printf '  %s\n' "${FOUND[@]}"
  if confirm "Remove these package archives?"; then
    for f in "${FOUND[@]}"; do delete_path "$f"; done
  fi
fi

# 2) Temp/workspace folders
for d in "tmp" ".workspace_tmp"; do
  if [[ -e "$d" ]]; then
    if confirm "Remove temp folder '$d'?"; then delete_path "$d"; fi
  fi
done

# 3) Redundant venv (prefer single .venv at root)
if [[ -d "backend_venv" ]]; then
  if confirm "Remove redundant virtualenv 'backend_venv'?"; then delete_path "backend_venv"; fi
fi

# 4) Frontend dist backups
if [[ -d "frontend/dist_backup" ]]; then
  if confirm "Remove 'frontend/dist_backup'?"; then delete_path "frontend/dist_backup"; fi
fi

# 5) Optional: Local SQLite DB files (safe if using Postgres only)
DB_FILES=(
  "backend/knowledge_base.db"
  "instance/structured_docs.db"
  "backend/instance/structured_docs.db"
)
DB_FOUND=()
for f in "${DB_FILES[@]}"; do [[ -f "$f" ]] && DB_FOUND+=("$f"); done
if [[ ${#DB_FOUND[@]} -gt 0 ]]; then
  echo "Found local SQLite DB files:"; printf '  %s\n' "${DB_FOUND[@]}"
  if confirm "Remove these SQLite files (recommended if using Postgres)?"; then
    for f in "${DB_FOUND[@]}"; do delete_path "$f"; done
  fi
fi

# 6) Optional: root-level Alembic 'migrations' if backend/migrations exists
if [[ -d "migrations" && -d "backend/migrations" ]]; then
  echo "Both root 'migrations/' and 'backend/migrations/' exist."
  if confirm "Remove root 'migrations/' (backend/migrations is canonical)?"; then delete_path "migrations"; fi
fi

# 7) Optional: node_modules (reinstall with npm ci)
if [[ -d "node_modules" ]]; then
  if confirm "Remove 'node_modules' (you can restore with 'npm ci')?"; then delete_path "node_modules"; fi
fi

echo "Cleanup complete."
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "This was a dry run. Re-run with --yes to apply deletions."
fi
