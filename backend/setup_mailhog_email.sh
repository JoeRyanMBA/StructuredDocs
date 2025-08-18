#!/bin/bash
# Email configuration for StructuredDocs with MailHog

# Set environment variables for email service
export EMAIL_DEBUG=false
export SMTP_SERVER=localhost
export SMTP_PORT=1025
export SMTP_USERNAME=
export SMTP_PASSWORD=
export FROM_EMAIL=noreply@structureddocs.local
export FROM_NAME="StructuredDocs Review System"

echo "Email configuration set for MailHog (localhost:1025)"
echo "MailHog web interface: http://localhost:8025"
