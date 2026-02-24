# Digital Ocean Spaces Storage Configuration

## Overview

StructuredDocs now supports **Digital Ocean Spaces** for persistent image storage. This is essential for App Platform deployments where local filesystem storage is ephemeral.

## Setup Instructions

### 1. Create a Space (Already Done)

- Space Name: `1docimages`
- Region: `nyc3`
- Endpoint: `https://1docimages.nyc3.digitaloceanspaces.com`

### 2. Generate Access Keys

1. Go to **API** section in Digital Ocean dashboard
2. Click **Spaces Keys** tab
3. Click **Generate New Key**
4. Save the **Access Key** and **Secret Key** securely

### 3. Configure Environment Variables

Add these to your App Platform environment variables:

```
SPACES_BUCKET=1docimages
SPACES_REGION=nyc3
SPACES_ACCESS_KEY=DO00EEZBJ84FKCJ9MN9E
SPACES_SECRET_KEY=pp+DF/m+4VsnaimgsFVv3KIWO6wZ2rDl3XP1Q4/N/fQ
```

Optional CDN endpoint (if you configure CDN for faster delivery):
```
SPACES_CDN_ENDPOINT=https://1docimages.nyc3.digitaloceanspaces.com
```

### 4. Deploy Changes

1. Commit and push the code changes:
   ```bash
   git add .
   git commit -m "feat: add Digital Ocean Spaces storage support"
   git push
   ```

2. App Platform will auto-deploy and use Spaces for image storage

## How It Works

- **Storage Backend**: Automatic detection - if Spaces environment variables are present, uses Spaces; otherwise falls back to local filesystem
- **Image URLs**: Images stored in Spaces are accessible via public URLs
- **Persistence**: Images survive redeployments and are accessible from multiple app instances
- **Cost**: Spaces pricing is ~$5/month for 250GB storage + bandwidth

## Testing

1. Import a Word document with images
2. Check that images display correctly
3. Verify images are in your Space:
   - Go to Digital Ocean Spaces dashboard
   - Navigate to `1docimages` space
   - Look for `images/imports/{doc_id}/` folder

## Fallback Behavior

If Spaces is not configured:
- Falls back to `IMAGE_STORAGE_ROOT` environment variable
- Uses `/app/backend/static/images` as final fallback
- ⚠️ **Note**: Local storage on App Platform is ephemeral and will be lost on redeployment

## Migration

To migrate existing local images to Spaces:
1. Download images from old storage
2. Upload to Spaces using the Digital Ocean Spaces CLI or web interface
3. Update database `public_url` fields if needed

## Dependencies

- `boto3>=1.34.0` - AWS SDK for Python (S3-compatible, works with Spaces)

Already added to `requirements.txt`.
