#!/bin/bash

echo "🚀 Deploying ALL backend files to PythonAnywhere..."

# First, ensure directories exist on PythonAnywhere
echo "📁 Creating directories on PythonAnywhere..."
ssh JoeRyanMBA@ssh.pythonanywhere.com "mkdir -p /home/JoeRyanMBA/StructuredDocs/backend/routes"
ssh JoeRyanMBA@ssh.pythonanywhere.com "mkdir -p /home/JoeRyanMBA/StructuredDocs/backend/utils"
ssh JoeRyanMBA@ssh.pythonanywhere.com "mkdir -p /home/JoeRyanMBA/StructuredDocs/backend/static"

# Upload main backend files
echo "📄 Uploading main backend files..."
scp backend/app.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/
scp backend/models.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/
scp backend/extensions.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/
scp backend/requirements.txt JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/
scp backend/__init__.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/

# Upload all route files
echo "📄 Uploading route files..."
scp backend/routes/__init__.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/admin.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/collections.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/dashboard.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/feedback.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/images.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/import_handler.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/imports.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/links.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/metrics.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/milestones.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/notifications.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/projects.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/publications.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/review_tokens.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/reviews.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/sequences.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/stakeholders.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/tags.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/tasks.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/topics.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/
scp backend/routes/users.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/routes/

# Upload utils files
echo "📄 Uploading utils files..."
scp backend/utils/__init__.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/utils/
scp backend/utils/email_service.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/utils/
scp backend/utils/image_handler.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/utils/
scp backend/utils/link_handler.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/backend/utils/

# Upload WSGI file
echo "📄 Uploading wsgi.py..."
scp wsgi.py JoeRyanMBA@ssh.pythonanywhere.com:/home/JoeRyanMBA/StructuredDocs/

echo "✅ All files uploaded successfully!"
echo "🔄 Now reload the web app in PythonAnywhere dashboard"
