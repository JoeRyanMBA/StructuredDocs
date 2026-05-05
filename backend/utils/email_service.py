"""Email service for sending various application emails (review, setup, reset).

Supports two delivery modes:
1. Provider HTTP API when EMAIL_PROVIDER is set to a supported provider.
2. SMTP delivery (STARTTLS or SSL) when no provider is chosen or EMAIL_PROVIDER=smtp.

Includes a debug mode (EMAIL_DEBUG=true) that writes emails to files instead.
"""

import smtplib
import ssl
import os
from email.utils import parseaddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from typing import Optional

try:  # Optional dependency for provider APIs
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # Fallback: provider mode will log an error if used

logger = logging.getLogger(__name__)


def _clean_env(key: str, default: Optional[str] = None) -> str:
    """Fetch and normalize an environment variable (strip quotes/whitespace)."""
    v = os.getenv(key, default)
    if isinstance(v, str):
        v = v.strip().strip("'\"")
    return v or ""


def _normalize_email_provider(value: Optional[str]) -> str:
    """Normalize EMAIL_PROVIDER so SMTP aliases use the native SMTP path."""
    provider = (value or '').strip().strip("'\"").lower()
    if provider in ('', 'smtp', 'sendgrid'):
        return ''
    return provider


def _first_nonempty_env(*keys: str, default: str = '') -> str:
    """Return the first non-empty env value among candidate keys."""
    for key in keys:
        v = _clean_env(key, '')
        if v:
            return v
    return default


def _extract_sender_email(value: str) -> str:
    """Extract bare email from values like 'Name <user@example.com>'."""
    _, addr = parseaddr(value or '')
    return (addr or '').strip()


class EmailService:
    # Class-level annotation (acceptable to static analyzers)
    last_error: Optional[str] = None

    def __init__(self) -> None:
        # SMTP configuration
        self.smtp_server = _first_nonempty_env('SMTP_SERVER', 'SMTP_HOST', default='localhost') or 'localhost'
        self.smtp_port = int(_clean_env('SMTP_PORT', '587') or '587')
        self.smtp_username = _first_nonempty_env('SMTP_USERNAME', 'SMTP_USER', default='')
        self.smtp_password = _clean_env('SMTP_PASSWORD', '')

        # From / branding
        self.from_email = _clean_env('FROM_EMAIL', 'noreply@structureddocs.local') or 'noreply@structureddocs.local'
        # Fallback to DEFAULT_FROM_EMAIL if FROM_EMAIL isn't set correctly
        default_from_email = _clean_env('DEFAULT_FROM_EMAIL', '')
        if not default_from_email:
            default_from_email = _extract_sender_email(_clean_env('MAIL_DEFAULT_SENDER', ''))
        if (not self.from_email or self.from_email.endswith('.local')) and default_from_email:
            self.from_email = default_from_email

        self.from_name = _clean_env('FROM_NAME', 'StructuredDocs Review System') or 'StructuredDocs Review System'
        # Optional fallback for name
        default_from_name = _clean_env('DEFAULT_FROM_NAME', '')
        if default_from_name:
            self.from_name = self.from_name or default_from_name

        # Provider (HTTP) configuration
        self.provider = _normalize_email_provider(os.getenv('EMAIL_PROVIDER'))  # 'postmark' | 'resend'
        self.postmark_token = _clean_env('POSTMARK_API_TOKEN', '')
        self.postmark_message_stream = _clean_env('POSTMARK_MESSAGE_STREAM', 'outbound') or 'outbound'
        self.resend_api_key = _clean_env('RESEND_API_KEY', '')

        # Debug mode
        self.debug_mode = os.getenv('EMAIL_DEBUG', 'false').strip().lower() == 'true'
        self.debug_email_dir = os.path.join(os.getcwd(), 'backend', 'debug_emails')

        # Reset last error
        self.last_error = None

    def reload_config(self) -> None:
        """Reload environment-driven configuration at runtime."""
        self.smtp_server = _first_nonempty_env('SMTP_SERVER', 'SMTP_HOST', default='localhost') or 'localhost'
        self.smtp_port = int(_clean_env('SMTP_PORT', '587') or '587')
        self.smtp_username = _first_nonempty_env('SMTP_USERNAME', 'SMTP_USER', default='')
        self.smtp_password = _clean_env('SMTP_PASSWORD', '')
        self.from_email = _clean_env('FROM_EMAIL', 'noreply@structureddocs.local') or 'noreply@structureddocs.local'
        default_from_email = _clean_env('DEFAULT_FROM_EMAIL', '')
        if not default_from_email:
            default_from_email = _extract_sender_email(_clean_env('MAIL_DEFAULT_SENDER', ''))
        if (not self.from_email or self.from_email.endswith('.local')) and default_from_email:
            self.from_email = default_from_email

        self.from_name = _clean_env('FROM_NAME', 'StructuredDocs Review System') or 'StructuredDocs Review System'
        default_from_name = _clean_env('DEFAULT_FROM_NAME', '')
        if default_from_name:
            self.from_name = self.from_name or default_from_name
        self.provider = _normalize_email_provider(os.getenv('EMAIL_PROVIDER'))
        self.postmark_token = _clean_env('POSTMARK_API_TOKEN', '')
        self.postmark_message_stream = _clean_env('POSTMARK_MESSAGE_STREAM', 'outbound') or 'outbound'
        self.resend_api_key = _clean_env('RESEND_API_KEY', '')
        self.debug_mode = os.getenv('EMAIL_DEBUG', 'false').strip().lower() == 'true'
        self.debug_email_dir = os.path.join(os.getcwd(), 'backend', 'debug_emails')
        self.last_error = None

    # ── Shared layout helpers ────────────────────────────────────────────

    def _get_base_url(self, base_url=None):
        return (base_url or os.getenv('FRONTEND_URL', 'http://localhost:5173')).rstrip('/')

    def _email_layout(self, title: str, body: str, base_url: str = None) -> str:
        """Return a full branded HTML email wrapping *body* with the logo header and footer."""
        base = self._get_base_url(base_url)
        logo_url = f'{base}/StructuredDocs_logo.svg'
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0f4f5;font-family:Arial,sans-serif;color:#333;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f5;padding:24px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
        <tr>
          <td style="padding:20px 28px 12px;">
            <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
              <tr>
                <td valign="middle" align="left" style="width:220px;padding-right:16px;">
                  <img src="{logo_url}" alt="StructuredDocs" height="36"
                       style="display:block;max-width:220px;" />
                </td>
                <td valign="middle" align="right">
                  <p style="color:#1f2933;margin:0;font-size:20px;font-weight:600;">{title}</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="background:#fff;padding:28px;border:1px solid #dee2e6;border-radius:8px;">
            {body}
          </td>
        </tr>
        <tr>
          <td style="padding:16px 0;text-align:center;color:#6c757d;font-size:12px;">
            StructuredDocs &mdash; Collaborative Documentation Platform
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    @staticmethod
    def _cta_button(label: str, url: str, color: str = '#008C9E') -> str:
        """Return a branded call-to-action button for use inside email body HTML."""
        return (
            f'<div style="text-align:center;margin:28px 0;">'
            f'<a href="{url}" style="background:{color};color:#fff;padding:13px 28px;'
            f'text-decoration:none;border-radius:6px;font-weight:bold;font-size:15px;">'
            f'{label}</a></div>'
        )

    @staticmethod
    def _fallback_link(url: str) -> str:
        return (
            f'<p style="color:#6c757d;font-size:12px;margin-top:4px;">'
            f'If the button above does not work, copy this link into your browser:<br>'
            f'<a href="{url}" style="color:#008C9E;">{url}</a></p>'
        )

    def send_review_notification(self, reviewer_email, reviewer_name, topic_title,
                                topic_id, author_message, due_date, priority,
                                review_token, base_url=None):
        """Send review notification email to reviewer"""
        try:
            if base_url is None:
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            
            review_url = f"{base_url}/review/{review_token}"
            
            subject = f"Review Request: {topic_title} (Topic #{topic_id})"
            
            html_content = self._create_review_email_html(
                reviewer_name, topic_title, topic_id, author_message, due_date, 
                priority, review_url
            )
            
            text_content = self._create_review_email_text(
                reviewer_name, topic_title, topic_id, author_message, due_date, 
                priority, review_url
            )
            
            return self._send_email(reviewer_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send review notification: {str(e)}")
            return False
    
    def send_bulk_review_notification(self, reviewer_email, reviewer_name, topic_titles,
                                      author_message, due_date, priority, batch_token,
                                      base_url=None):
        """Send a single digest email for a bulk review batch."""
        try:
            if base_url is None:
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')

            portal_url = f"{base_url}/bulk-review/{batch_token}"
            n = len(topic_titles)
            subject = f"Review Request: {n} Topic{'s' if n != 1 else ''} Assigned for Review"

            html_content = self._create_bulk_review_email_html(
                reviewer_name, topic_titles, author_message, due_date, priority, portal_url,
                base_url=base_url
            )
            text_content = self._create_bulk_review_email_text(
                reviewer_name, topic_titles, author_message, due_date, priority, portal_url
            )

            return self._send_email(reviewer_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send bulk review notification: {str(e)}")
            return False

    def _create_bulk_review_email_html(self, reviewer_name, topic_titles, author_message,
                                       due_date, priority, portal_url, base_url=None):
        due_str = due_date.strftime('%B %d, %Y') if due_date else 'No deadline set'
        priority_colors = {'urgent': '#dc3545', 'high': '#fd7e14', 'medium': '#008C9E', 'low': '#6c757d'}
        priority_color = priority_colors.get(priority or 'medium', '#008C9E')

        topics_html = ''.join(
            f'<li style="padding:4px 0;">{i + 1}. {title}</li>'
            for i, title in enumerate(topic_titles)
        )

        message_block = (
            f'<div style="background:#f0f9f9;border-left:4px solid #008C9E;padding:12px 16px;'
            f'margin:16px 0;border-radius:4px;">'
            f'<strong>Message from requester:</strong><br>{author_message}</div>'
            if author_message else ''
        )

        body = f"""
    <p>Hello {reviewer_name},</p>
    <p>You have been assigned <strong>{len(topic_titles)} topic{'s' if len(topic_titles) != 1 else ''}</strong> for review.</p>
    <div style="background:#f8f9fa;padding:16px;border-radius:6px;margin:16px 0;">
      <p style="margin:0 0 8px;font-weight:bold;">Topics to Review:</p>
      <ul style="margin:0;padding-left:20px;">{topics_html}</ul>
    </div>
    <p><strong>Priority:</strong> <span style="color:{priority_color};font-weight:bold;">{(priority or 'medium').upper()}</span></p>
    <p><strong>Due Date:</strong> {due_str}</p>
    {message_block}
    {self._cta_button('Open Review Portal', portal_url)}
    <p style="color:#6c757d;font-size:13px;">The portal lets you navigate between topics, leave feedback, and track your progress in one place.</p>
    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
    {self._fallback_link(portal_url)}"""

        return self._email_layout(f'Review Request: {len(topic_titles)} Topics', body, base_url)

    def _create_bulk_review_email_text(self, reviewer_name, topic_titles, author_message,
                                       due_date, priority, portal_url):
        due_str = due_date.strftime('%B %d, %Y') if due_date else 'No deadline set'
        topics_text = '\n'.join(f'  {i + 1}. {t}' for i, t in enumerate(topic_titles))
        message_block = f'\nMessage from requester:\n  {author_message}\n' if author_message else ''
        return (
            f"Hello {reviewer_name},\n\n"
            f"You have been assigned {len(topic_titles)} topic(s) for review.\n\n"
            f"Topics to Review:\n{topics_text}\n\n"
            f"Priority: {(priority or 'medium').upper()}\n"
            f"Due Date: {due_str}\n"
            f"{message_block}\n"
            f"Open your review portal here:\n{portal_url}\n\n"
            f"The portal lets you navigate between topics, leave feedback, and track your progress."
        )

    def send_review_reminder(self, reviewer_email, reviewer_name, topic_title, 
                           due_date, review_token, base_url=None, is_follow_up=False):
        """Send reminder email for pending review"""
        try:
            if base_url is None:
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            
            review_url = f"{base_url}/review/{review_token}"
            
            # Add "Second Request:" prefix for follow-ups
            subject_prefix = "Second Request: " if is_follow_up else ""
            subject = f"{subject_prefix}Review Reminder: {topic_title}"
            
            html_content = self._create_reminder_email_html(
                reviewer_name, topic_title, due_date, review_url, is_follow_up
            )
            
            text_content = self._create_reminder_email_text(
                reviewer_name, topic_title, due_date, review_url, is_follow_up
            )
            
            return self._send_email(reviewer_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send review reminder: {str(e)}")
            return False
    
    def send_review_request(self, reviewer_email, reviewer_name, topic_title, 
                           author_name, due_date, review_url, author_message="", 
                           is_sequential=False, sequence_position=None, total_reviewers=None, topic_id=None):
        """Send review request email to reviewer (for sequential reviews and direct requests)"""
        try:
            # Construct full URL if only a path is provided
            if review_url.startswith('/'):
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
                review_url = f"{base_url}{review_url}"
            
            # Construct subject based on whether it's sequential
            if is_sequential and sequence_position and total_reviewers:
                subject = f"Sequential Review Request (Step {sequence_position} of {total_reviewers}): {topic_title}"
            else:
                subject = f"Review Request: {topic_title}"
            
            # Create HTML content
            html_content = self._create_review_request_email_html(
                reviewer_name, topic_title, author_name, due_date, review_url,
                author_message, is_sequential, sequence_position, total_reviewers, topic_id,
                base_url=self._get_base_url()
            )
            
            # Create text content
            text_content = self._create_review_request_email_text(
                reviewer_name, topic_title, author_name, due_date, review_url,
                author_message, is_sequential, sequence_position, total_reviewers, topic_id
            )
            
            return self._send_email(reviewer_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send review request: {str(e)}")
            return False

    def send_password_setup_email(self, user_email, user_name, setup_url, 
                                 created_by_admin=True, admin_name=None):
        """Send password setup email to new users"""
        try:
            subject = "Welcome to StructuredDocs - Set Your Password"
            
            html_content = self._create_password_setup_email_html(
                user_name, setup_url, created_by_admin, admin_name
            )
            
            text_content = self._create_password_setup_email_text(
                user_name, setup_url, created_by_admin, admin_name
            )
            
            return self._send_email(user_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send password setup email: {str(e)}")
            return False

    def send_password_reset_email(self, user_email, user_name, reset_url):
        """Send password reset email to existing users"""
        try:
            subject = "StructuredDocs Password Reset Request"
            
            html_content = self._create_password_reset_email_html(
                user_name, reset_url
            )
            
            text_content = self._create_password_reset_email_text(
                user_name, reset_url
            )
            
            return self._send_email(user_email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    def _send_email(self, to_email, subject, html_content, text_content):
        """Send email via provider HTTP API if configured; otherwise use SMTP or debug mode"""
        # Only use debug mode when explicitly enabled; do not default to True
        if self.debug_mode:
            # In debug mode, just log the email content
            logger.info("=== EMAIL DEBUG MODE ===")
            logger.info(f"To: {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info("--- EMAIL CONTENT ---")
            logger.info(text_content)
            logger.info("=== END EMAIL ===")

            # Also write to a file for easy access
            self._write_debug_email(to_email, subject, text_content)
            return True

        # Try provider-based delivery first if configured
        if self.provider:
            ok = self._send_via_provider(to_email, subject, html_content, text_content)
            if ok:
                self.last_error = None
                return True
            # If provider configured but failed, fall back to SMTP as secondary path
            logger.warning("Provider email sending failed; falling back to SMTP")

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject

            # Many SMTP providers require the From address to match the authenticated user.
            # When SMTP_USERNAME is set and differs from FROM_EMAIL, use the username as
            # the envelope From and preserve branding via Reply-To.
            from_addr = self.from_email
            if self.smtp_username and self.smtp_username != self.from_email:
                from_addr = self.smtp_username
                # Keep branded address as Reply-To so replies still reach the intended inbox
                msg['Reply-To'] = self.from_email

            msg['From'] = f"{self.from_name} <{from_addr}>"
            msg['To'] = to_email

            # Add both text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            use_ssl = (self.smtp_port == 465) or (os.getenv('SMTP_USE_SSL', 'false').lower() == 'true')
            if use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context)
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                # Optional STARTTLS for ports like 587
                if self.smtp_username and self.smtp_password:
                    try:
                        server.starttls()
                    except Exception:
                        # If STARTTLS is not supported, proceed without it
                        pass
                    server.login(self.smtp_username, self.smtp_password)

            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            self.last_error = None
            return True

        except Exception as e:
            logger.error(
                f"SMTP error sending email to {to_email}: {str(e)} | "
                f"server={self.smtp_server}:{self.smtp_port}, from={self.from_email}"
            )
            self.last_error = f"SMTP error: {e}"
            return False

    def _send_via_provider(self, to_email: str, subject: str, html_content: str, text_content: str) -> bool:
        """Send email using a transactional provider HTTP API.

        Supported providers: postmark, resend
        """
        provider = (self.provider or '').lower()
        if not provider:
            return False
        if requests is None:
            logger.error("requests not available; install it or disable EMAIL_PROVIDER")
            return False

        try:
            if provider == 'postmark':
                if not self.postmark_token:
                    msg = "POSTMARK_API_TOKEN not set"
                    logger.error(msg)
                    self.last_error = msg
                    return False
                url = 'https://api.postmarkapp.com/email'
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Postmark-Server-Token': self.postmark_token,
                }
                payload = {
                    'From': f"{self.from_name} <{self.from_email}>",
                    'To': to_email,
                    'Subject': subject,
                    'HtmlBody': html_content,
                    'TextBody': text_content,
                    'MessageStream': self.postmark_message_stream or 'outbound',
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code in (200, 201):
                    logger.info(f"Postmark: email sent to {to_email}")
                    return True
                msg = f"Postmark failure {resp.status_code}: {resp.text}".strip()
                logger.error(msg)
                self.last_error = msg
                return False

            if provider == 'resend':
                if not self.resend_api_key:
                    msg = "RESEND_API_KEY not set"
                    logger.error(msg)
                    self.last_error = msg
                    return False
                url = 'https://api.resend.com/emails'
                headers = {
                    'Authorization': f"Bearer {self.resend_api_key}",
                    'Content-Type': 'application/json',
                }
                payload = {
                    'from': f"{self.from_name} <{self.from_email}>",
                    'to': [to_email],
                    'subject': subject,
                    'html': html_content,
                    'text': text_content,
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code in (200, 201):
                    logger.info(f"Resend: email sent to {to_email}")
                    return True
                msg = f"Resend failure {resp.status_code}: {resp.text}".strip()
                logger.error(msg)
                self.last_error = msg
                return False

            logger.error(f"Unsupported EMAIL_PROVIDER: {provider}")
            self.last_error = f"Unsupported provider {provider}"
            return False
        except Exception as e:
            logger.error(f"Provider send error ({provider}) to {to_email}: {str(e)}")
            self.last_error = f"Provider error: {e}"
            return False

    # ------------------------------------------------------------------ #
    #  Task notifications                                                  #
    # ------------------------------------------------------------------ #

    def send_task_notification(self, to_email: str, to_name: str,
                               task_title: str, task_id: int,
                               changes: dict, actor_name: str,
                               base_url: Optional[str] = None) -> bool:
        """Send an email when a task is created (assigned) or key fields change.

        ``changes`` is a dict mapping field label → (old_value, new_value).
        For a new assignment pass ``changes={"Assigned to": (None, to_name)}``.
        """
        try:
            if base_url is None:
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')

            is_new = all(old is None for old, _ in changes.values())
            action = "assigned to you" if is_new else "updated"
            subject = f"Task {action}: {task_title}"

            html_content = self._create_task_notification_html(
                to_name, task_title, task_id, changes, actor_name, base_url, is_new
            )
            text_content = self._create_task_notification_text(
                to_name, task_title, task_id, changes, actor_name, base_url, is_new
            )
            return self._send_email(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send task notification: {e}")
            return False

    def _create_task_notification_html(self, to_name, task_title, task_id,
                                       changes, actor_name, base_url, is_new):
        header_title = "✅ New Task Assigned" if is_new else "🔔 Task Updated"
        action_text = "A task has been assigned to you" if is_new else "A task you are assigned to has been updated"

        rows_html = ""
        for label, (old_val, new_val) in changes.items():
            old_str = str(old_val) if old_val not in (None, "") else "—"
            new_str = str(new_val) if new_val not in (None, "") else "—"
            if is_new:
                rows_html += (
                    f'<tr><td style="padding:6px 12px;color:#6c757d;width:140px">{label}</td>'
                    f'<td style="padding:6px 12px"><strong>{new_str}</strong></td></tr>'
                )
            else:
                rows_html += (
                    f'<tr><td style="padding:6px 12px;color:#6c757d;width:140px">{label}</td>'
                    f'<td style="padding:6px 12px">'
                    f'<span style="text-decoration:line-through;color:#adb5bd">{old_str}</span>'
                    f' &rarr; <strong>{new_str}</strong></td></tr>'
                )

        body = f"""
    <p>Hello {to_name},</p>
    <p>{action_text} by <strong>{actor_name}</strong>.</p>
    <div style="background:#f8f9fa;border-radius:6px;margin:16px 0;overflow:hidden;border:1px solid #dee2e6;">
      <div style="background:#e9ecef;padding:8px 12px;font-weight:bold;">{task_title}</div>
      <table style="width:100%;border-collapse:collapse;font-size:0.9rem">
        {rows_html}
      </table>
    </div>
    <p style="color:#6c757d;font-size:13px;margin-top:24px;">
      Log in to StructuredDocs to view or update this task.
    </p>
    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
    <p style="color:#6c757d;font-size:12px;margin:0;">
      You are receiving this email because you are assigned to this task.
    </p>"""

        return self._email_layout(header_title, body, base_url)

    def _create_task_notification_text(self, to_name, task_title, task_id,
                                       changes, actor_name, base_url, is_new):
        action_text = "A task has been assigned to you" if is_new else "A task you are assigned to has been updated"
        lines = [
            f"Hello {to_name},",
            "",
            f"{action_text} by {actor_name}.",
            "",
            f"Task: {task_title}",
            "",
        ]
        for label, (old_val, new_val) in changes.items():
            old_str = str(old_val) if old_val not in (None, "") else "—"
            new_str = str(new_val) if new_val not in (None, "") else "—"
            if is_new:
                lines.append(f"  {label}: {new_str}")
            else:
                lines.append(f"  {label}: {old_str} → {new_str}")
        lines += ["", "Log in to StructuredDocs to view or update this task."]
        return "\n".join(lines)

    def send_test_email(self, to_email: str, base_url: str | None = None) -> bool:
        """Send a simple test email to verify SMTP configuration.

        This does not expose secrets and uses the current configuration.
        """
        try:
            if base_url is None:
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')

            subject = "StructuredDocs Test Email"
            body = f"""
    <p>This is a test email to confirm SMTP delivery from StructuredDocs.</p>
    <ul>
      <li><strong>From:</strong> {self.from_name} &lt;{self.from_email}&gt;</li>
      <li><strong>Server:</strong> {self.smtp_server}:{self.smtp_port}</li>
    </ul>
    <p>You can visit the app here: <a href="{base_url}" style="color:#008C9E;">{base_url}</a></p>
    <p style="color:#6c757d;font-size:13px;">Timestamp: {datetime.now().isoformat()}</p>"""
            html_content = self._email_layout('Email Configuration Test', body, base_url)
            text_content = (
                "StructuredDocs Email Test\n\n"
                f"From: {self.from_name} <{self.from_email}>\n"
                f"Server: {self.smtp_server}:{self.smtp_port}\n"
                f"Timestamp: {datetime.now().isoformat()}\n"
            )

            return self._send_email(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False

    def check_smtp_health(self) -> tuple[bool, dict]:
        """Validate SMTP connectivity/auth without sending a user-facing message."""
        provider = self.provider or 'smtp'
        if provider != 'smtp':
            detail = {
                'provider': provider,
                'checked': False,
                'reason': f"SMTP health check skipped because EMAIL_PROVIDER={provider}",
            }
            self.last_error = detail['reason']
            return False, detail

        use_ssl = (self.smtp_port == 465) or (os.getenv('SMTP_USE_SSL', 'false').lower() == 'true')
        auth_attempted = bool(self.smtp_username and self.smtp_password)
        tls_started = False
        server = None

        try:
            if use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context, timeout=10)
                tls_started = True
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                server.ehlo()
                try:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                    server.ehlo()
                    tls_started = True
                except Exception:
                    # Some providers/ports don't support STARTTLS; continue and let login/connect determine health.
                    tls_started = False

            if auth_attempted:
                server.login(self.smtp_username, self.smtp_password)

            self.last_error = None
            return True, {
                'provider': 'smtp',
                'checked': True,
                'server': self.smtp_server,
                'port': self.smtp_port,
                'useSSL': use_ssl,
                'tlsStarted': tls_started,
                'authAttempted': auth_attempted,
            }
        except Exception as e:
            self.last_error = f"SMTP health check error: {e}"
            return False, {
                'provider': 'smtp',
                'checked': True,
                'server': self.smtp_server,
                'port': self.smtp_port,
                'useSSL': use_ssl,
                'tlsStarted': tls_started,
                'authAttempted': auth_attempted,
                'error': str(e),
            }
        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    pass
    
    def _write_debug_email(self, to_email, subject, content):
        """Write email to debug file for development"""
        try:
            debug_dir = self.debug_email_dir
            os.makedirs(debug_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_email = to_email.replace('@', '_at_').replace('.', '_')
            filename = f"{timestamp}_{safe_email}.txt"
            
            with open(os.path.join(debug_dir, filename), 'w') as f:
                f.write(f"To: {to_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n")
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to write debug email: {str(e)}")
    
    def _create_review_request_email_html(self, reviewer_name, topic_title, author_name,
                                         due_date, review_url, author_message="",
                                         is_sequential=False, sequence_position=None,
                                         total_reviewers=None, topic_id=None, base_url=None):
        """Create HTML email content for review request"""
        due_date_str = 'Not specified'
        if due_date:
            if isinstance(due_date, str):
                try:
                    due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00')) \
                        if due_date.endswith('Z') else datetime.strptime(due_date, '%Y-%m-%d')
                    due_date_str = due_date_obj.strftime('%B %d, %Y')
                except ValueError:
                    due_date_str = due_date
            elif hasattr(due_date, 'strftime'):
                due_date_str = due_date.strftime('%B %d, %Y')

        sequential_block = ""
        if is_sequential and sequence_position and total_reviewers:
            sequential_block = (
                f'<p><strong>Sequential Review:</strong> This is step {sequence_position} '
                f'of {total_reviewers} in a sequential review process.</p>'
                '<p>The sequential review process gets feedback or approval from a '
                'Subject Matter Expert (SME) before other feedback. This step ensures '
                'any technical elements or procedures are correct before getting '
                'feedback or approval from other reviewers.</p>'
            )

        message_block = ""
        if author_message:
            message_block = (
                f'<div style="background:#f0f9f9;border-left:4px solid #008C9E;'
                f'padding:12px 16px;margin:16px 0;border-radius:4px;">'
                f'<strong>Message from {author_name}:</strong><br>{author_message}</div>'
            )

        topic_id_line = ""
        if topic_id:
            topic_id_line = f'<p style="margin:4px 0;"><strong>Topic ID:</strong> {topic_id}</p>'
        
        body = f"""
    <p>Hello {reviewer_name},</p>
    <p>You have been requested to review the following topic:</p>
    <div style="background:#f8f9fa;padding:16px;border-radius:6px;margin:16px 0;">
      <p style="margin:0 0 6px;font-weight:bold;font-size:1.05em;">{topic_title}</p>
      <p style="margin:4px 0;"><strong>Requested by:</strong> {author_name}</p>
      <p style="margin:4px 0;"><strong>Due Date:</strong> {due_date_str}</p>
      {topic_id_line}
    </div>
    {sequential_block}
    {message_block}
    {self._cta_button('Start Review', review_url)}
    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
    {self._fallback_link(review_url)}
    <p style="color:#6c757d;font-size:13px;margin-top:16px;">
      Thank you for your time and expertise.<br>StructuredDocs Review System
    </p>"""

        return self._email_layout('Review Request', body, base_url)
    
    def _create_review_request_email_text(self, reviewer_name, topic_title, author_name, 
                                         due_date, review_url, author_message="",
                                         is_sequential=False, sequence_position=None, total_reviewers=None, topic_id=None):
        """Create plain text email content for review request"""
        due_date_str = 'Not specified'
        if due_date:
            if isinstance(due_date, str):
                try:
                    # Handle ISO format with 'Z'
                    if due_date.endswith('Z'):
                        due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    else:
                        # Handle other common date formats
                        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                    due_date_str = due_date_obj.strftime('%B %d, %Y')
                except ValueError:
                    due_date_str = due_date # Fallback to original string
            elif hasattr(due_date, 'strftime'):
                due_date_str = due_date.strftime('%B %d, %Y')

        # Sequential review specific text
        sequential_text = ""
        if is_sequential and sequence_position and total_reviewers:
            sequential_text = (
                f"\nSequential Review: This is step {sequence_position} of {total_reviewers} "
                "in a sequential review process.\n"
                "The sequential review process gets feedback or approval from a "
                "Subject Matter Expert (SME) before other feedback. This step ensures "
                "any technical elements or procedures are correct before getting "
                "feedback or approval from other reviewers.\n"
            )
        
        # Author message
        message_section = ""
        if author_message:
            message_section = f"\n--- Message from {author_name} ---\n{author_message}\n--- End Message ---\n"
        
        topic_id_line = ""
        if topic_id:
            topic_id_line = f"Topic ID: {topic_id}\n"
        
        return f"""
Review Request

Hello {reviewer_name},

You have been requested to review the following topic:

Title: {topic_title}
Requested by: {author_name}
Due Date: {due_date_str}
{topic_id_line}{sequential_text}{message_section}
To access the review, please visit:
{review_url}

Thank you for your time and expertise.

Best regards,
StructuredDocs Review System
"""
    
    def _create_review_email_html(self, reviewer_name, topic_title, topic_id,
                                  author_message, due_date, priority, review_url,
                                  base_url=None):
        """Create HTML email content for review notification"""
        if isinstance(due_date, str):
            try:
                formatted_due_date = datetime.strptime(due_date, '%Y-%m-%d').strftime('%B %d, %Y')
            except Exception:
                formatted_due_date = due_date
        else:
            formatted_due_date = due_date.strftime('%B %d, %Y') if due_date else 'Not specified'

        message_block = (
            f'<p><strong>Message from Author:</strong></p><p>{author_message}</p>'
            if author_message else ''
        )

        body = f"""
    <p>Hello {reviewer_name},</p>
    <p>You have been requested to review the following document:</p>
    <div style="background:#f8f9fa;padding:16px;border-radius:6px;margin:16px 0;border-left:4px solid #008C9E;">
      <p style="margin:0 0 6px;font-weight:bold;font-size:1.05em;">Topic #{topic_id}: {topic_title}</p>
      <p style="margin:4px 0;"><strong>Priority:</strong> {priority.title()}</p>
      <p style="margin:4px 0;"><strong>Due Date:</strong> {formatted_due_date}</p>
      {message_block}
    </div>
    {self._cta_button('Start Review', review_url)}
    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
    {self._fallback_link(review_url)}
    <p style="color:#6c757d;font-size:13px;margin-top:16px;">
      Thank you for your time and expertise.<br>StructuredDocs Review System
    </p>"""

        return self._email_layout('Review Request', body, base_url)
    
    def _create_review_email_text(self, reviewer_name, topic_title, topic_id, author_message, 
                                 due_date, priority, review_url):
        """Create plain text email content for review notification"""
        # Handle due_date formatting - convert string to datetime if needed
        if isinstance(due_date, str):
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                formatted_due_date = due_date_obj.strftime('%B %d, %Y')
            except:
                formatted_due_date = due_date
        else:
            formatted_due_date = due_date.strftime('%B %d, %Y') if due_date else 'Not specified'
            
        content = f"""
Review Request

Hello {reviewer_name},

You have been requested to review the following document:

Topic #{topic_id}: {topic_title}
Priority: {priority.title()}
Due Date: {formatted_due_date}
"""
        
        if author_message:
            content += f"\nMessage from Author:\n{author_message}\n"
        
        content += f"""
Please access the review portal using this link:
{review_url}

Thank you for your time and expertise.

Best regards,
StructuredDocs Review System
"""
        return content
    
    def _create_reminder_email_html(self, reviewer_name, topic_title, due_date,
                                    review_url, is_follow_up=False, base_url=None):
        """Create HTML email content for review reminder"""
        reminder_text = "This is a follow-up reminder" if is_follow_up else "This is a friendly reminder"
        header_title = "⏰ Follow-up: Review Pending" if is_follow_up else "⏰ Review Reminder"

        body = f"""
    <p>Hello {reviewer_name},</p>
    <p>{reminder_text} that you have a pending review:</p>
    <div style="background:#fff8e1;padding:16px;border-radius:6px;margin:16px 0;border-left:4px solid #ffc107;">
      <p style="margin:0 0 6px;font-weight:bold;font-size:1.05em;">{topic_title}</p>
      <p style="margin:4px 0;"><strong>Due Date:</strong> {due_date.strftime('%B %d, %Y')}</p>
    </div>
    {self._cta_button('Complete Review', review_url)}
    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
    {self._fallback_link(review_url)}
    <p style="color:#6c757d;font-size:13px;margin-top:16px;">
      Thank you for your time and expertise.<br>StructuredDocs Review System
    </p>"""

        return self._email_layout(header_title, body, base_url)
    
    def _create_reminder_email_text(self, reviewer_name, topic_title, due_date, review_url, is_follow_up=False):
        """Create plain text email content for review reminder"""
        reminder_text = "This is a follow-up reminder" if is_follow_up else "This is a friendly reminder"
        
        return f"""
Review Reminder

Hello {reviewer_name},

{reminder_text} that you have a pending review:

Title: {topic_title}
Due Date: {due_date.strftime('%B %d, %Y')}

Please access the review portal using this link:
{review_url}

Thank you for your time and expertise.

Best regards,
StructuredDocs Review System
"""

    def _create_password_setup_email_html(self, user_name, setup_url,
                                          created_by_admin=True, admin_name=None,
                                          base_url=None):
        """Create HTML email content for password setup"""
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        if created_by_admin and admin_name:
            intro = f"An administrator ({admin_name}) has created an account for you on StructuredDocs."
        elif created_by_admin:
            intro = "An administrator has created an account for you on StructuredDocs."
        else:
            intro = "Welcome to StructuredDocs! Your account has been created."

        body = f"""
    <p>{greeting}</p>
    <p>{intro}</p>
    <div style="background:#f0f9f9;padding:16px;border-radius:6px;margin:16px 0;border-left:4px solid #008C9E;">
      <p style="margin:0 0 6px;font-weight:bold;color:#005B6E;">Set Your Password</p>
      <p style="margin:0;">To complete your account setup, you need to create a password.</p>
    </div>
    {self._cta_button('Set My Password', setup_url)}
    <div style="background:#fff8e1;padding:12px 16px;border-radius:6px;margin:16px 0;border-left:4px solid #ffc107;">
      <p style="margin:0;"><strong>Important:</strong> This link will expire in 24 hours.
      If it expires, please contact an administrator to resend the setup email.</p>
    </div>
    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
    {self._fallback_link(setup_url)}
    <p style="color:#6c757d;font-size:13px;margin-top:16px;">
      If you have any questions, please contact your system administrator.
    </p>"""

        return self._email_layout('Welcome to StructuredDocs', body, base_url)

    def _create_password_setup_email_text(self, user_name, setup_url, created_by_admin=True, admin_name=None):
        """Create plain text email content for password setup"""
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        
        if created_by_admin and admin_name:
            intro = f"An administrator ({admin_name}) has created an account for you on StructuredDocs."
        elif created_by_admin:
            intro = "An administrator has created an account for you on StructuredDocs."
        else:
            intro = "Welcome to StructuredDocs! Your account has been created."
        
        return f"""
Welcome to StructuredDocs

{greeting}

{intro}

SET YOUR PASSWORD
To complete your account setup and start using StructuredDocs, you need to create a password.

Click the link below to set your password:
{setup_url}

IMPORTANT: This link will expire in 24 hours for security reasons. If the link expires, please contact an administrator to resend the setup email.

ABOUT STRUCTUREDDOCS
StructuredDocs is a collaborative documentation platform that helps teams create, review, and manage structured documents. Once you set your password, you'll be able to:

- Create and edit documents and topics
- Participate in collaborative review processes  
- Manage projects and collections
- Track document workflows and approvals

If you have any questions or need assistance, please contact your system administrator.

Best regards,
StructuredDocs Team
"""

    def _create_password_reset_email_html(self, user_name, reset_url, base_url=None):
        """Create HTML email content for password reset"""
        greeting = f"Hello {user_name}," if user_name else "Hello,"

        body = f"""
    <p>{greeting}</p>
    <p>We received a request to reset your password for your StructuredDocs account.</p>
    {self._cta_button('Reset My Password', reset_url)}
    <div style="background:#fde8ea;padding:12px 16px;border-radius:6px;margin:16px 0;border-left:4px solid #dc3545;">
      <p style="margin:0;"><strong>Security Notice:</strong></p>
      <ul style="margin:6px 0 0;padding-left:20px;">
        <li>This link will expire in 1 hour</li>
        <li>If you didn't request this reset, you can safely ignore this email</li>
        <li>Your password won't change until you click the link and set a new one</li>
      </ul>
    </div>
    <hr style="border:none;border-top:1px solid #dee2e6;margin:20px 0;">
    {self._fallback_link(reset_url)}
    <p style="color:#6c757d;font-size:13px;margin-top:16px;">
      If you continue to have trouble accessing your account, contact your system administrator.
    </p>"""

        return self._email_layout('Password Reset Request', body, base_url)

    def _create_password_reset_email_text(self, user_name, reset_url):
        """Create plain text email content for password reset"""
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        
        return f"""
Password Reset Request

{greeting}

We received a request to reset your password for your StructuredDocs account.

To reset your password, click the link below:
{reset_url}

SECURITY NOTICE:
- This link will expire in 1 hour for security reasons
- If you didn't request this password reset, please ignore this email
- Your password won't be changed until you click the link and set a new one

If you continue to have problems accessing your account, please contact your system administrator.

Best regards,
StructuredDocs Team
"""

# Global email service instance - will be initialized with environment variables
email_service = None

def get_email_service():
    """Get or create the email service instance with current environment variables"""
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service

# For backward compatibility, also create an instance
email_service = EmailService()
