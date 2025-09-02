#!/bin/bash
# Comprehensive build and deployment script
set -e  # Exit on any error

echo "🚀 Starting StructuredDocs Build Process"
echo "========================================"

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

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -f "requirements.txt" ]; then
    print_error "Not in the correct project directory"
    exit 1
fi

print_status "Project directory verified"

# Build frontend
echo ""
echo "🔧 Building Frontend..."
cd frontend

if [ ! -f "package.json" ]; then
    print_error "Frontend package.json not found"
    exit 1
fi

# Clean install dependencies
rm -rf node_modules package-lock.json
npm install

# Build the application
npm run build

# Verify build output
if [ ! -f "dist/index.html" ]; then
    print_error "Frontend build failed - index.html not found"
    exit 1
fi

if [ ! -d "dist/assets" ]; then
    print_error "Frontend build failed - assets directory not found"
    exit 1
fi

ASSET_COUNT=$(ls dist/assets/ | wc -l)
print_status "Frontend built successfully with $ASSET_COUNT assets"

cd ..
print_status "Frontend build completed"

# Verify Python environment
echo ""
echo "🐍 Verifying Python Environment..."
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    exit 1
fi

if [ ! -f ".enable_blueprints" ]; then
    print_error ".enable_blueprints file not found"
    exit 1
fi

print_status "Python environment verified"

# Build Docker image
echo ""
echo "🐳 Building Docker Image..."
docker build -t structureddocs:latest .

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Test the container locally (optional)
echo ""
read -p "🧪 Test container locally? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing container..."
    docker run -d --name structureddocs-test -p 8080:8080 structureddocs:latest
    sleep 10

    if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
        print_status "Container health check passed"
        docker stop structureddocs-test
        docker rm structureddocs-test
    else
        print_error "Container health check failed"
        docker logs structureddocs-test
        docker stop structureddocs-test
        docker rm structureddocs-test
        exit 1
    fi
fi

echo ""
print_status "Build process completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Push to GitHub: git add . && git commit -m 'Build update' && git push"
echo "2. DigitalOcean will automatically deploy"
echo "3. Monitor deployment at: https://structureddocs-srhab.ondigitalocean.app"
echo ""
echo "🔍 To check deployment status:"
echo "   curl https://structureddocs-srhab.ondigitalocean.app/api/health"
