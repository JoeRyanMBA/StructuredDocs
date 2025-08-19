# PythonAnywhere Setup Guide for StructuredDocs

## Prerequisites
1. Have a PythonAnywhere account
2. Upload your project files to PythonAnywhere

## Setup Steps

### 1. Install Required Packages
Open a Bash console on PythonAnywhere and run:

```bash
pip3.12 install --user SQLAlchemy Flask-SQLAlchemy Flask-Migrate Flask-CORS python-docx Flask reportlab psutil Pillow email-validator psycopg2-binary Flask-JWT-Extended
```

### 2. Upload Project Files
Upload your entire StructuredDocs project to your PythonAnywhere files section, typically to:
```
/home/yourusername/StructuredDocs/
```

### 3. Configure Web App
1. Go to the **Web** tab in your PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.12** (or your preferred version)
5. Set the **Source code** path to: `/home/yourusername/StructuredDocs/`
6. Set the **Working directory** to: `/home/yourusername/StructuredDocs/`

### 4. Configure WSGI File
1. In the Web tab, click on the **WSGI configuration file** link
2. Replace the contents with the following:

```python
#!/usr/bin/python3

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/StructuredDocs'  # Update with your actual username
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set up the Flask app
os.chdir(project_home)
from backend.app import app as application

if __name__ == "__main__":
    application.run()
```

### 5. Set Up Database
In a Bash console, navigate to your project and set up the database:

```bash
cd /home/yourusername/StructuredDocs/
python3 backend/seed_database.py
```

### 6. Configure Static Files (for Vue.js frontend)
1. In the Web tab, go to the **Static files** section
2. Add a new static files mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/StructuredDocs/frontend/dist/`

### 7. Build Frontend (if needed)
If you need to build the Vue.js frontend:

```bash
cd /home/yourusername/StructuredDocs/frontend/
npm install
npm run build
```

### 8. Reload Web App
Click the **Reload** button in the Web tab to start your application.

## Important Notes

### Database Location
- PythonAnywhere uses SQLite by default
- Your database will be at: `/home/yourusername/StructuredDocs/instance/structured_docs.db`

### Logs
- Check the **Error log** and **Server log** in the Web tab for debugging
- Backend logs: `/home/yourusername/StructuredDocs/backend/nohup.out`

### Environment Variables
If you need environment variables, set them in the WSGI file:
```python
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = 'sqlite:///instance/structured_docs.db'
```

### Ports
- PythonAnywhere handles port assignment automatically
- Your app will be available at: `https://yourusername.pythonanywhere.com`
- No need to specify ports like 5050 in the code

## Troubleshooting

### Common Issues:
1. **Import errors**: Make sure all packages are installed with `pip3.12 install --user`
2. **Database errors**: Ensure the database is created and migrated
3. **Static files not loading**: Check the static files mapping in Web tab
4. **App not reloading**: Click the Reload button after changes

### Checking Logs:
```bash
tail -f /var/log/yourusername.pythonanywhere.com.error.log
tail -f /var/log/yourusername.pythonanywhere.com.server.log
```
