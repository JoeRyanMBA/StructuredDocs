#!/bin/bash
# PythonAnywhere Deployment Script
# Run this script in your PythonAnywhere console to update from GitHub

set -e

echo "🚀 Deploying StructuredDocs to PythonAnywhere..."

# Navigate to project directory
cd /home/JoeRyanMBA/StructuredDocs

echo "📥 Pulling latest changes from GitHub..."
if [ -d .git ]; then
    git pull origin main || git pull || true
else
    echo "(No .git repo in project directory; skipping git pull)"
fi

echo "📦 Installing/updating Python dependencies..."
pip3 install --user -r backend/requirements.txt || pip3.12 install --user -r backend/requirements.txt || true

echo "🗄️  Running database migrations (if any)..."
cd backend
export PYTHONANYWHERE_ENVIRONMENT=1
python3 -c "
try:
    from flask_migrate import upgrade
    from app import create_app
    app = create_app()
    with app.app_context():
        upgrade()
    print('✅ Database migrations completed')
except Exception as e:
    print(f'ℹ️  No migrations to run or error: {e}')
"

echo "👤 Creating admin user..."
python3 create_admin.py || python3.12 create_admin.py || true
cd ..

echo "🧹 Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Deployment complete!"
echo ""
echo "🔄 Next steps:"
echo "1. Go to https://www.pythonanywhere.com/user/JoeRyanMBA/webapps/"
echo "2. Click the 'Reload' button for your web app"
echo "3. Check the error logs if anything doesn't work"
echo ""
echo "🌐 Your app will be live at: https://joeryanmba.pythonanywhere.com"
