# StructuredDocs PythonAnywhere Full Deployment Guide

## Files to Upload

### 1. Updated Backend (app.py)
- **Source**: `/workspaces/StructuredDocs/app_updated.py`
- **Destination**: `/home/JoeRyanMBA/StructuredDocs/backend/app.py`
- **Action**: Replace the existing app.py file

### 2. Frontend Files
- **Source**: `/workspaces/StructuredDocs/frontend/dist/*` (all contents)
- **Destination**: `/home/JoeRyanMBA/StructuredDocs/frontend/dist/`
- **Action**: Upload all files and folders from the dist directory

## Step-by-Step Deployment

### Step 1: Upload Backend
1. Download `app_updated.py` from this Codespace
2. In PythonAnywhere Files tab, navigate to `/home/JoeRyanMBA/StructuredDocs/backend/`
3. Delete or rename the existing `app.py`
4. Upload the new `app_updated.py` and rename it to `app.py`

### Step 2: Upload Frontend
1. Download the `deployment_package.tar.gz` file from this Codespace
2. Extract it locally to get the `frontend/dist/` folder
3. In PythonAnywhere Files tab, navigate to `/home/JoeRyanMBA/StructuredDocs/`
4. Create the directory structure: `frontend/dist/`
5. Upload all contents from your local `frontend/dist/` to the PythonAnywhere `frontend/dist/` folder:
   - `index.html`
   - `assets/` folder (with all CSS/JS files)
   - `images/` folder
   - `tinymce/` folder

### Step 3: Reload Web App
1. Go to PythonAnywhere Web tab
2. Click "Reload" on your web app
3. Wait for the reload to complete

### Step 4: Test
1. Visit `https://structureddocs.joe-ryan.mba`
2. You should see the full StructuredDocs application
3. Login with: Tester1 / Census2030 (HTTP Basic Auth)

## Expected Results

- **Root URL**: `https://structureddocs.joe-ryan.mba` → Full Vue.js application
- **API Endpoints**: `https://structureddocs.joe-ryan.mba/api/*` → JSON responses
- **Authentication**: HTTP Basic Auth protects both frontend and API
- **Database**: PostgreSQL with 42 projects, 2 stakeholders, etc.

## Troubleshooting

If you see JSON instead of the web interface:
- Check that frontend files are uploaded to the correct path
- Verify the directory structure matches exactly
- Ensure all assets are uploaded (CSS, JS, images)

If API endpoints don't work:
- Check that the app.py was properly uploaded and replaced
- Verify the web app was reloaded after file changes
