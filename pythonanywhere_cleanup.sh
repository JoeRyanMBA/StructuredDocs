#!/bin/bash

# PythonAnywhere Storage Cleanup Script
# This script removes unnecessary files to free up storage space

echo "=== PythonAnywhere Storage Cleanup ==="
echo "This will remove development files and duplicates to save ~400MB"
echo ""

# Function to safely remove files/directories
safe_remove() {
    if [ -e "$1" ]; then
        echo "Removing: $1"
        rm -rf "$1"
    else
        echo "Not found: $1"
    fi
}

# Remove duplicate frontend builds (keep only the latest one)
echo "1. Removing duplicate frontend builds..."
safe_remove "frontend_dist.zip"
safe_remove "frontend_dist_fixed.zip"
safe_remove "frontend_dist_with_metrics_fix.zip"
safe_remove "frontend_final_with_notifications_fix.zip"
safe_remove "deployment_package.tar.gz"
# Keep frontend_dist_debug_modal.zip as it's the latest

echo ""
echo "2. Removing development dependencies..."
safe_remove "backend/venv"
safe_remove "node_modules"
safe_remove "package-lock.json"

echo ""
echo "3. Removing old app versions..."
safe_remove "app_final.py"
safe_remove "app_updated.py"
safe_remove "app_final_with_notifications_fix.py"
safe_remove "app_final_with_topics_and_notifications_fix.py"
safe_remove "app_production_with_tasks.py"

echo ""
echo "4. Removing development/testing files..."
safe_remove "csv_export"
safe_remove "cypress"
safe_remove "cypress.config.js"
safe_remove "cypress.config.json"
safe_remove "backend/debug_emails"
safe_remove "test_*.py"
safe_remove "debug_*.py"
safe_remove "final_*.py"
safe_remove "fix_*.py"
safe_remove "check_*.py"
safe_remove "export_*.py"
safe_remove "migrate_*.py"
safe_remove "setup_*.py"

echo ""
echo "5. Removing large sample images..."
safe_remove "backend/static/images/20221211_101032_*.jpg"
safe_remove "backend/static/images/20221123_103925_*.jpg"
safe_remove "backend/static/images/20221224_170207_*.jpg"

echo ""
echo "6. Removing documentation and guides..."
safe_remove "*.md"
safe_remove "perfectly_aligned_toc.pdf"

echo ""
echo "7. Removing shell scripts..."
safe_remove "*.sh"
safe_remove "deploy_*.sh"
safe_remove "restart*.sh"
safe_remove "upload_*.sh"
safe_remove "make_port_*.sh"

echo ""
echo "8. Removing backup files..."
safe_remove "backend/routes/*.backup"
safe_remove "*.sql"

echo ""
echo "=== Files to KEEP on PythonAnywhere ==="
echo "✓ frontend/ (built Vue.js app)"
echo "✓ backend/app.py (main Flask app)"
echo "✓ backend/models.py (database models)"
echo "✓ backend/routes/ (API routes)"
echo "✓ backend/utils/ (utility functions)"
echo "✓ backend/migrations/ (database migrations)"
echo "✓ backend/requirements.txt (Python dependencies)"
echo "✓ wsgi.py or pythonanywhere_wsgi_content.py (WSGI config)"
echo "✓ README.md (keep this one for reference)"

echo ""
echo "=== Cleanup Complete ==="
echo "Estimated space saved: ~400MB"
echo ""
echo "After running this script, you should only need:"
echo "1. The frontend/ directory (built Vue.js app)"
echo "2. The backend/ directory (Flask API + essential files)"
echo "3. The WSGI configuration file"
echo ""
echo "Total size after cleanup should be < 200MB"
