import logging
import mysql.connector

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_all_categories, get_category_by_id, get_category_by_name, create_category, update_category, delete_category
from logging_config import LOGGER_NAME
from utils.decorators import login_required


categories_bp = Blueprint('categories', __name__)
logger = logging.getLogger(LOGGER_NAME)


@categories_bp.route("/", methods=["GET"])
@login_required
def categories():
    try:
        categories_list = get_all_categories()

        return render_template("categories.html", categories=categories_list)

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while loading categories | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while loading categories | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))


@categories_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_category_route():
    if request.method == "GET":
        return render_template("add_category.html")

    category_name = request.form.get("category_name", "").strip()
    category_description = request.form.get("category_description", "").strip()

    if not category_name or not category_description:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("categories.add_category_route"))

    category_name = category_name.title()

    try:
        existing_category = get_category_by_name(category_name)

        if existing_category:
            flash(f"Category '{category_name}' already exists.", "error")
            return redirect(url_for("categories.add_category_route"))

        create_category(category_name, category_description)

        flash(f"Category '{category_name}' created successfully.", "success")
        logger.info(f"Category created successfully | Category: '{category_name}' | User: {session['user']['username']}")
        return redirect(url_for("categories.categories"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while creating category | Category: '{category_name}' | User: {session['user']['username']}")
        return redirect(url_for("categories.add_category_route"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while creating category | Category: '{category_name}' | User: {session['user']['username']}")
        return redirect(url_for("categories.add_category_route"))


@categories_bp.route("/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category_route(category_id):
    try:
        category = get_category_by_id(category_id)

        if not category:
            flash("Category not found.", "error")
            return redirect(url_for("categories.categories"))

        delete_category(category_id)

        flash(f"Category '{category['name']}' deleted successfully.", "success")
        logger.info(f"Category deleted successfully | Category ID: {category_id} | Category: '{category['name']}' | User: {session['user']['username']}")
        return redirect(url_for("categories.categories"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while deleting category | Category ID: {category_id} | User: {session['user']['username']}")
        return redirect(url_for("categories.categories"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while deleting category | Category ID: {category_id} | User: {session['user']['username']}")
        return redirect(url_for("categories.categories"))


@categories_bp.route("/update/<int:category_id>", methods=["POST"])
@login_required
def update_category_route(category_id):
    category_name = request.form.get("category_name", "").strip()
    category_description = request.form.get("category_description", "").strip()

    if not category_name or not category_description:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("categories.categories"))

    category_name = category_name.title()

    try:
        category = get_category_by_id(category_id)

        if not category:
            flash("Category not found.", "error")
            return redirect(url_for("categories.categories"))

        existing_category = get_category_by_name(category_name)

        if (existing_category and existing_category["id"] != category_id):
            flash(f"Category '{category_name}' already exists.", "error")
            return redirect(url_for("categories.categories"))

        update_category(
            category_id,
            category_name,
            category_description
        )

        flash(f"Category '{category_name}' updated successfully.", "success")
        logger.info(f"Category updated successfully | Category ID: {category_id} | Old Name: '{category['name']}' | New Name: '{category_name}' | User: {session['user']['username']}")
        return redirect(url_for("categories.categories"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating category | Category ID: {category_id} | New Name: '{category_name}' | User: {session['user']['username']}")
        return redirect(url_for("categories.categories"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating category | Category ID: {category_id} | New Name: '{category_name}' | User: {session['user']['username']}")
        return redirect(url_for("categories.categories"))

