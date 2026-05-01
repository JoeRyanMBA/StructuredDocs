#!/bin/bash
# Provider-neutral wrapper for bootstrapping a new server.
# Usage:
#   ./scripts/setup_server.sh <test|training|production>
#   ssh root@SERVER_IP 'bash -s' < scripts/setup_server.sh production

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/setup_droplet.sh" "$@"
