import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(to_email: str, subject: str, content: str, html_content: str | None = None):
    """
    Send an email using SendGrid.
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        content (str): Email body (plain text)
        html_content (str|None): Optional HTML body
    Returns:
        response: SendGrid response object or None on failure
    """
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@structureddocs.online')

    if not api_key:
        raise ValueError("SENDGRID_API_KEY not set in environment variables.")
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        return None
