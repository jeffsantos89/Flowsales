import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    """Email configuration settings"""
    smtp_server: str = os.getenv("SMTP_SERVER", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    
    def validate(self) -> None:
        """Validate email configuration"""
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass]):
            raise ValueError("Missing required SMTP configuration")

class EmailService:
    """Email service for handling email operations"""
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self.config.validate()
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def send_email(
        self,
        recipient: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send an email with retry mechanism and proper error handling
        
        Args:
            recipient: Email recipient
            subject: Email subject
            message: Plain text message
            html_message: Optional HTML message
            headers: Optional additional headers
            
        Returns:
            bool: True if email was sent successfully
            
        Raises:
            smtplib.SMTPException: If email sending fails after all retries
        """
        try:
            # Create message container
            msg = MIMEMultipart('alternative')
            msg["Subject"] = subject
            msg["From"] = self.config.smtp_user
            msg["To"] = recipient
            
            # Add custom headers
            if headers:
                for key, value in headers.items():
                    msg[key] = str(value)
            
            # Attach plain text and HTML parts
            msg.attach(MIMEText(message, 'plain'))
            if html_message:
                msg.attach(MIMEText(html_message, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_pass)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            raise
            
def get_email_service() -> EmailService:
    """Factory function to create EmailService instance"""
    return EmailService()
