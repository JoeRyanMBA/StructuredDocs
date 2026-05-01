# Email Sending and Domain Authentication

StructuredDocs now sends email via SMTP. For Proton recipients, reliable delivery depends on correct SPF, DKIM, and DMARC alignment for your sender domain.

Checklist

- Set environment variables for the app:

  - `EMAIL_PROVIDER=smtp`
  - `SMTP_SERVER`: SMTP host (for Proton relay, `smtp.protonmail.ch`)
  - `SMTP_PORT`: usually `587` for STARTTLS, or `465` for SSL
  - `SMTP_USERNAME`: SMTP account username
  - `SMTP_PASSWORD`: SMTP account password
  - `SMTP_USE_SSL=true` only for port `465`

  - `DEFAULT_FROM_EMAIL`: a real mailbox on your verified domain (example: `no-reply@structureddocs.online`)
  - `FROM_EMAIL` (optional): if unset, app falls back to `DEFAULT_FROM_EMAIL`
  - `FROM_NAME` (optional): sender display name

SMTP configuration notes

1. Ensure the `FROM_EMAIL` domain is authorized by your SMTP provider.
2. For Proton relay, use the SMTP credentials issued by Proton for relay/SMTP access.
3. Publish SPF, DKIM, and DMARC records for your sender domain.

Proton-focused deliverability tips

- Proton is strict about authentication alignment.
- Keep envelope sender and visible From aligned to the same domain when possible.
- Avoid using unverified or `.local` sender addresses.

Troubleshooting

- Call `GET /api/admin/email-status` with either `X-Admin-Token: $ADMIN_API_KEY` or an admin JWT to view sanitized configuration.
- Call `POST /api/admin/send-test-email` with `{"to": "you@example.com"}` and either `X-Admin-Token: $ADMIN_API_KEY` or an admin JWT to test delivery.
- Check message headers in Proton for:

```text
Authentication-Results:
  spf=pass;
  dkim=pass;
  dmarc=pass
```

- If delivery still fails, check provider SMTP logs for auth/rate-limit or rejection details.
