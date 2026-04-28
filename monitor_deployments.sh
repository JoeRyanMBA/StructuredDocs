#!/bin/bash
# Deployment Status Monitor for StructuredDocs
# Checks the configured app URL and optional frontend URL.

set -euo pipefail

APP_URL="${APP_URL:-https://your-app-url}"
FRONTEND_URL="${FRONTEND_URL:-}"

echo "🔍 StructuredDocs Deployment Monitor"
echo "===================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check_endpoint() {
    local url=$1
    local name=$2

    echo -n "Checking $name... "
    if curl -fsS --max-time 10 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ UP${NC}"
    else
        echo -e "${RED}❌ DOWN${NC}"
    fi
}

echo ""
echo "🏠 App deployment:"
check_endpoint "${APP_URL%/}/api/health" "App health"

echo ""
echo "⚡ Performance Check:"
echo -n "Response time: "
curl -s -w "%{time_total}s\n" -o /dev/null "${APP_URL%/}/api/health"

if [[ -n "$FRONTEND_URL" ]]; then
    echo ""
    echo "🖥️ Frontend deployment:"
    check_endpoint "${FRONTEND_URL%/}/" "Frontend"
fi

echo ""
echo "💡 Configure APP_URL and FRONTEND_URL before running this script for your environment."
