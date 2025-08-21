#!/bin/bash

# Production Build Script - Removes debug console.log statements
# This creates a clean production build without debug logging

echo "🧹 Creating production build without debug logs..."

# Create a temporary directory for production files
TEMP_DIR="frontend_production_temp"
mkdir -p "${TEMP_DIR}"

# Copy frontend source to temp directory
cp -r frontend/* "${TEMP_DIR}/"

# Remove console.log statements from Vue files (keeping console.error and console.warn)
echo "🔇 Removing debug console.log statements..."
find "${TEMP_DIR}/src" -name "*.vue" -type f -exec sed -i.bak '/console\.log(/d' {} +
find "${TEMP_DIR}/src" -name "*.js" -type f -exec sed -i.bak '/console\.log(/d' {} +

# Remove backup files created by sed
find "${TEMP_DIR}" -name "*.bak" -delete

echo "📦 Building production frontend..."
cd "${TEMP_DIR}"
npm install --silent
npm run build
cd ..

# Create deployment package
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="frontend_production_${TIMESTAMP}.tar.gz"
tar -czf "${PACKAGE_NAME}" -C "${TEMP_DIR}/dist" .

echo "✅ Created clean production package: ${PACKAGE_NAME}"

# Cleanup
rm -rf "${TEMP_DIR}"

echo ""
echo "🎯 PRODUCTION DEPLOYMENT READY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Clean Package: ${PACKAGE_NAME}"
echo "✨ Debug logs removed for production"
echo ""
echo "🌐 PythonAnywhere Deployment:"
echo "1. Upload ${PACKAGE_NAME} to PythonAnywhere"
echo "2. Extract to frontend/dist/"
echo "3. Reload web app"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
