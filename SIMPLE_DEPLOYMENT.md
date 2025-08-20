# Simple PythonAnywhere Deployment Guide

## Recommended: Manual Deployment (No SSH Key Needed)

### One-Time Setup:
1. **Clone repo** on PythonAnywhere:
   ```bash
   cd ~
   git clone https://github.com/JoeRyanMBA/StructuredDocs.git
   ```

2. **Install dependencies**:
   ```bash
   pip3.12 install --user SQLAlchemy Flask-SQLAlchemy Flask-Migrate Flask-CORS python-docx Flask reportlab psutil Pillow email-validator psycopg2-binary Flask-JWT-Extended
   ```

3. **Create the deployment script**:
   ```bash
   cd ~/StructuredDocs
   chmod +x deploy_pythonanywhere.sh
   ```

### Every Deployment:
1. **Push changes** to GitHub from your local machine
2. **Run deployment** on PythonAnywhere:
   ```bash
   cd ~/StructuredDocs
   ./deploy_pythonanywhere.sh
   ```
3. **Reload web app** in PythonAnywhere Web tab

### Alternative: Manual Steps
If the script doesn't work, you can do it manually:
```bash
cd ~/StructuredDocs
git pull origin main
pip3.12 install --user -r backend/requirements.txt
# Then reload web app in dashboard
```

## For Automatic Deployment Later:
- Follow the SSH key steps above
- Or use PythonAnywhere's "Deploy from GitHub" feature if available

## Troubleshooting:
- **Permission denied**: Make sure the deployment script is executable: `chmod +x deploy_pythonanywhere.sh`
- **Git errors**: Set up Git credentials on PythonAnywhere: `git config --global user.name "Your Name"`
- **Package errors**: Use `pip3.12 install --user package-name` to install missing packages
