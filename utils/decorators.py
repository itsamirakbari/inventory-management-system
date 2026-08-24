import logging

from flask import redirect, url_for, flash, session
from functools import wraps
from logging_config import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))

        return func(*args, **kwargs)

    return wrapper


@login_required
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if session["user"]["role"] != "admin":
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for("dashboard.dashboard"))

        return func(*args, **kwargs)

    return wrapper

