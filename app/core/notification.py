# app/core/notification.py
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Manager for sending notifications to users about validation events
    such as approvals, rejections, or items that need review.
    """
    
    def __init__(self, smtp_server: Optional[str] = None, smtp_port: int = 587, 
                 use_tls: bool = True, username: Optional[str] = None, 
                 password: Optional[str] = None):
        """
        Initialize the notification manager.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            use_tls: Whether to use TLS for connection
            username: SMTP username for authentication
            password: SMTP password for authentication
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        
        # Flag to determine if email is configured
        self.email_configured = bool(smtp_server and username and password)
    
    def send_email_notification(self, subject: str, message: str, recipients: List[str], 
                               sender: Optional[str] = None) -> bool:
        """
        Send an email notification.
        
        Args:
            subject: Email subject
            message: Email message body (HTML)
            recipients: List of recipient email addresses
            sender: Sender email address
            
        Returns:
            Boolean indicating success
        """
        if not self.email_configured:
            logger.warning("Email notifications not configured, skipping email notification")
            return False
            
        if not sender:
            sender = self.username
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            
            # Attach HTML message
            msg.attach(MIMEText(message, 'html'))
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                    
                if self.username and self.password:
                    server.login(self.username, self.password)
                    
                server.send_message(msg)
                
            logger.info(f"Sent email notification to {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def send_validation_approval_notification(self, validation_data: Dict[str, Any], 
                                             recipients: List[str]) -> bool:
        """
        Send notification when a validation item has been approved.
        
        Args:
            validation_data: Data about the validation item
            recipients: List of recipient email addresses
            
        Returns:
            Boolean indicating success
        """
        subject = f"Rule Validation Approved: {validation_data.get('title', 'Untitled')}"
        
        message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Rule Validation Approved</h2>
                </div>
                <div class="content">
                    <p>A rule validation has been approved and converted to a guideline rule:</p>
                    <ul>
                        <li><strong>Title:</strong> {validation_data.get('title', 'Untitled')}</li>
                        <li><strong>Type:</strong> {validation_data.get('rule_type', 'Unknown').title()}</li>
                        <li><strong>Approved by:</strong> {validation_data.get('validator', 'System')}</li>
                    </ul>
                    <p>The rule has been added to the active guidelines and will be included in future guideline generations.</p>
                    <p><a href="{validation_data.get('url', '#')}">View Rule</a></p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from the ESD & Latch-up Guideline Generator System.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email_notification(subject, message, recipients)
    
    def send_validation_rejection_notification(self, validation_data: Dict[str, Any], 
                                              recipients: List[str]) -> bool:
        """
        Send notification when a validation item has been rejected.
        
        Args:
            validation_data: Data about the validation item
            recipients: List of recipient email addresses
            
        Returns:
            Boolean indicating success
        """
        subject = f"Rule Validation Rejected: {validation_data.get('title', 'Untitled')}"
        
        message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; }}
                .reason {{ background-color: #f8f9fa; padding: 10px; border-left: 3px solid #dc3545; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Rule Validation Rejected</h2>
                </div>
                <div class="content">
                    <p>A rule validation has been rejected:</p>
                    <ul>
                        <li><strong>Title:</strong> {validation_data.get('title', 'Untitled')}</li>
                        <li><strong>Type:</strong> {validation_data.get('rule_type', 'Unknown').title()}</li>
                        <li><strong>Rejected by:</strong> {validation_data.get('validator', 'System')}</li>
                    </ul>
                    <p><strong>Reason for rejection:</strong></p>
                    <div class="reason">
                        <p>{validation_data.get('notes', 'No reason provided.')}</p>
                    </div>
                    <p><a href="{validation_data.get('url', '#')}">View Details</a></p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from the ESD & Latch-up Guideline Generator System.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email_notification(subject, message, recipients)
    
    def send_needs_review_notification(self, validation_data: Dict[str, Any], 
                                      recipients: List[str]) -> bool:
        """
        Send notification when a validation item has been marked for review.
        
        Args:
            validation_data: Data about the validation item
            recipients: List of recipient email addresses
            
        Returns:
            Boolean indicating success
        """
        subject = f"Rule Needs Review: {validation_data.get('title', 'Untitled')}"
        
        message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #17a2b8; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 20px; }}
                .notes {{ background-color: #f8f9fa; padding: 10px; border-left: 3px solid #17a2b8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Rule Needs Further Review</h2>
                </div>
                <div class="content">
                    <p>A rule validation has been marked as needing further review:</p>
                    <ul>
                        <li><strong>Title:</strong> {validation_data.get('title', 'Untitled')}</li>
                        <li><strong>Type:</strong> {validation_data.get('rule_type', 'Unknown').title()}</li>
                        <li><strong>Marked by:</strong> {validation_data.get('validator', 'System')}</li>
                    </ul>
                    <p><strong>Reviewer Notes:</strong></p>
                    <div class="notes">
                        <p>{validation_data.get('notes', 'No additional notes provided.')}</p>
                    </div>
                    <p>Please review this rule at your earliest convenience.</p>
                    <p><a href="{validation_data.get('url', '#')}">Review Now</a></p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from the ESD & Latch-up Guideline Generator System.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email_notification(subject, message, recipients)
    
    def log_notification(self, notification_type: str, validation_id: int, user: str, 
                        message: str) -> None:
        """
        Log a notification event for record-keeping.
        
        Args:
            notification_type: Type of notification (approval, rejection, etc)
            validation_id: ID of the validation item
            user: User who triggered the notification
            message: Notification message
        """
        logger.info(f"NOTIFICATION [{notification_type.upper()}]: " 
                   f"Validation #{validation_id} - User: {user} - {message}")


# Default notification manager instance
notification_manager = NotificationManager()
