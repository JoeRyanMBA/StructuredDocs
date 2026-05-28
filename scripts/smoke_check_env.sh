#!/usr/bin/env bash
# Lightweight smoke test for a StructuredDocs environment URL.
#
# Usage:
#   ./scripts/smoke_check_env.sh http://127.0.0.1:18080

set -euo pipefail

BASE_URL="${1:-}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-20}"

if [[ -z "$BASE_URL" ]]; then
  echo "Usage: $0 <base-url>" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required" >&2
  exit 1
fi

trimmed_base="${BASE_URL%/}"

assert_get_ok() {
  local path="$1"
  local url="${trimmed_base}${path}"
  local code
  code="$(curl -sS -m "$TIMEOUT_SECONDS" -o /tmp/smoke_body.$$ -w "%{http_code}" "$url" || true)"
  if [[ "$code" != "200" ]]; then
    echo "FAIL: GET ${path} returned HTTP ${code}" >&2
    cat /tmp/smoke_body.$$ >&2 || true
    rm -f /tmp/smoke_body.$$
    return 1
  fi
  rm -f /tmp/smoke_body.$$
  echo "OK: GET ${path}"
}

assert_contains() {
  local path="$1"
  local expected="$2"
  local url="${trimmed_base}${path}"
  local body
  body="$(curl -sS -m "$TIMEOUT_SECONDS" "$url")"
  if [[ "$body" != *"$expected"* ]]; then
    echo "FAIL: ${path} did not contain expected text: ${expected}" >&2
    echo "$body" >&2
    return 1
  fi
  echo "OK: ${path} contains '${expected}'"
}

assert_get_ok "/api/health"
assert_get_ok "/api/version"
assert_contains "/api/version" "StructuredDocs"
assert_get_ok "/"

echo "Smoke checks passed for ${trimmed_base}"
