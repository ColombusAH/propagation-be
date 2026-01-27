import logging
import smtplib
import resend
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.resend_api_key = settings.RESEND_API_KEY
        
        # Resend default onboarding email or configured email
        self.from_email = settings.EMAILS_FROM_EMAIL or "onboarding@resend.dev"
        
        if self.resend_api_key:
            resend.api_key = self.resend_api_key

    def send_verification_email(self, to_email: str, code: str):
        """Send verification code via email."""
        
        # Priority 1: Resend API
        if self.resend_api_key:
            try:
                params = {
                    "from": f"Tagid RFID <{self.from_email}>",
                    "to": [to_email],
                    "subject": "Your Verification Code - Tagid RFID",
                    "html": f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
                            <h2>Welcome to Tagid RFID!</h2>
                            <p>Your verification code is:</p>
                            <h1 style="color: #4A90E2; letter-spacing: 5px; font-size: 32px;">{code}</h1>
                            <p>This code will expire in 15 minutes.</p>
                        </body>
                    </html>
                    """
                }
                resend.Emails.send(params)
                logger.info(f"Verification email sent via Resend to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via Resend to {to_email}: {e}")
                # Fallthrough to SMTP or Mock if Resend fails

        # Priority 2: SMTP
        if self.smtp_host:
            try:
                msg = MIMEMultipart()
                msg["From"] = self.from_email
                msg["To"] = to_email
                msg["Subject"] = "Your Verification Code - Tagid RFID"

                body = f"""
                <html>
                    <body>
                        <h2>Welcome to Tagid RFID!</h2>
                        <p>Your verification code is:</p>
                        <h1 style="color: #4A90E2; letter-spacing: 5px;">{code}</h1>
                        <p>This code will expire in 15 minutes.</p>
                    </body>
                </html>
                """
                msg.attach(MIMEText(body, "html"))

                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                
                logger.info(f"Verification email sent via SMTP to {to_email}")
                return True
            except Exception as e:
                logger.error(f"Failed to send email via SMTP to {to_email}: {e}")
                return False

        # Priority 3: Mock (Development/Fallback)
        print(f"\n==================================================")
        print(f" [MOCK EMAIL] To: {to_email}")
        print(f" [MOCK EMAIL] Verification Code: {code}")
        print(f"==================================================\n")
        logger.warning(f"No email provider configured. Mocking email to {to_email}")
        return True

# Singleton instance
email_service = EmailService()
