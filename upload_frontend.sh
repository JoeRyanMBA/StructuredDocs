#!/bin/bash

echo "🚀 Uploading frontend and backend to PythonAnywhere..."

# Create frontend directory on PythonAnywhere
echo "📁 Creating frontend directory..."
ssh JoeRyanMBA@ssh.pythonanywhere.com "mkdir -p /home/JoeRyanMBA/StructuredDocs/frontend"

# Upload the entire dist folder
echo "📦 Uploading frontend build files..."
scp -r frontend/dist JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/frontend/

# Upload the updated backend app.py
echo "📄 Uploading updated app.py..."
scp backend/app.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/

echo "✅ Upload complete!"
echo "🔄 Now reload your web app in PythonAnywhere dashboard"
echo "🌐 Visit https://structureddocs.joe-ryan.mba to see your full application!"
