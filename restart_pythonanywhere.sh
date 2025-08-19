#!/bin/bash
# PythonAnywhere restart script - simplified for PythonAnywhere environment

echo "=== PythonAnywhere App Restart ==="

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "Error: Please run this script from the StructuredDocs root directory"
    exit 1
fi

echo "Stopping any running Flask processes..."
# Kill any existing Flask processes (be careful with this on shared hosting)
pkill -f "flask run" 2>/dev/null || true
sleep 1

echo "Setting up environment..."
export FLASK_APP=backend.app
export FLASK_ENV=production

echo "Checking Python and Flask installation..."
python3 --version
python3 -c "import flask; print(f'Flask version: {flask.__version__}')" 2>/dev/null || echo "Flask not found - please install: pip3 install --user Flask"

echo "Starting Flask application..."
echo "Note: For PythonAnywhere, you should use the Web App configuration instead of running flask directly."
echo "This script is mainly for testing. For production, configure your Web App in the PythonAnywhere dashboard."

# For testing purposes only - PythonAnywhere uses Web Apps for production
echo "Starting test server on localhost..."
python3 -m flask run --host=127.0.0.1 --port=8000 &

sleep 2

if pgrep -f "flask run" > /dev/null; then
    echo "✅ Test Flask server started on localhost:8000"
    echo "💡 For production: Configure Web App in PythonAnywhere dashboard"
    echo "💡 Use the WSGI file: wsgi.py"
else
    echo "❌ Failed to start Flask server"
    echo "Check the error messages above"
fi

echo "=== Setup Complete ==="
echo ""
echo "Next steps for PythonAnywhere:"
echo "1. Go to Web tab in PythonAnywhere dashboard"
echo "2. Create a new Web App (Manual configuration, Python 3.10)"
echo "3. Set source code path to your project directory"
echo "4. Configure WSGI file (see PYTHONANYWHERE_SETUP.md)"
echo "5. Click Reload to start your app"
