#!/bin/bash
# Database Setup Script for PythonAnywhere
# Run this script to initialize/reset your database and create admin user

set -e

echo "🚀 Setting up StructuredDocs database on PythonAnywhere..."

# Navigate to project directory
cd /home/JoeRyanMBA/StructuredDocs

echo "📦 Installing/updating Python dependencies..."
pip3.12 install --user -r backend/requirements.txt

cd backend

echo "🗄️  Creating/updating database tables..."
export PYTHONANYWHERE_ENVIRONMENT=1
export PYTHONPATH=/home/JoeRyanMBA/StructuredDocs:$PYTHONPATH
python3.12 -c "
import sys
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs')
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs/backend')

from backend.app import create_app
app = create_app()

# Import db after app creation to avoid initialization issues
from backend.extensions import db
with app.app_context():
    db.create_all()
    print('✅ Database tables created/updated')
"

echo "🗄️  Running database migrations..."
export PYTHONPATH=/home/JoeRyanMBA/StructuredDocs:$PYTHONPATH
python3.12 -c "
import sys
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs')
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs/backend')

try:
    from flask_migrate import upgrade
    from backend.app import create_app
    app = create_app()
    with app.app_context():
        upgrade()
    print('✅ Database migrations completed')
except Exception as e:
    print(f'ℹ️  No migrations to run or error: {e}')
"

echo "� Testing database connection and tables..."
export PYTHONPATH=/home/JoeRyanMBA/StructuredDocs:$PYTHONPATH
python3.12 -c "
import sys
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs')
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs/backend')

try:
    from backend.app import create_app
    app = create_app()
    
    with app.app_context():
        from backend.extensions import db
        from backend.models import Notification
        #!/bin/bash
        # Legacy placeholder: StructuredDocs now provisions databases via managed cloud services.

        set -euo pipefail

        echo "This helper has been retired. Use the backend deployment docs to provision databases."
        exit 1
        tables = inspector.get_table_names()
