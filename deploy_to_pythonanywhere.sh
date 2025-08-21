#!/bin/bash

# Streamlined Deployment Script for PythonAnywhere
# Usage: ./deploy_to_pythonanywhere.sh [commit-message]

set -e  # Exit on any error

echo "🚀 Starting deployment process..."

# Get commit message or use default
COMMIT_MSG="${1:-Auto-deploy frontend changes}"

# Step 1: Build frontend
echo "📦 Building frontend..."
cd frontend
npm install --silent
npm run build
cd ..

# Step 2: Create deployment package
echo "📦 Creating deployment package..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="frontend_deploy_${TIMESTAMP}.tar.gz"
tar -czf "${PACKAGE_NAME}" -C frontend/dist .

echo "✅ Created deployment package: ${PACKAGE_NAME}"

# Step 3: Commit changes to git
echo "💾 Committing changes to git..."
git add .
git commit -m "${COMMIT_MSG}" || echo "No changes to commit"

# Step 4: Push to remote
echo "⬆️ Pushing to remote repository..."
git push origin $(git branch --show-current)

# Step 5: Display deployment instructions
echo ""
echo "🎯 DEPLOYMENT READY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Package: ${PACKAGE_NAME}"
echo "🌐 PythonAnywhere Steps:"
echo ""
echo "1. Upload ${PACKAGE_NAME} to PythonAnywhere Files"
echo "   📍 Upload Location: /home/JoeRyanMBA/StructuredDocs/ (project directory)"
echo ""
echo "2. Run these commands in PythonAnywhere console:"
echo ""
echo "   cd /home/JoeRyanMBA/StructuredDocs"
echo "   mv frontend/dist frontend/dist_backup_${TIMESTAMP}"
echo "   mkdir -p frontend/dist"
echo "   cd frontend/dist"
echo "   tar -xzf ../${PACKAGE_NAME}"
echo "   ls -la  # Verify files are extracted"
echo ""
echo "3. Reload your web app in PythonAnywhere Web tab"
echo "4. Hard refresh (Ctrl+F5) your browser"
echo ""
echo "📋 Expected files in /home/JoeRyanMBA/StructuredDocs/frontend/dist/:"
echo "   - index.html"
echo "   - assets/ (directory with CSS/JS files)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
