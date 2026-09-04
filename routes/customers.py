import logging
import mysql.connector

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_all_customers, get_customer_by_id, get_customer_by_name_and_address, create_customer, update_customer, update_customer_status
from logging_config import LOGGER_NAME
from utils.decorators import login_required


customers_bp = Blueprint('customers', __name__)
logger = logging.getLogger(LOGGER_NAME)


@customers_bp.route("/", methods=["GET"])
@login_required
def customers():
    try:
        customers_list = get_all_customers()

        return render_template("customers.html",customers=customers_list)

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while loading customers | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while loading customers | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))


@customers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_customer_route():
    if request.method == "GET":
        return render_template("add_customer.html")

    customer_name = request.form.get("customer_name", "").strip()
    contact_person = request.form.get("contact_person", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()
    street = request.form.get("street", "").strip()
    house_number = request.form.get("house_number", "").strip()
    postal_code = request.form.get("postal_code", "").strip()
    city = request.form.get("city", "").strip()
    country = request.form.get("country", "").strip()
    description = request.form.get("description", "").strip()

    if not customer_name or not street or not house_number or not postal_code or not city or not country:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("customers.add_customer_route"))

    customer_name = customer_name.title()
    contact_person = contact_person.title()
    street = street.title()
    city = city.title()
    country = country.title()

    try:
        existing_customer = get_customer_by_name_and_address(customer_name, street, house_number, postal_code, city, country)

        if existing_customer:
            flash(f"Customer '{customer_name}' already exists.", "error")
            return redirect(url_for("customers.add_customer_route"))

        create_customer(
            customer_name,
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
        flash(f"Customer '{customer_name}' created successfully.", "success")
        logger.info(f"Customer created successfully | Customer: '{customer_name}' | User: {session['user']['username']}")
        return redirect(url_for("customers.customers"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while creating customer | Customer: '{customer_name}' | User: {session['user']['username']}")
        return redirect(url_for("customers.add_customer_route"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while creating customer | Customer: '{customer_name}' | User: {session['user']['username']}")
        return redirect(url_for("customers.add_customer_route"))


@customers_bp.route("/update/<int:customer_id>", methods=["POST"])
@login_required
def update_customer_route(customer_id):
    customer_name = request.form.get("customer_name", "").strip()
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
        customer_name,
        street,
        house_number,
        postal_code,
        city,
        country
    )):
        flash("Please fill all required fields.", "error")
        return redirect(url_for("customers.customers"))

    customer_name = customer_name.title()
    contact_person = contact_person.title()
    street = street.title()
    city = city.title()
    country = country.title()

    try:
        customer = get_customer_by_id(customer_id)

        if not customer:
            flash("Customer does not exist.", "error")
            return redirect(url_for("customers.customers"))

        existing_customer = get_customer_by_name_and_address(
            customer_name,
            street,
            house_number,
            postal_code,
            city,
            country
        )

        if (existing_customer and existing_customer["id"] != customer_id):
            flash(f"Customer '{customer_name}' already exists.", "error")
            return redirect(url_for("customers.customers"))

        update_customer(
            customer_id,
            customer_name,
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
        flash(f"Customer '{customer_name}' updated successfully.", "success")
        logger.info(f"Customer updated successfully | Customer ID: {customer_id} | Old Customer Name: '{customer['customer_name']}' | New Customer Name: '{customer_name}' | User: {session['user']['username']}")
        return redirect(url_for("customers.customers"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating customer | Customer ID: {customer_id} | New Customer Name: '{customer_name}' | User: {session['user']['username']}")
        return redirect(url_for("customers.customers"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating customer | Customer ID: {customer_id} | New Customer Name: '{customer_name}' | User: {session['user']['username']}")
        return redirect(url_for("customers.customers"))


@customers_bp.route("/update_customer_status/<int:customer_id>", methods=["POST"])
@login_required
def update_customer_status_route(customer_id):
    try:
        customer = get_customer_by_id(customer_id)

        if not customer:
            flash("Customer does not exist.", "error")
            return redirect(url_for("customers.customers"))

        old_status = bool(customer["is_active"])
        new_status = not old_status

        update_customer_status(customer_id, new_status)
        status_message = "activated" if new_status else "deactivated"

        flash(f"Customer '{customer['customer_name']}' {status_message} successfully.", "success")
        logger.info(f"Customer status updated successfully. | Customer ID: {customer_id} | Customer: '{customer['customer_name']}' | Old Status: {old_status} | New Status: {new_status} | User: {session['user']['username']}")
        return redirect(url_for("customers.customers"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating customer status | Customer ID: {customer_id} | User: {session['user']['username']}")
        return redirect(url_for("customers.customers"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating customer status | Customer ID: {customer_id} | User: {session['user']['username']}")
        return redirect(url_for("customers.customers"))

