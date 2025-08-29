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
        
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        print('✅ Database connection successful')
        
        # Check if notifications table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'📋 Available tables: {tables}')
        
        if 'notifications' in tables:
            print('✅ Notifications table exists')
            
            # Try to query notifications
            count = Notification.query.count()
            print(f'📊 Notifications count: {count}')
            
            # Try to create a test notification
            test_notification = Notification(
                title='Test Notification',
                message='This is a test notification',
                type='test'
            )
            db.session.add(test_notification)
            db.session.commit()
            print('✅ Test notification created successfully')
            
            # Clean up test notification
            db.session.delete(test_notification)
            db.session.commit()
            print('✅ Test notification cleaned up')
            
        else:
            print('❌ Notifications table does not exist')
            print('🛠️  Creating notifications table...')
            db.create_all()
            print('✅ Notifications table created')
            
except Exception as e:
    print(f'❌ Database test failed: {e}')
    import traceback
    traceback.print_exc()
"

echo "🔍 Testing dashboard stats endpoint..."
export PYTHONPATH=/home/JoeRyanMBA/StructuredDocs:$PYTHONPATH
python3.12 -c "
import sys
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs')
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs/backend')

try:
    from backend.app import create_app
    from backend.routes.dashboard import bp as dashboard_bp
    app = create_app()
    
    # Check if blueprint is already registered
    if 'dashboard' not in [bp.name for bp in app.blueprints.values()]:
        app.register_blueprint(dashboard_bp)
    
    with app.test_client() as client:
        # Test GET request to dashboard stats endpoint
        response = client.get('/api/dashboard/stats')
        print(f'� Dashboard stats status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Dashboard stats endpoint working!')
            data = response.get_json()
            print(f'📈 Stats keys: {list(data.keys()) if data else \"No data\"}')
        else:
            print(f'❌ Dashboard stats failed: {response.get_data(as_text=True)}')
            
except Exception as e:
    print(f'❌ Dashboard test failed: {e}')
    import traceback
    traceback.print_exc()
"

echo "👤 Creating admin user..."
export PYTHONPATH=/home/JoeRyanMBA/StructuredDocs:$PYTHONPATH
python3.12 -c "
import sys
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs')
sys.path.insert(0, '/home/JoeRyanMBA/StructuredDocs/backend')

from backend.create_admin import create_admin_user
create_admin_user('admin@example.com', 'password', 'Admin User')
print('✅ Admin user created successfully')
"

echo "🧹 Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "✅ Database setup complete!"
echo ""
echo "🔑 Admin Login Credentials:"
echo "   Email: admin@example.com"
echo "   Password: password"
echo ""
echo "🔄 Next steps:"
echo "1. Go to https://www.pythonanywhere.com/user/JoeRyanMBA/webapps/"
echo "2. Click the 'Reload' button for your web app"
echo "3. Try logging in with the admin credentials above"
echo ""
echo "🌐 Your app will be live at: https://joeryanmba.pythonanywhere.com"
