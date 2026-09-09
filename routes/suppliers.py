import logging
import mysql.connector

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_all_suppliers, get_supplier_by_id, get_supplier_by_name, create_supplier, update_supplier, delete_supplier
from logging_config import LOGGER_NAME
from utils.decorators import login_required
from utils.validators import is_valid_email


suppliers_bp = Blueprint('suppliers', __name__)
logger = logging.getLogger(LOGGER_NAME)


@suppliers_bp.route("/", methods=["GET"])
@login_required
def suppliers():
    try:
        suppliers_list = get_all_suppliers()

        return render_template("suppliers.html",suppliers=suppliers_list)

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while loading suppliers | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while loading suppliers | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))


@suppliers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_supplier_route():
    if request.method == "GET":
        return render_template("add_supplier.html")

    company_name = request.form.get("company_name", "").strip()
    contact_person = request.form.get("contact_person", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    street = request.form.get("street", "").strip()
    house_number = request.form.get("house_number", "").strip()
    postal_code = request.form.get("postal_code", "").strip()
    city = request.form.get("city", "").strip()
    country = request.form.get("country", "").strip()
    description = request.form.get("description", "").strip()

    if not all((
        company_name,
        contact_person,
        email,
        phone,
        street,
        house_number,
        postal_code,
        city,
        country,
        description
    )):
        flash("Please fill all required fields.", "error")
        return redirect(url_for("suppliers.add_supplier_route"))

    if not is_valid_email(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("suppliers.add_supplier_route"))

    company_name = company_name.title()
    contact_person = contact_person.title()
    street = street.title()
    city = city.title()
    country = country.title()

    try:
        existing_supplier = get_supplier_by_name(company_name)

        if existing_supplier:
            flash(f"Supplier '{company_name}' already exists.", "error")
            return redirect(url_for("suppliers.add_supplier_route"))

        create_supplier(
            company_name,
            contact_person,
            email,
            phone,
            street,
            house_number,
            postal_code,
            city,
            country,
            description
        )
        flash(f"Supplier '{company_name}' created successfully.", "success")
        logger.info(f"Supplier created successfully | Supplier: '{company_name}' | User: {session['user']['username']}")
        return redirect(url_for("suppliers.suppliers"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while creating supplier | Supplier: '{company_name}' | User: {session['user']['username']}")
        return redirect(url_for("suppliers.add_supplier_route"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while creating supplier | Supplier: '{company_name}' | User: {session['user']['username']}")
        return redirect(url_for("suppliers.add_supplier_route"))


@suppliers_bp.route("/delete/<int:supplier_id>", methods=["POST"])
@login_required
def delete_supplier_route(supplier_id):
    try:
        supplier = get_supplier_by_id(supplier_id)

        if not supplier:
            flash("Supplier not found.", "error")
            return redirect(url_for("suppliers.suppliers"))

        delete_supplier(supplier_id)
        flash(f"Supplier '{supplier['company_name']}' deleted successfully.", "success")
        logger.info(f"Supplier deleted successfully | Supplier ID: {supplier_id} | Supplier: '{supplier['company_name']}' | User: {session['user']['username']}")
        return redirect(url_for("suppliers.suppliers"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while deleting supplier | Supplier ID: {supplier_id} | User: {session['user']['username']}")
        return redirect(url_for("suppliers.suppliers"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while deleting supplier | Supplier ID: {supplier_id} | User: {session['user']['username']}")
        return redirect(url_for("suppliers.suppliers"))


@suppliers_bp.route("/update/<int:supplier_id>", methods=["POST"])
@login_required
def update_supplier_route(supplier_id):
    company_name = request.form.get("company_name", "").strip()
    contact_person = request.form.get("contact_person", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    street = request.form.get("street", "").strip()
    house_number = request.form.get("house_number", "").strip()
    postal_code = request.form.get("postal_code", "").strip()
    city = request.form.get("city", "").strip()
    country = request.form.get("country", "").strip()
    description = request.form.get("description", "").strip()

    if not all((
        company_name,
        contact_person,
        email,
        phone,
        street,
        house_number,
        postal_code,
        city,
        country,
        description
    )):
        flash("Please fill all required fields.", "error")
        return redirect(url_for("suppliers.suppliers"))

    if not is_valid_email(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("suppliers.suppliers"))

    company_name = company_name.title()
    contact_person = contact_person.title()
    street = street.title()
    city = city.title()
    country = country.title()

    try:
        supplier = get_supplier_by_id(supplier_id)

        if not supplier:
            flash("Supplier not found.", "error")
            return redirect(url_for("suppliers.suppliers"))

        existing_supplier = get_supplier_by_name(company_name)

        if existing_supplier and existing_supplier["id"] != supplier_id:
            flash(f"Supplier '{company_name}' already exists.", "error")
            return redirect(url_for("suppliers.suppliers"))

        update_supplier(
            supplier_id,
            company_name,
            contact_person,
            email,
            phone,
            street,
            house_number,
            postal_code,
            city,
            country,
            description
        )
        flash(f"Supplier '{company_name}' updated successfully.", "success")
        logger.info(f"Supplier updated successfully | Supplier ID: {supplier_id} | Old Company Name: '{supplier['company_name']}' | New Company Name: '{company_name}' | User: {session['user']['username']}")
        return redirect(url_for("suppliers.suppliers"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating supplier | Supplier ID: {supplier_id} | New Company Name: '{company_name}' | User: {session['user']['username']}")
        return redirect(url_for("suppliers.suppliers"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating supplier | Supplier ID: {supplier_id} | New Company Name: '{company_name}' | User: {session['user']['username']}")
        return redirect(url_for("suppliers.suppliers"))


