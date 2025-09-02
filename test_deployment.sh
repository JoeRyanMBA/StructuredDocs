#!/bin/bash
# Deployment Test Script for StructuredDocs
# Tests the current Docker setup and provides alternatives

set -e

echo "🔍 StructuredDocs Deployment Test"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test 1: Check if required files exist
echo "1. Checking required files..."
if [ -f "Dockerfile" ]; then
    print_status "Dockerfile exists"
else
    print_error "Dockerfile missing"
    exit 1
fi

if [ -f "frontend/package.json" ]; then
    print_status "Frontend package.json exists"
else
    print_error "Frontend package.json missing"
    exit 1
fi

if [ -f "requirements.txt" ]; then
    print_status "Python requirements.txt exists"
else
    print_error "Python requirements.txt missing"
    exit 1
fi

# Test 2: Check frontend build
echo ""
echo "2. Testing frontend build..."
cd frontend
if npm run build 2>/dev/null; then
    print_status "Frontend build successful"
    if [ -d "dist/assets" ]; then
        print_status "Assets directory created"
        ASSET_COUNT=$(find dist/assets -name "*.js" -o -name "*.css" | wc -l)
        echo "   Found $ASSET_COUNT asset files"
    else
        print_error "Assets directory not found after build"
    fi
else
    print_error "Frontend build failed"
fi
cd ..

# Test 3: Check Docker build
echo ""
echo "3. Testing Docker build..."
if docker build -t structureddocs:test . 2>/dev/null; then
    print_status "Docker build successful"
else
    print_error "Docker build failed"
    echo "   Trying with no cache..."
    if docker build --no-cache -t structureddocs:test .; then
        print_status "Docker build successful (no cache)"
    else
        print_error "Docker build still failed"
    fi
fi

# Test 4: Check if container has assets
echo ""
echo "4. Testing asset copying in container..."
CONTAINER_ID=$(docker run -d structureddocs:test sleep 10)
if [ $? -eq 0 ]; then
    print_status "Container started successfully"
    if docker exec $CONTAINER_ID ls -la frontend/dist/assets/ 2>/dev/null; then
        print_status "Assets found in container"
        ASSET_COUNT_CONTAINER=$(docker exec $CONTAINER_ID find frontend/dist/assets -name "*.js" -o -name "*.css" | wc -l)
        echo "   Container has $ASSET_COUNT_CONTAINER asset files"
    else
        print_error "Assets not found in container"
    fi
    docker stop $CONTAINER_ID >/dev/null
    docker rm $CONTAINER_ID >/dev/null
else
    print_error "Failed to start container"
fi

# Test 5: Alternative deployment check
echo ""
echo "5. Checking alternative deployment options..."
if command -v vercel &> /dev/null; then
    print_status "Vercel CLI available"
else
    print_warning "Vercel CLI not installed (npm install -g vercel)"
fi

if command -v railway &> /dev/null; then
    print_status "Railway CLI available"
else
    print_warning "Railway CLI not installed (npm install -g @railway/cli)"
fi

# Summary
echo ""
echo "📊 Test Summary:"
echo "================"

if [ -d "frontend/dist/assets" ] && docker images | grep -q structureddocs; then
    print_status "Current Docker setup appears functional"
    echo "   Next: Run './build-deploy.sh' to deploy"
else
    print_warning "Issues found with current setup"
    echo "   Consider using Vercel as backup:"
    echo "   cd frontend && npm run build && npx vercel --prod"
fi

echo ""
echo "🔗 Useful commands:"
echo "==================="
echo "Deploy to DigitalOcean: ./build-deploy.sh"
echo "Deploy to Vercel: cd frontend && npx vercel --prod"
echo "Check health: curl https://your-app-url/api/health"
echo "View logs: docker logs <container_id>"
