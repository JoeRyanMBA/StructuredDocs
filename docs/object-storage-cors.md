# Object Storage CORS and Permissions Configuration

## Problem

Uploads succeed, but browsers receive 403 errors when loading image URLs.

## Common causes

1. Bucket/object is not publicly readable (or signed URL policy blocks access).
2. CORS rules are missing or too restrictive.

## Recommended CORS configuration

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://your-frontend-domain.example"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

## Verify access

```bash
curl -I https://your-bucket-endpoint/images/imports/134/image1.png
curl -I -H "Origin: https://your-frontend-domain.example" \
  https://your-bucket-endpoint/images/imports/134/image1.png
```

Expected:
- HTTP 200 response
- Access-Control-Allow-Origin header for your frontend domain

## Security notes

- Prefer explicit origins over `*` in production.
- Limit methods to GET/HEAD for image access.
