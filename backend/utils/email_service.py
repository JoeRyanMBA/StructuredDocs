"""
Email service for sending review notifications
"""
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from typing import Optional

try:
    import requests  # Used for provider HTTP APIs (Postmark, Resend)
except Exception:  # pragma: no cover - only needed if provider HTTP path is used
    requests = None

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration - can be set via environment variables
        def _clean(key, default=None):
            v = os.getenv(key, default)
            if isinstance(v, str):
                # Strip surrounding quotes and whitespace if present
                v = v.strip().strip("'\"")
            return v

        # SMTP config
        self.smtp_server = (_clean('SMTP_SERVER', 'localhost') or 'localhost')
        self.smtp_port = int(str(_clean('SMTP_PORT', '587') or '587'))
        self.smtp_username = (_clean('SMTP_USERNAME', '') or '')
        self.smtp_password = (_clean('SMTP_PASSWORD', '') or '')
        # From branding
        self.from_email = (_clean('FROM_EMAIL', 'noreply@structureddocs.local') or 'noreply@structureddocs.local')
        self.from_name = (_clean('FROM_NAME', 'StructuredDocs Review System') or 'StructuredDocs Review System')
        # Optional provider-based sending (avoids SMTP deliverability hassles)
        self.provider = (os.getenv('EMAIL_PROVIDER', '') or '').strip().lower()  # e.g., 'postmark' or 'resend'
        self.postmark_token = _clean('POSTMARK_API_TOKEN', '')
        self.postmark_message_stream = _clean('POSTMARK_MESSAGE_STREAM', 'outbound') or 'outbound'
        self.resend_api_key = _clean('RESEND_API_KEY', '')
        # Email debug settings
        self.debug_mode = (os.getenv('EMAIL_DEBUG', 'false') or 'false').strip().lower() == 'true'
        # Default debug email directory
        self.debug_email_dir = os.path.join(os.getcwd(), 'backend', 'debug_emails')

    def reload_config(self):
        """Reload configuration from environment variables"""
        def _clean(key, default=None):
            v = os.getenv(key, default)
            if isinstance(v, str):
                v = v.strip().strip("'\"")
            return v

        # SMTP config
        self.smtp_server = (_clean('SMTP_SERVER', 'localhost') or 'localhost')
        self.smtp_port = int(str(_clean('SMTP_PORT', '587') or '587'))
        self.smtp_username = (_clean('SMTP_USERNAME', '') or '')
        self.smtp_password = (_clean('SMTP_PASSWORD', '') or '')
        # From branding
        self.from_email = (_clean('FROM_EMAIL', 'noreply@structureddocs.local') or 'noreply@structureddocs.local')
        self.from_name = (_clean('FROM_NAME', 'StructuredDocs Review System') or 'StructuredDocs Review System')
        # Provider config
        self.provider = (os.getenv('EMAIL_PROVIDER', '') or '').strip().lower()
        self.postmark_token = _clean('POSTMARK_API_TOKEN', '')
        self.postmark_message_stream = _clean('POSTMARK_MESSAGE_STREAM', 'outbound') or 'outbound'
        self.resend_api_key = _clean('RESEND_API_KEY', '')
        # Debug
        self.debug_mode = (os.getenv('EMAIL_DEBUG', 'false') or 'false').strip().lower() == 'true'
        # Set debug email directory relative to current working directory
        self.debug_email_dir = os.path.join(os.getcwd(), 'backend', 'debug_emails')
        
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
                           is_sequential=False, sequence_position=None, total_reviewers=None):
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
                author_message, is_sequential, sequence_position, total_reviewers
            )
            
            # Create text content
            text_content = self._create_review_request_email_text(
                reviewer_name, topic_title, author_name, due_date, review_url,
                author_message, is_sequential, sequence_position, total_reviewers
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
                return True
            # If provider configured but failed, fall back to SMTP as secondary path
            logger.warning("Provider email sending failed; falling back to SMTP")

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject

            # Some SMTP providers (e.g., Gmail) require the From address to match the authenticated user
            from_addr = self.from_email
            if self.smtp_username and (
                'gmail' in (self.smtp_server or '').lower() or 'google' in (self.smtp_server or '').lower()
            ):
                if self.smtp_username != self.from_email:
                    # Use SMTP username as the From to pass provider checks
                    from_addr = self.smtp_username
                    # Preserve branding via Reply-To so replies go to branded address
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
            return True

        except Exception as e:
            logger.error(
                f"SMTP error sending email to {to_email}: {str(e)} | "
                f"server={self.smtp_server}:{self.smtp_port}, from={self.from_email}"
            )
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
                    logger.error("POSTMARK_API_TOKEN not set")
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
                logger.error(f"Postmark send failed {resp.status_code}: {resp.text}")
                return False

            if provider == 'resend':
                if not self.resend_api_key:
                    logger.error("RESEND_API_KEY not set")
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
                logger.error(f"Resend send failed {resp.status_code}: {resp.text}")
                return False

            logger.error(f"Unsupported EMAIL_PROVIDER: {provider}")
            return False
        except Exception as e:
            logger.error(f"Provider send error ({provider}) to {to_email}: {str(e)}")
            return False

    def send_test_email(self, to_email: str, base_url: str | None = None) -> bool:
        """Send a simple test email to verify SMTP configuration.

        This does not expose secrets and uses the current configuration.
        """
        try:
            if base_url is None:
                base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')

            subject = "StructuredDocs Test Email"
            html_content = f"""
            <html>
            <body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\"> 
                <h2>StructuredDocs Email Test</h2>
                <p>This is a test email to confirm SMTP delivery from StructuredDocs.</p>
                <ul>
                    <li>From: {self.from_name} &lt;{self.from_email}&gt;</li>
                    <li>Server: {self.smtp_server}:{self.smtp_port}</li>
                </ul>
                <p>You can visit the app here: <a href=\"{base_url}\">{base_url}</a></p>
                <p>Timestamp: {datetime.now().isoformat()}</p>
            </body>
            </html>
            """
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
                                         is_sequential=False, sequence_position=None, total_reviewers=None):
        """Create HTML email content for review request"""
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
            sequential_text = f"""
            <p><strong>Sequential Review:</strong> This is step {sequence_position} of {total_reviewers} in a sequential review process.</p>
            """
        
        # Author message
        message_section = ""
        if author_message:
            message_section = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #00796B; margin: 20px 0;">
                <h4>Message from {author_name}:</h4>
                <p>{author_message}</p>
            </div>
            """
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Review Request</h2>
            
            <p>Hello {reviewer_name},</p>
            
            <p>You have been requested to review the following topic:</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">{topic_title}</h3>
                <p><strong>Requested by:</strong> {author_name}</p>
                <p><strong>Due Date:</strong> {due_date_str}</p>
            </div>
            
            {sequential_text}
            {message_section}
            
            <p>To access the review, please click the link below:</p>
            <p><a href="{review_url}" style="background-color: #00796B; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Access Review</a></p>
            
            <p>Thank you for your time and expertise.</p>
            
            <p>Best regards,<br>
            StructuredDocs Review System</p>
        </body>
        </html>
        """
    
    def _create_review_request_email_text(self, reviewer_name, topic_title, author_name, 
                                         due_date, review_url, author_message="",
                                         is_sequential=False, sequence_position=None, total_reviewers=None):
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
            sequential_text = f"\nSequential Review: This is step {sequence_position} of {total_reviewers} in a sequential review process.\n"
        
        # Author message
        message_section = ""
        if author_message:
            message_section = f"\n--- Message from {author_name} ---\n{author_message}\n--- End Message ---\n"
        
        return f"""
Review Request

Hello {reviewer_name},

You have been requested to review the following topic:

Title: {topic_title}
Requested by: {author_name}
Due Date: {due_date_str}
{sequential_text}{message_section}
To access the review, please visit:
{review_url}

Thank you for your time and expertise.

Best regards,
StructuredDocs Review System
"""
    
    def _create_review_email_html(self, reviewer_name, topic_title, topic_id, author_message, 
                                 due_date, priority, review_url):
        """Create HTML email content for review notification"""
        # Handle due_date formatting - convert string to datetime if needed
        if isinstance(due_date, str):
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
                formatted_due_date = due_date_obj.strftime('%B %d, %Y')
            except:
                formatted_due_date = due_date
        else:
            formatted_due_date = due_date.strftime('%B %d, %Y') if due_date else 'Not specified'
            
        return f"""
        <html>
        <body>
            <h2>Review Request</h2>
            <p>Hello {reviewer_name},</p>
            
            <p>You have been requested to review the following document:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #00796B;">
                <h3>Topic #{topic_id}: {topic_title}</h3>
                <p><strong>Priority:</strong> {priority.title()}</p>
                <p><strong>Due Date:</strong> {formatted_due_date}</p>
                {f'<p><strong>Message from Author:</strong></p><p>{author_message}</p>' if author_message else ''}
            </div>
            
            <p>Please click the link below to access the review portal:</p>
            <p><a href="{review_url}" style="background-color: #00796B; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Start Review</a></p>
            
            <p>Or copy and paste this URL into your browser:<br>
            <code>{review_url}</code></p>
            
            <p>Thank you for your time and expertise.</p>
            
            <p>Best regards,<br>
            StructuredDocs Review System</p>
        </body>
        </html>
        """
    
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
    
    def _create_reminder_email_html(self, reviewer_name, topic_title, due_date, review_url, is_follow_up=False):
        """Create HTML email content for review reminder"""
        reminder_text = "This is a follow-up reminder" if is_follow_up else "This is a friendly reminder"
        
        return f"""
        <html>
        <body>
            <h2>Review Reminder</h2>
            <p>Hello {reviewer_name},</p>
            
            <p>{reminder_text} that you have a pending review:</p>
            
            <div style="background-color: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107;">
                <h3>{topic_title}</h3>
                <p><strong>Due Date:</strong> {due_date.strftime('%B %d, %Y')}</p>
            </div>
            
            <p>Please click the link below to access the review portal:</p>
            <p><a href="{review_url}" style="background-color: #ffc107; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Complete Review</a></p>
            
            <p>Or copy and paste this URL into your browser:<br>
            <code>{review_url}</code></p>
            
            <p>Thank you for your time and expertise.</p>
            
            <p>Best regards,<br>
            StructuredDocs Review System</p>
        </body>
        </html>
        """
    
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

    def _create_password_setup_email_html(self, user_name, setup_url, created_by_admin=True, admin_name=None):
        """Create HTML email content for password setup"""
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        
        if created_by_admin and admin_name:
            intro = f"An administrator ({admin_name}) has created an account for you on StructuredDocs."
        elif created_by_admin:
            intro = "An administrator has created an account for you on StructuredDocs."
        else:
            intro = "Welcome to StructuredDocs! Your account has been created."
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Welcome to StructuredDocs</h2>
            
            <p>{greeting}</p>
            
            <p>{intro}</p>
            
            <div style="background-color: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2e7d32;">Set Your Password</h3>
                <p>To complete your account setup and start using StructuredDocs, you need to create a password.</p>
            </div>
            
            <p>Click the link below to set your password:</p>
            <p><a href="{setup_url}" style="background-color: #00796B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Set My Password</a></p>
            
            <p>Or copy and paste this URL into your browser:<br>
            <code style="background-color: #f8f9fa; padding: 5px; border-radius: 3px;">{setup_url}</code></p>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p><strong>Important:</strong> This link will expire in 24 hours for security reasons. If the link expires, please contact an administrator to resend the setup email.</p>
            </div>
            
            <h3>About StructuredDocs</h3>
            <p>StructuredDocs is a collaborative documentation platform that helps teams create, review, and manage structured documents. Once you set your password, you'll be able to:</p>
            <ul>
                <li>Create and edit documents and topics</li>
                <li>Participate in collaborative review processes</li>
                <li>Manage projects and collections</li>
                <li>Track document workflows and approvals</li>
            </ul>
            
            <p>If you have any questions or need assistance, please contact your system administrator.</p>
            
            <p>Best regards,<br>
            StructuredDocs Team</p>
        </body>
        </html>
        """

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

    def _create_password_reset_email_html(self, user_name, reset_url):
        """Create HTML email content for password reset"""
        greeting = f"Hello {user_name}," if user_name else "Hello,"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Password Reset Request</h2>
            
            <p>{greeting}</p>
            
            <p>We received a request to reset your password for your StructuredDocs account.</p>
            
            <div style="background-color: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #856404;">Reset Your Password</h3>
                <p>Click the link below to create a new password for your account.</p>
            </div>
            
            <p><a href="{reset_url}" style="background-color: #ffc107; color: black; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset My Password</a></p>
            
            <p>Or copy and paste this URL into your browser:<br>
            <code style="background-color: #f8f9fa; padding: 5px; border-radius: 3px;">{reset_url}</code></p>
            
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc3545;">
                <p><strong>Security Notice:</strong></p>
                <ul>
                    <li>This link will expire in 1 hour for security reasons</li>
                    <li>If you didn't request this password reset, please ignore this email</li>
                    <li>Your password won't be changed until you click the link and set a new one</li>
                </ul>
            </div>
            
            <p>If you continue to have problems accessing your account, please contact your system administrator.</p>
            
            <p>Best regards,<br>
            StructuredDocs Team</p>
        </body>
        </html>
        """

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
