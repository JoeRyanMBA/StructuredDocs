# App Platform Configuration Guide

## Required Environment Variables

### 1. Digital Ocean Spaces (for persistent images)

In your App Platform dashboard, add these environment variables:

```
SPACES_BUCKET=1docimages
SPACES_REGION=nyc3
SPACES_ACCESS_KEY=<your-spaces-access-key>
SPACES_SECRET_KEY=<your-spaces-secret-key>
```

**To get your access keys:**
1. Go to Digital Ocean Dashboard → API
2. Click "Spaces Keys" tab  
3. Click "Generate New Key"
4. Copy the Access Key and Secret Key

### 2. Database (already configured)

```
DATABASE_URL=postgresql://<username>:<password>@<host>:25060/defaultdb?sslmode=require
```

### 3. Other Required Variables

```
SECRET_KEY=<random-32-char-string>
FRONTEND_URL=https://structureddocs.online
IMAGE_STORAGE_ROOT=/app/backend/static/images
```

## How to Add Environment Variables in App Platform

1. Go to https://cloud.digitalocean.com/apps
2. Click your StructuredDocs app
3. Go to "Settings" tab
4. Scroll to "Environment Variables" section
5. Click "Edit"
6. Add each variable with name and value
7. Click "Save"
8. App will automatically redeploy

## Verification

After adding environment variables and redeploying:

1. Import a document with images
2. Check `/all-images` - images should display
3. Go to Digital Ocean Spaces dashboard
4. Open `1docimages` space
5. You should see files in `images/imports/` folders

## Troubleshooting

### Images not uploading to Spaces
- Check environment variables are set correctly
- Verify Spaces access key has read/write permissions
- Check App Platform build logs for boto3 import errors

### Images showing 404
- If using local storage (no Spaces vars), images lost on redeploy
- Set Spaces env vars and reimport documents

### Word imports failing
- Check Dockerfile includes: `pandoc`
- Build logs should show: `apt-get install -y gcc curl pandoc`
