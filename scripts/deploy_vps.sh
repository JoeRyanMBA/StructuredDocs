#!/bin/bash
# Provider-neutral wrapper for environment deployments to a VPS.
# Usage:
#   ./scripts/deploy_vps.sh <test|training|production> [server-ip]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/deploy.sh" "$@"
