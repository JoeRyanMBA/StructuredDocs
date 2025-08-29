#!/bin/bash
# Email Configuration Script for Gmail SMTP
# Replace YOUR_EMAIL and YOUR_APP_PASSWORD with your actual values

echo "Setting up Gmail SMTP configuration..."

# Set environment variables
export EMAIL_DEBUG=false
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your_email@gmail.com
export SMTP_PASSWORD=your_16_character_app_password
export FROM_EMAIL=your_email@gmail.com
export FROM_NAME="StructuredDocs Review System"

echo "Gmail SMTP configured. Run 'source setup_gmail_smtp.sh' to activate."
echo ""
echo "To get a Gmail App Password:"
echo "1. Go to https://myaccount.google.com/security"
echo "2. Enable 2-Step Verification if not already enabled"
echo "3. Go to App passwords and generate one for 'StructuredDocs'"
echo "4. Update SMTP_USERNAME and SMTP_PASSWORD above with your credentials"
