# Email Sending and Domain Authentication

If recipients see "This email has failed its domain's authentication requirements", configure a verified sender and SPF/DKIM for your domain to satisfy DMARC.

Checklist

- Set environment variables for the app:

  - `DEFAULT_FROM_EMAIL`: a real mailbox on your verified domain (e.g. `no-reply@structureddocs.online`)
  - `FROM_EMAIL` (optional): if unset, the app will fall back to `DEFAULT_FROM_EMAIL`

  - `FROM_NAME` (optional): sender display name
  - `EMAIL_PROVIDER=sendgrid` (or `smtp`/`postmark`/`resend`)

  - `SENDGRID_API_KEY`: your SendGrid API key
  - `SENDGRID_VERIFIED_SENDER`: a SendGrid-verified sender address (or a domain-authenticated from)

SendGrid configuration

1. In SendGrid, complete either:

- Single Sender Verification for the address in `SENDGRID_VERIFIED_SENDER`, or

- Domain Authentication for `structureddocs.online` (adds SPF + DKIM DNS records).

2. If using Single Sender, set `SENDGRID_VERIFIED_SENDER` to that address. The app will use it as the From and set Reply-To to your branding address if different.

3. If you completed Domain Authentication and want your branded From, set `FROM_EMAIL=no-reply@structureddocs.online` and leave `SENDGRID_VERIFIED_SENDER` unset.

SMTP configuration (alternative)

- Set `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`.

- Ensure the From address matches the authenticated mailbox or add a Reply-To header as configured in the app.

- Publish SPF/DKIM/DMARC for your domain if possible.

Troubleshooting

- Call `GET /api/admin/email-status` with `Authorization: Bearer $ADMIN_API_KEY` to view sanitized config.

- Call `POST /api/admin/send-test-email` with `{"to": "you@example.com"}` and `Authorization: Bearer $ADMIN_API_KEY` to test delivery. The response will include provider details and status.
