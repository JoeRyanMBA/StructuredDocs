# Spaces CORS and Permissions Configuration

## Problem
Images are uploaded to Spaces and redirect (302) works, but browsers get **403 Forbidden** when trying to load images.

## Symptoms
- Network tab shows 302 redirect successful
- Browser gets 403 Forbidden from CDN URL
- Example: `https://1docimages.nyc3.digitaloceanspaces.com/images/imports/134/image1.png` → 403

## Root Cause
Two potential issues:
1. **Bucket not configured for public access** (most common)
2. **Missing CORS headers** (prevents browser from loading)

## Solution 1: Enable Public Access on Bucket (CRITICAL)

### Via Digital Ocean Dashboard

1. **Go to Spaces** in Digital Ocean dashboard
2. **Click on `1docimages` space**
3. **Go to Settings tab**
4. **Scroll to "File Listing"**
5. **Enable "Public" access** (allows files with public-read ACL to be accessed)

**OR** if that option doesn't exist:

1. **Check "Permissions" or "Access Control"**
2. **Ensure bucket allows public files**
3. **Verify files are uploaded with `public-read` ACL**

### Via AWS CLI (S3-compatible)

```bash
# Configure AWS CLI for Digital Ocean Spaces
aws configure --profile digitalocean
# Access Key: Your SPACES_ACCESS_KEY
# Secret Key: Your SPACES_SECRET_KEY  
# Region: nyc3

# Remove any restrictive bucket policy
aws s3api delete-public-access-block \
  --bucket 1docimages \
  --endpoint-url https://nyc3.digitaloceanspaces.com \
  --profile digitalocean

# Set bucket policy to allow public reads
cat > bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::1docimages/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket 1docimages \
  --policy file://bucket-policy.json \
  --endpoint-url https://nyc3.digitaloceanspaces.com \
  --profile digitalocean
```

## Solution 2: Configure CORS on Spaces

### Via Digital Ocean Dashboard

1. **Go to Spaces** in Digital Ocean dashboard
2. **Click on `1docimages` space**
3. **Go to Settings tab**
4. **Scroll to CORS Configurations**
5. **Click "Add CORS Configuration"**
6. **Add this configuration**:

```json
{
  "AllowedOrigins": ["*"],
  "AllowedMethods": ["GET", "HEAD"],
  "AllowedHeaders": ["*"],
  "MaxAgeSeconds": 3600
}
```

**For production (more secure), use specific origins**:
```json
{
  "AllowedOrigins": [
    "https://structureddocs.online",
    "https://www.structureddocs.online"
  ],
  "AllowedMethods": ["GET", "HEAD"],
  "AllowedHeaders": ["*"],
  "MaxAgeSeconds": 3600
}
```

### Via AWS CLI (S3-compatible)

```bash
# Install AWS CLI if needed
pip install awscli

# Configure for Digital Ocean Spaces
aws configure --profile digitalocean
# Enter your SPACES_ACCESS_KEY as Access Key ID
# Enter your SPACES_SECRET_KEY as Secret Access Key
# Enter nyc3 as Default region name
# Press enter for Default output format

# Create CORS configuration file
cat > cors.json << 'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
EOF

# Apply CORS configuration
aws s3api put-bucket-cors \
  --bucket 1docimages \
  --cors-configuration file://cors.json \
  --endpoint-url https://nyc3.digitaloceanspaces.com \
  --profile digitalocean

# Verify CORS is set
aws s3api get-bucket-cors \
  --bucket 1docimages \
  --endpoint-url https://nyc3.digitaloceanspaces.com \
  --profile digitalocean
```

## Verify Everything is Working

### Step 1: Test Public Access (Fix 403 errors)

```bash
# Test if file is publicly accessible (without auth)
curl -I https://1docimages.nyc3.digitaloceanspaces.com/images/imports/134/image1_2d3727c5.png
```

**Expected**: `HTTP/2 200` (or `HTTP/1.1 200`)
**If you get 403**: Bucket public access is not configured (see Solution 1)

### Step 2: Test CORS Headers

```bash
curl -I -H "Origin: https://structureddocs.online" \
  https://1docimages.nyc3.digitaloceanspaces.com/images/imports/134/image1_2d3727c5.png
```

**Expected**:
```
HTTP/2 200
access-control-allow-origin: *
access-control-allow-methods: GET, HEAD
```

**If CORS headers missing**: CORS not configured (see Solution 2)

### Step 3: Test in Browser Console

Open browser DevTools (F12) → Console tab:

```javascript
// Test public access
fetch('https://1docimages.nyc3.digitaloceanspaces.com/images/imports/134/image1_2d3727c5.png')
  .then(r => console.log('✅ Status:', r.status, 'CORS:', r.headers.get('access-control-allow-origin')))
  .catch(e => console.error('❌ Error:', e.message))
```

**Expected**: `✅ Status: 200 CORS: *`

### Step 4: Verify in App

1. **Hard refresh your app** (Ctrl+Shift+R / Cmd+Shift+R)
   - Images should now display!

## Security Notes

- `AllowedOrigins: ["*"]` allows any website to load your images (good for public content)
- For private content, specify exact domains
- `AllowedMethods: ["GET", "HEAD"]` is read-only (secure for images)
- CDN automatically adds proper cache headers

## Related Docs
- https://docs.digitalocean.com/products/spaces/how-to/configure-cors/
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html
