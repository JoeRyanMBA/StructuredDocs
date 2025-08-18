"""
Email service for sending review notifications
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Email configuration - can be set via environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@structureddocs.local')
        self.from_name = os.getenv('FROM_NAME', 'StructuredDocs Review System')
        
        # For development, we'll use a simple debug mode
        self.debug_mode = os.getenv('EMAIL_DEBUG', 'true').lower() == 'true'
        
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
    
    def _send_email(self, to_email, subject, html_content, text_content):
        """Send email using SMTP or debug mode"""
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
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add both text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.smtp_username and self.smtp_password:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
            return False
    
    def _write_debug_email(self, to_email, subject, content):
        """Write email to debug file for development"""
        try:
            debug_dir = "/workspaces/StructuredDocs/backend/debug_emails"
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
        # Handle due_date formatting
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                pass
        
        due_date_str = due_date.strftime('%B %d, %Y') if hasattr(due_date, 'strftime') else str(due_date)
        
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
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
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
            <p><a href="{review_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Access Review</a></p>
            
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
        # Handle due_date formatting
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                pass
        
        due_date_str = due_date.strftime('%B %d, %Y') if hasattr(due_date, 'strftime') else str(due_date)
        
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
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff;">
                <h3>Topic #{topic_id}: {topic_title}</h3>
                <p><strong>Priority:</strong> {priority.title()}</p>
                <p><strong>Due Date:</strong> {formatted_due_date}</p>
                {f'<p><strong>Message from Author:</strong></p><p>{author_message}</p>' if author_message else ''}
            </div>
            
            <p>Please click the link below to access the review portal:</p>
            <p><a href="{review_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Start Review</a></p>
            
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

# Global email service instance
email_service = EmailService()
