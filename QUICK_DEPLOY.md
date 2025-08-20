# Quick PythonAnywhere Deployment Guide

## Your Setup Status ✅
- ✅ PostgreSQL database configured
- ✅ Flask app properly structured
- ✅ WSGI file created

## Steps to Deploy on PythonAnywhere:

### 1. Upload Files
Upload your entire StructuredDocs folder to PythonAnywhere files section

### 2. Install Dependencies
In a PythonAnywhere console:
```bash
pip3.13 install --user SQLAlchemy Flask-SQLAlchemy Flask-Migrate Flask-CORS python-docx Flask reportlab psutil Pillow email-validator psycopg2-binary Flask-JWT-Extended
```

### 3. Create Web App
1. Go to **Web** tab in PythonAnywhere dashboard
2. **Add a new web app** → **Manual configuration** → **Python 3.13**
3. Set **Source code**: `/home/JoeRyanMBA/StructuredDocs/`
4. Set **Working directory**: `/home/JoeRyanMBA/StructuredDocs/`

### 4. Configure WSGI
Click on **WSGI configuration file** and replace contents with:
```python
#!/usr/bin/python3
import sys
import os

project_home = '/home/JoeRyanMBA/StructuredDocs'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.chdir(project_home)
from backend.app import create_app
application = create_app()
```

### 5. Set Up Database
In console:
```bash
cd /home/JoeRyanMBA/StructuredDocs/
python3 backend/seed_database.py
```

### 6. Frontend (Optional)
If serving Vue.js files:
- Build: `cd frontend && npm run build`
- Static files mapping: URL `/static/` → Directory `/home/JoeRyanMBA/StructuredDocs/frontend/dist/`

### 7. Launch
Click **Reload** in Web tab

## Your app will be live at:
`https://joeryanmba.pythonanywhere.com`

## Troubleshooting:
- Check **Error log** in Web tab
- Ensure PostgreSQL credentials are correct
- Verify all packages are installed with `pip3.13 install --user`
