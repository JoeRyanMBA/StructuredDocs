#!/bin/bash

echo "🚀 Deploying updated files to PythonAnywhere..."

# Copy the updated WSGI file
echo "📄 Uploading wsgi.py..."
scp wsgi.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/

# Copy the updated app.py
echo "📄 Uploading backend/app.py..."
scp backend/app.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/

echo "✅ Files uploaded successfully!"
echo "🔄 Now reload the web app in PythonAnywhere dashboard"
