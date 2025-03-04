import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import secrets

class EmailHandler:
    def __init__(self):
        load_dotenv()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('EMAIL_USER')
        self.sender_password = os.getenv('EMAIL_PASSWORD')

    def send_recovery_email(self, to_email, recovery_code):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = "Password Recovery Code"

            body = f"""Hello!

You requested to reset your password. Here's your recovery code:
{recovery_code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

Best regards,
Virtual Classroom Team"""

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()

            return True, "Recovery code sent to your email!"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"

    def generate_recovery_code(self):
        return secrets.token_hex(3)  # Generates a 6-character code 