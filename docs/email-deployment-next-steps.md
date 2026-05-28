# Email SMTP Deployment - Next Steps

## Objective

Finish SMTP configuration so password setup and review emails are delivered reliably, including to Proton addresses.

## Required Environment Variables

Set these in your hosting platform:

```bash
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.protonmail.ch
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_USE_SSL=false
DEFAULT_FROM_EMAIL=no-reply@structureddocs.online
FROM_EMAIL=no-reply@structureddocs.online
FROM_NAME=StructuredDocs
EMAIL_DEBUG=false
```

## Verification Steps

1. Check runtime email config:

```bash
curl -H "X-Admin-Token: $ADMIN_API_KEY" \
  https://your-domain/api/admin/email-status
```

2. Send a test message:

```bash
curl -X POST \
  -H "X-Admin-Token: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"to": "your-test@proton.me"}' \
  https://your-domain/api/admin/send-test-email
```

3. Inspect received headers and confirm:

```text
Authentication-Results:
  spf=pass;
  dkim=pass;
  dmarc=pass
```

## Common Issues

- Invalid SMTP credentials.
- Wrong SMTP host/port combination.
- `EMAIL_DEBUG=true` (writes files instead of sending).
- Sender domain missing SPF/DKIM/DMARC records.
- From address not authorized by the SMTP account.

## Success Criteria

- Test endpoint returns `ok: true`.
- Proton recipient gets the message.
- No authentication failure warning in message headers.
