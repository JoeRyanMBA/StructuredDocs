#!/bin/bash

# Clean Backend Deployment Script for PythonAnywhere
# This script creates a minimal production package

echo "🧹 Creating clean backend deployment package..."

# Create temporary directory for clean backend
TEMP_DIR="backend_production_temp"
mkdir -p "${TEMP_DIR}"

# Copy only essential backend files
echo "📁 Copying essential backend files..."

# Core application files
cp backend/app.py "${TEMP_DIR}/"
cp backend/__init__.py "${TEMP_DIR}/"
cp backend/extensions.py "${TEMP_DIR}/"
cp backend/models.py "${TEMP_DIR}/"
cp backend/requirements.txt "${TEMP_DIR}/"

# Routes directory (exclude test files and cache)
cp -r backend/routes "${TEMP_DIR}/"
rm -f "${TEMP_DIR}/routes/test_imports.py" 2>/dev/null || true
rm -f "${TEMP_DIR}/routes/publications.py.backup" 2>/dev/null || true
rm -rf "${TEMP_DIR}/routes/__pycache__" 2>/dev/null || true

# Utils directory (exclude cache files)
cp -r backend/utils "${TEMP_DIR}/"
rm -rf "${TEMP_DIR}/utils/__pycache__" 2>/dev/null || true

# Email service (essential for notifications)
cp backend/notifications.py "${TEMP_DIR}/"
cp backend/pdf_config.py "${TEMP_DIR}/"

# Static files (essential for image serving)
cp -r backend/static "${TEMP_DIR}/"

# Migrations (essential for database)
cp -r backend/migrations "${TEMP_DIR}/"

# Alembic config (essential for migrations)
cp backend/alembic.ini "${TEMP_DIR}/"

# Create deployment package
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="backend_clean_${TIMESTAMP}.tar.gz"
tar -czf "${PACKAGE_NAME}" -C "${TEMP_DIR}" .

# Cleanup
rm -rf "${TEMP_DIR}"

echo "✅ Clean backend package created: ${PACKAGE_NAME}"
echo ""
echo "📦 Package contents:"
tar -tzf "${PACKAGE_NAME}" | head -20

echo ""
echo "🚀 Upload this package to PythonAnywhere and extract to your project directory"</content>
<parameter name="filePath">/workspaces/StructuredDocs/create_clean_backend.sh
