import logging
import mysql.connector
import random
import smtplib
import time

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.email_service import send_verification_email, send_registration_success_email, send_password_reset_email, send_password_changed_email
from utils.validators import is_valid_password, is_valid_email
from db import get_user_by_username, get_user_by_email, create_user, update_user_password
from logging_config import LOGGER_NAME


auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(LOGGER_NAME)
VERIFICATION_SESSION_LIFETIME_SECONDS = 600


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username").strip()
    email = request.form.get("email").strip().lower()
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not username or not email or not password or not confirm_password:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("auth.register"))

    if password != confirm_password:
        flash("Passwords do not match. Please try again.", "error")
        return redirect(url_for("auth.register"))

    if not is_valid_email(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("auth.register"))

    if not is_valid_password(password):
        flash(
            "Password must contain at least 8 characters, "
            "including at least one letter and one number.",
            "error"
        )
        return redirect(url_for("auth.register"))

    user = get_user_by_username(username)

    if user:
        flash("User already exists.", "error")
        return redirect(url_for("auth.register"))

    email_user = get_user_by_email(email)

    if email_user:
        flash("Email address already exists.", "error")
        return redirect(url_for("auth.register"))

    password_hash = generate_password_hash(password)

    verification_code = random.randint(100000, 999999)

    session["pending_user"] = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "verification_code": verification_code,
        "expires_at": time.time() + VERIFICATION_SESSION_LIFETIME_SECONDS
    }

    try:
        send_verification_email(email, verification_code)

    except (smtplib.SMTPException, OSError):
        flash("Failed to send verification email. Please try again.", "error")
        logger.exception("Failed to send verification email.")
        return redirect(url_for("auth.register"))

    flash("A verification code has been sent to your email.", "success")

    return redirect(url_for("auth.verify"))


@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "GET":
        return render_template("verify.html")

    code = request.form.get("verification_code").strip()
    if not code:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("auth.verify"))

    pending_user = session.get("pending_user")

    if not pending_user:
        flash("Registration session expired.", "error")
        return redirect(url_for("auth.register"))

    if time.time() > pending_user.get("expires_at", 0):
        session.pop("pending_user", None)
        flash("Registration verification code has expired.", "error")
        return redirect(url_for("auth.register"))

    if code != str(pending_user["verification_code"]):
        flash("Invalid verification code.", "error")
        return redirect(url_for("auth.verify"))

    try:
        create_user(
            pending_user["username"],
            pending_user["email"],
            pending_user["password_hash"],
        )

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception("Database error while creating user.")
        return redirect(url_for("auth.verify"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception("Unexpected error during user registration.")
        return redirect(url_for("auth.verify"))

    try:
        send_registration_success_email(pending_user)

    except (smtplib.SMTPException, OSError):
        logger.exception(
            f"User registered, but welcome email failed | "
            f"Username: {pending_user['username']}"
        )

    session.pop("pending_user", None)

    flash("Registration completed successfully.", "success")
    logger.info(f"User registered | Username: {pending_user['username']}")

    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username").strip()
    password = request.form.get("password")

    if not username or not password:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("auth.login"))

    user = get_user_by_username(username)

    if not user:
        flash("Invalid username or password.", "error")
        return redirect(url_for("auth.login"))

    if not check_password_hash(user["password_hash"], password):
        flash("Invalid username or password.", "error")
        return redirect(url_for("auth.login"))

    session["user"] = {
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }

    flash(f"Welcome back, {user['username']}!", "success")
    logger.info(f"User logged in | Username: {user['username']}")

    return redirect(url_for("dashboard.dashboard"))


@auth_bp.route("/logout")
def logout():
    user = session.get("user")
    if user:
        logger.info(f"User logged out | Username: {user['username']}")

    session.pop("user", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")

    email = request.form.get("email").strip().lower()

    if not email:
        flash("Please enter your email address.", "error")
        return redirect(url_for("auth.forgot_password"))

    if not is_valid_email(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = get_user_by_email(email)

    if not user:
        flash("Invalid email address.", "error")
        return redirect(url_for("auth.forgot_password"))

    reset_code = random.randint(100000, 999999)

    session["pending_reset"] = {
        "user_id": user["id"],
        "email": user["email"],
        "reset_code": reset_code,
        "expires_at": time.time() + VERIFICATION_SESSION_LIFETIME_SECONDS
    }

    try:
        send_password_reset_email(user["email"], reset_code)

    except (smtplib.SMTPException, OSError):
        flash("Failed to send password reset email. Please try again.", "error")
        logger.exception("Failed to send password reset email.")
        return redirect(url_for("auth.forgot_password"))

    flash("A password reset code has been sent to your email.", "success")

    return redirect(url_for("auth.reset_password"))


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("reset_password.html")

    code = request.form.get("reset_code").strip()
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")

    if not code or not new_password or not confirm_new_password:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("auth.reset_password"))

    if new_password != confirm_new_password:
        flash("Passwords do not match. Please try again.", "error")
        return redirect(url_for("auth.reset_password"))

    if not is_valid_password(new_password):
        flash(
            "Password must contain at least 8 characters, "
            "including at least one letter and one number.",
            "error"
        )
        return redirect(url_for("auth.reset_password"))

    pending_reset = session.get("pending_reset")

    if not pending_reset:
        flash("Password reset session expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    if time.time() > pending_reset.get("expires_at", 0):
        session.pop("pending_reset", None)
        flash("Password reset code has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    if code != str(pending_reset["reset_code"]):
        flash("Password reset code does not match. Please try again.", "error")
        return redirect(url_for("auth.reset_password"))

    password_hash = generate_password_hash(new_password)

    try:
        update_user_password(
            pending_reset["user_id"],
            password_hash
        )

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(
            f"Database error while resetting password | "
            f"User ID: {pending_reset['user_id']} | "
            f"Email: {pending_reset['email']}"
        )
        return redirect(url_for("auth.reset_password"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(
            f"Unexpected error while resetting password | "
            f"User ID: {pending_reset['user_id']} | "
            f"Email: {pending_reset['email']}"
        )
        return redirect(url_for("auth.reset_password"))

    try:
        send_password_changed_email(pending_reset["email"])

    except (smtplib.SMTPException, OSError):
        logger.exception(
            f"Password reset successfully, but notification email failed | "
            f"User ID: {pending_reset['user_id']}"
        )

    session.pop("pending_reset", None)

    flash("Your password has been changed successfully.", "success")
    logger.info(f"Password changed | User ID: {pending_reset['user_id']}")

    return redirect(url_for("auth.login"))








