import logging
import mysql.connector
import random
import smtplib
import time

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils.email_service import send_email_change_verification, send_password_changed_email
from utils.validators import is_valid_password, is_valid_email
from db import get_user_by_id, get_user_by_email, update_user_password, update_user_email
from logging_config import LOGGER_NAME
from utils.decorators import login_required


profile_bp = Blueprint("profile", __name__)
logger = logging.getLogger(LOGGER_NAME)


@profile_bp.route("/", methods=["GET"])
@login_required
def profile():
    user_id = session["user"]["user_id"]

    try:
        user = get_user_by_id(user_id)

        if not user:
            session.pop("user", None)
            flash("User account not found.", "error")
            return redirect(url_for("auth.login"))

        return render_template("profile.html", profile_user=user)

    except mysql.connector.Error:
        flash("A database error occurred while loading your profile.", "error")
        logger.exception(f"Database error while loading profile | User ID: {user_id}")
        return redirect(url_for("dashboard.dashboard"))

    except Exception:
        flash("An unexpected error occurred while loading your profile.", "error")
        logger.exception(f"Unexpected error while loading profile | User ID: {user_id}")
        return redirect(url_for("dashboard.dashboard"))


@profile_bp.route("/update-email", methods=["POST"])
@login_required
def update_email():
    user_id = session["user"]["user_id"]
    new_email = request.form.get("email", "").strip().lower()
    current_password = request.form.get("current_password", "")

    if not new_email or not current_password:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("profile.profile"))

    if not is_valid_email(new_email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("profile.profile"))

    try:
        user = get_user_by_id(user_id)

        if not user:
            session.pop("user", None)
            flash("User account could not be found.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user["password_hash"], current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("profile.profile"))

        if new_email == user["email"].lower():
            flash("Please enter a different email address.", "error")
            return redirect(url_for("profile.profile"))

        email_owner = get_user_by_email(new_email)

        if email_owner and email_owner["id"] != user_id:
            flash("Email address is already in use.", "error")
            return redirect(url_for("profile.profile"))

    except mysql.connector.Error:
        flash("A database error occurred while validating your email.", "error")
        logger.exception(f"Database error while validating email change | User ID: {user_id}")
        return redirect(url_for("profile.profile"))

    except Exception:
        flash("An unexpected error occurred while validating your email.", "error")
        logger.exception(f"Unexpected error while validating email change | User ID: {user_id}")
        return redirect(url_for("profile.profile"))

    verification_code = random.randint(100000, 999999)

    try:
        send_email_change_verification(new_email, verification_code)

    except (smtplib.SMTPException, OSError):
        flash("Failed to send the verification code. Please try again.","error")
        logger.exception(f"Failed to send email-change verification | User ID: {user_id}")
        return redirect(url_for("profile.profile"))

    session["pending_email_change"] = {
        "user_id": user_id,
        "new_email": new_email,
        "verification_code": verification_code,
        "expires_at": time.time() + 600
    }

    flash("A verification code has been sent to your new email address.","success")
    logger.info(f"Email change requested | User ID: {user_id} | Username: {user['username']}")

    return redirect(url_for("profile.profile"))


@profile_bp.route("/verify-email", methods=["POST"])
@login_required
def verify_email():
    verification_code = request.form.get("verification_code", "").strip()

    if not verification_code:
        flash("Please enter the verification code.", "error")
        return redirect(url_for("profile.profile"))

    pending_change = session.get("pending_email_change")

    if not pending_change:
        flash("Email verification session expired.", "error")
        return redirect(url_for("profile.profile"))

    user_id = session["user"]["user_id"]

    if pending_change["user_id"] != user_id:
        session.pop("pending_email_change", None)
        flash("Invalid email verification session.", "error")
        return redirect(url_for("profile.profile"))

    if time.time() > pending_change["expires_at"]:
        session.pop("pending_email_change", None)
        flash("The verification code has expired. Please request a new one.","error")
        return redirect(url_for("profile.profile"))

    if verification_code != str(pending_change["verification_code"]):
        flash("Invalid verification code.", "error")
        return redirect(url_for("profile.profile"))

    new_email = pending_change["new_email"]

    try:
        email_owner = get_user_by_email(new_email)

        if email_owner and email_owner["id"] != user_id:
            session.pop("pending_email_change", None)
            flash("Email address is already in use.", "error")
            return redirect(url_for("profile.profile"))

        update_user_email(user_id, new_email)

        session_user = dict(session["user"])
        session_user["email"] = new_email
        session["user"] = session_user

        session.pop("pending_email_change", None)

        flash("Email address updated successfully.", "success")
        logger.info(f"Email updated successfully | User ID: {user_id}")

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating email | User ID: {user_id}")

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating email | User ID: {user_id}")

    return redirect(url_for("profile.profile"))


@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    user_id = session["user"]["user_id"]

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_new_password = request.form.get("confirm_new_password", "")

    if not current_password or not new_password or not confirm_new_password:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("profile.profile"))

    if new_password != confirm_new_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("profile.profile"))

    if not is_valid_password(new_password):
        flash(
            "Password must contain at least 8 characters, "
            "including at least one letter and one number.",
            "error"
        )
        return redirect(url_for("profile.profile"))

    try:
        user = get_user_by_id(user_id)

        if not user:
            session.clear()
            flash("User account could not be found.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user["password_hash"], current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("profile.profile"))

        if check_password_hash(user["password_hash"], new_password):
            flash("New password must be different from the current password.","error")
            return redirect(url_for("profile.profile"))

        new_password_hash = generate_password_hash(new_password)
        update_user_password(user_id, new_password_hash)

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while changing password | User ID: {user_id}")
        return redirect(url_for("profile.profile"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while changing password | User ID: {user_id}")
        return redirect(url_for("profile.profile"))

    try:
        send_password_changed_email(user["email"])

    except (smtplib.SMTPException, OSError):
        logger.exception(f"Password changed, but notification email failed | User ID: {user_id}")

    logger.info(f"Password changed successfully | User ID: {user_id} | Username: {user['username']}")

    session.clear()

    flash("Password changed successfully. Please log in with your new password.","success")

    return redirect(url_for("auth.login"))






