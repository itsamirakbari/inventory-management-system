import smtplib
import logging

from email.message import EmailMessage
from flask import current_app
from logging_config import LOGGER_NAME

logger = logging.getLogger(f"{LOGGER_NAME}.email_service")


def send_verification_email(email, verification_code):
    message = EmailMessage()

    message["To"] = email
    message["From"] = current_app.config["MAIL_USERNAME"]
    message["Subject"] = "Email Verification"
    message.set_content(
        f"""Hello,
        
    Your verification code is:
    
    {verification_code}
    
    Please enter this code to complete your registration.
    
    Best regards,
    Inventory Management System
    """
    )

    try:
        with smtplib.SMTP(
            current_app.config["MAIL_SERVER"],
            current_app.config["MAIL_PORT"]
        ) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(
                current_app.config["MAIL_USERNAME"],
                current_app.config["MAIL_PASSWORD"],
            )
            smtp.send_message(message)

        return True

    except smtplib.SMTPException:
        logger.exception("Failed to send verification email.")
        raise


def send_registration_success_email(user):
    message = EmailMessage()
    message["To"] = user['email']
    message["From"] = current_app.config["MAIL_USERNAME"]
    message["Subject"] = "Welcome to Inventory Management System"
    message.set_content(
        f"""Hello {user['username']},
        
        Your account has been successfully created.
        
        Account information:
        
        Username: {user['username']}
        Email: {user['email']}
        
        You can now log in to your account.

    Best regards,
    Inventory Management System Team
    """
    )

    try:
        with smtplib.SMTP(
            current_app.config["MAIL_SERVER"],
            current_app.config["MAIL_PORT"]
        ) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(
                current_app.config["MAIL_USERNAME"],
                current_app.config["MAIL_PASSWORD"],
            )
            smtp.send_message(message)

        return True

    except smtplib.SMTPException:
        logger.exception("Failed to send registration email.")
        raise


def send_password_reset_email(email, reset_code):
    message = EmailMessage()
    message["To"] = email
    message["From"] = current_app.config["MAIL_USERNAME"]
    message["Subject"] = "Password Reset"
    message.set_content(
        f"""Hello,
        
        You requested to reset your password.

        Your password reset code is:

        {reset_code}

        Please enter this code to reset your password.
        
        If you did not request a password reset, you can safely ignore this email.

    Best regards,
    Inventory Management System Team
    """
    )

    try:
        with smtplib.SMTP(
            current_app.config["MAIL_SERVER"],
            current_app.config["MAIL_PORT"]
        ) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(
                current_app.config["MAIL_USERNAME"],
                current_app.config["MAIL_PASSWORD"],
            )
            smtp.send_message(message)

        return True

    except smtplib.SMTPException:
        logger.exception("Failed to send password reset email.")
        raise


def send_password_changed_email(email):
    message = EmailMessage()
    message["To"] = email
    message["From"] = current_app.config["MAIL_USERNAME"]
    message["Subject"] = "Password Changed"
    message.set_content(
        f"""Hello,

    Your password has been successfully changed.

    If you made this change, no further action is required.

    If you did not change your password, please contact support immediately to secure your account.

    Best regards,
    Inventory Management System Team
    """
    )

    try:
        with smtplib.SMTP(
            current_app.config["MAIL_SERVER"],
            current_app.config["MAIL_PORT"]
        ) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(
                current_app.config["MAIL_USERNAME"],
                current_app.config["MAIL_PASSWORD"],
            )
            smtp.send_message(message)

        return True

    except smtplib.SMTPException:
        logger.exception("Failed to send password changed email.")
        raise


def send_email_change_verification(email, verification_code):
    message = EmailMessage()
    message["To"] = email
    message["From"] = current_app.config["MAIL_USERNAME"]
    message["Subject"] = "Confirm Your New Email Address"
    message.set_content(
        f""" Hello,
            
    You requested to use this email address for your InventoryPro account.
    
    Your verification code is:
    
    {verification_code}
    
    This code is valid for 10 minutes.
    
    If you did not request this change, you can safely ignore this email.
    
    Best regards,
    Inventory Management System Team 
    """
    )

    try:
        with smtplib.SMTP(
            current_app.config["MAIL_SERVER"],
            current_app.config["MAIL_PORT"]
        ) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(
                current_app.config["MAIL_USERNAME"],
                current_app.config["MAIL_PASSWORD"],
            )
            smtp.send_message(message)

        return True

    except smtplib.SMTPException:
        logger.exception("Failed to send email change verification.")
        raise


