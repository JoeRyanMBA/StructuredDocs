# Spaces CORS Configuration

## Problem
Images are uploaded to Spaces and redirect (302) works, but browsers can't load the images due to CORS (Cross-Origin Resource Sharing) restrictions.

## Symptoms
- Network tab shows 302 redirect successful
- Browser fails to load the CDN image
- Console shows CORS errors like: "No 'Access-Control-Allow-Origin' header"

## Solution: Configure CORS on Digital Ocean Spaces

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

## Verify CORS is Working

After configuring CORS:

1. **Test with curl**:
   ```bash
   curl -I -H "Origin: https://structureddocs.online" \
     https://1docimages.nyc3.digitaloceanspaces.com/images/imports/134/image1_2d3727c5.png
   ```
   
   Should return:
   ```
   HTTP/2 200
   access-control-allow-origin: *
   access-control-allow-methods: GET, HEAD
   ```

2. **Test in browser**:
   - Open browser DevTools → Console
   - Try fetching an image:
     ```javascript
     fetch('https://1docimages.nyc3.digitaloceanspaces.com/images/imports/134/image1_2d3727c5.png')
       .then(r => console.log('✅ CORS OK:', r.status))
       .catch(e => console.error('❌ CORS Error:', e))
     ```

3. **Hard refresh your app** (Ctrl+Shift+R / Cmd+Shift+R)
   - Images should now display!

## Security Notes

- `AllowedOrigins: ["*"]` allows any website to load your images (good for public content)
- For private content, specify exact domains
- `AllowedMethods: ["GET", "HEAD"]` is read-only (secure for images)
- CDN automatically adds proper cache headers

## Related Docs
- https://docs.digitalocean.com/products/spaces/how-to/configure-cors/
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html
