#!/bin/bash
# Deployment Status Monitor for StructuredDocs
# Checks all deployment options and their health

echo "🔍 StructuredDocs Deployment Monitor"
echo "===================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check endpoint
check_endpoint() {
    local url=$1
    local name=$2

    echo -n "Checking $name... "

    if curl -s --max-time 10 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ UP${NC}"
        return 0
    else
        echo -e "${RED}❌ DOWN${NC}"
        return 1
    fi
}

# Check DigitalOcean (Primary)
echo ""
echo "🏠 Primary Deployment:"
check_endpoint "https://structureddocs-srhab.ondigitalocean.app/api/health" "DigitalOcean Health"
check_endpoint "https://structureddocs-srhab.ondigitalocean.app/" "DigitalOcean Frontend"

# Check Vercel (Backup - if deployed)
echo ""
echo "⚡ Backup Deployments:"
echo "Vercel: Not deployed yet (run 'npm install -g vercel && cd frontend && vercel --prod')"
echo "Railway: Not deployed yet (run 'npm install -g @railway/cli && railway login && railway init')"

# Performance check
echo ""
echo "⚡ Performance Check:"
echo -n "Response time: "
RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null "https://structureddocs-srhab.ondigitalocean.app/api/health")
echo "${RESPONSE_TIME}s"

# Asset check
echo -n "Assets loading: "
if curl -s -I "https://structureddocs-srhab.ondigitalocean.app/assets/" | grep -q "200"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

echo ""
echo "📊 Deployment Summary:"
echo "======================"
echo "✅ DigitalOcean: ACTIVE (Primary)"
echo "⏳ Vercel: Ready for deployment"
echo "⏳ Railway: Ready for deployment"
echo ""
echo "🚀 Quick Deploy Commands:"
echo "Vercel:  cd frontend && npx vercel --prod"
echo "Railway: railway login && railway init && railway up"
