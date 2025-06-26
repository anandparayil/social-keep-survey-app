"""
Email utilities for Social Keep
"""

from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re


def send_password_reset_email(email, reset_token):
    """Send password reset email with secure link"""
    try:
        subject = "Social Keep - Password Reset Request"
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password for Social Keep.</p>
            <p><a href="{base_url}/reset-password/{reset_token}">Click here to reset your password</a></p>
            <p>If you did not request this, please ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
            <br><p>– Social Keep Team</p>
        </body>
        </html>
        """

        text_body = f"""
        Password Reset Request
        
        You requested to reset your password for Social Keep.
        Reset here: {base_url}/reset-password/{reset_token}
        This link expires in 1 hour.
        
        – Social Keep Team
        """

        return send_email(email, subject, text_body, html_body)

    except Exception as e:
        current_app.logger.error(f"[Email Error] Password reset failed: {e}")
        return False


def send_survey_notification(email, survey_name, survey_type):
    """Notify user about a new survey"""
    try:
        subject = f"New Survey Available: {survey_name}"
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        duration = "24 hours" if survey_type == "daily" else "1 week"

        html_body = f"""
        <html>
        <body>
            <h2>New {survey_type.title()} Survey</h2>
            <p>A new survey <strong>{survey_name}</strong> is now available for you to complete.</p>
            <p><a href="{base_url}/login">Login to Social Keep</a> and complete it within {duration}.</p>
            <br><p>– Social Keep Team</p>
        </body>
        </html>
        """

        text_body = f"""
        New {survey_type.title()} Survey
        
        Survey: {survey_name}
        Duration: {duration}
        Login to complete: {base_url}/login
        
        – Social Keep Team
        """

        return send_email(email, subject, text_body, html_body)

    except Exception as e:
        current_app.logger.error(f"[Email Error] Survey notification failed: {e}")
        return False


def send_credentials_email(email, username, password):
    """Send initial login credentials to new participant"""
    try:
        subject = "Your Social Keep Account Credentials"
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

        html_body = f"""
        <html>
        <body>
            <h2>Welcome to Social Keep!</h2>
            <p>Your account has been created with the following credentials:</p>
            <ul>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>Password:</strong> {password}</li>
            </ul>
            <p><strong>Please change your password after logging in.</strong></p>
            <p><a href="{base_url}/login">Click here to log in</a></p>
            <br><p>– Social Keep Team</p>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Social Keep!

        Your login credentials:
        Email: {email}
        Password: {password}

        Please change your password after logging in:
        {base_url}/login

        – Social Keep Team
        """

        return send_email(email, subject, text_body, html_body)

    except Exception as e:
        current_app.logger.error(f"[Email Error] Sending credentials failed: {e}")
        return False


def send_email(to_email, subject, text_body, html_body=None):
    """Send an email using SMTP with optional HTML"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = current_app.config.get("MAIL_USERNAME")
        msg["To"] = to_email

        msg.attach(MIMEText(text_body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP(
            current_app.config.get("MAIL_SERVER", "smtp.gmail.com"),
            current_app.config.get("MAIL_PORT", 587),
            timeout=10
        )
        server.starttls()

        username = current_app.config.get("MAIL_USERNAME")
        password = current_app.config.get("MAIL_PASSWORD")
        if username and password:
            server.login(username, password)

        server.send_message(msg)
        server.quit()

        current_app.logger.info(f"[Email Sent] To: {to_email} | Subject: {subject}")
        return True

    except Exception as e:
        current_app.logger.error(f"[Email Error] Sending failed: {e}")
        return False


def validate_email(email):
    """Basic email format validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
