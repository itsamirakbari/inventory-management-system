import logging
import mysql.connector

from datetime import datetime
from uuid import uuid4
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from db import get_all_invoices, get_invoice_by_id, get_invoice_items, create_invoice, create_invoice_item, update_invoice_status, get_available_products, get_active_customers, get_customer_by_id, get_product_by_id, create_inventory_transaction_with_stock_update
from logging_config import LOGGER_NAME
from utils.decorators import login_required
from utils.invoice_pdf import generate_invoice_pdf


invoices_bp = Blueprint('invoices', __name__)
logger = logging.getLogger(LOGGER_NAME)


def generate_invoice_number():
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = uuid4().hex[:6].upper()

    return f"INV-{date_part}-{random_part}"


@invoices_bp.route("/", methods=["GET"])
@login_required
def invoices():
    try:
        invoices_list = get_all_invoices()

        return render_template(
            "invoices.html", invoices=invoices_list)

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while loading invoices | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while loading invoices | User: {session['user']['username']}")
        return redirect(url_for("dashboard.dashboard"))


@invoices_bp.route("/<int:invoice_id>", methods=["GET"])
@login_required
def invoice_detail_route(invoice_id):
    try:
        invoice = get_invoice_by_id(invoice_id)

        if not invoice:
            flash("Invoice not found.", "error")
            return redirect(url_for("invoices.invoices"))

        items = get_invoice_items(invoice_id)

        return render_template("invoice_detail.html", invoice=invoice, items=items)

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while loading invoice details | Invoice ID: {invoice_id} | User: {session['user']['username']}")
        return redirect(url_for("invoices.invoices"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while loading invoice details | Invoice ID: {invoice_id} | User: {session['user']['username']}")
        return redirect(url_for("invoices.invoices"))


@invoices_bp.route("/<int:invoice_id>/pdf", methods=["GET"])
@login_required
def download_invoice_pdf_route(invoice_id):
    try:
        invoice = get_invoice_by_id(invoice_id)

        if not invoice:
            flash("Invoice not found.", "error")
            return redirect(url_for("invoices.invoices"))

        items = get_invoice_items(invoice_id)
        pdf_buffer = generate_invoice_pdf(invoice, items)

        logger.info(f"Invoice PDF generated successfully | Invoice ID: {invoice_id} | Invoice Number: '{invoice['invoice_number']}' | User: {session['user']['username']}")

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{invoice['invoice_number']}.pdf",
        )

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while generating invoice PDF | Invoice ID: {invoice_id} | User: {session['user']['username']}")
        return redirect(url_for("invoices.invoices"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while generating invoice PDF | Invoice ID: {invoice_id} | User: {session['user']['username']}")
        return redirect(url_for("invoices.invoice_detail_route", invoice_id=invoice_id))


@invoices_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_invoice_route():
    if request.method == "GET":
        try:
            customers = get_active_customers()
            products = get_available_products()

            return render_template("add_invoice.html", customers=customers, products=products)

        except mysql.connector.Error:
            flash("Database error. Please try again.", "error")
            logger.exception(f"Database error while loading invoice form | User: {session['user']['username']}")
            return redirect(url_for("invoices.invoices"))

        except Exception:
            flash("An unexpected error occurred.", "error")
            logger.exception(f"Unexpected error while loading invoice form | User: {session['user']['username']}")
            return redirect(url_for("invoices.invoices"))

    customer_id = request.form.get("customer_id", "").strip()
    invoice_date = request.form.get("invoice_date", "").strip()
    note = request.form.get("note", "").strip()

    product_ids = request.form.getlist("product_id")
    quantities = request.form.getlist("quantity")

    user_id = session["user"]["user_id"]

    try:
        if not customer_id or not invoice_date:
            raise ValueError("Please select a customer and invoice date.")

        if not product_ids or not quantities:
            raise ValueError("Please add at least one product.")

        if len(product_ids) != len(quantities):
            raise ValueError("Invalid invoice items.")

        if not customer_id.isdigit():
            raise ValueError("Invalid customer.")

        customer_id = int(customer_id)

        try:
            invoice_date = datetime.strptime(invoice_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid invoice date.") from None

        customer = get_customer_by_id(customer_id)

        if not customer or not customer["is_active"]:
            raise ValueError("The selected customer is not available.")

        invoice_items = []
        seen_product_ids = set()
        total_amount = Decimal("0.00")

        for product_id_value, quantity_value in zip(product_ids, quantities):
            product_id_value = product_id_value.strip()
            quantity_value = quantity_value.strip()

            if not product_id_value.isdigit() or not quantity_value.isdigit():
                raise ValueError("Invalid product or quantity.")

            product_id = int(product_id_value)
            quantity = int(quantity_value)

            if product_id <= 0 or quantity <= 0:
                raise ValueError("Product quantity must be greater than zero.")

            if product_id in seen_product_ids:
                raise ValueError("Each product can only be added once.")

            seen_product_ids.add(product_id)

            product = get_product_by_id(product_id)

            if not product or not product["is_active"]:
                raise ValueError(f"Product ID {product_id} is not available.")

            if quantity > product["stock_quantity"]:
                raise ValueError(
                    f"Not enough stock for '{product['name']}'."
                    f"Available: {product['stock_quantity']}."
                )

            unit_price = Decimal(str(product["price"]))
            total_amount += unit_price * quantity

            invoice_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price
            })

        invoice_number = generate_invoice_number()

        invoice_id = create_invoice(
            invoice_number,
            customer_id,
            user_id,
            invoice_date,
            total_amount,
            note
        )

        for item in invoice_items:
            create_invoice_item(
                invoice_id,
                item["product_id"],
                item["quantity"],
                item["unit_price"]
            )

            create_inventory_transaction_with_stock_update(
                "stock_out",
                item["product_id"],
                user_id,
                item["quantity"],
                "sale",
                invoice_number,
                None
            )

        flash(f"Invoice '{invoice_number}' created successfully.", "success")
        logger.info(f"Invoice created successfully | Invoice ID: {invoice_id} | Invoice Number: '{invoice_number}' | Customer ID: {customer_id} | Total Amount: {total_amount} | User: {session['user']['username']}")

        return redirect(url_for("invoices.invoice_detail_route", invoice_id=invoice_id))

    except ValueError as error:
        flash(str(error), "error")
        logger.warning(f"Invoice creation rejected | Customer ID: '{customer_id}' | Reason: {error} | User: {session['user']['username']}")
        return redirect(url_for("invoices.add_invoice_route"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while creating invoice | Customer ID: '{customer_id}' | User: {session['user']['username']}")
        return redirect(url_for("invoices.add_invoice_route"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while creating invoice | Customer ID: '{customer_id}' | User: {session['user']['username']}")
        return redirect(url_for("invoices.add_invoice_route"))


@invoices_bp.route("/<int:invoice_id>/status", methods=["POST"])
@login_required
def update_invoice_status_route(invoice_id):
    new_status = request.form.get("status", "").strip().lower()

    if new_status not in ("open", "paid"):
        flash("Invalid invoice status.", "error")
        return redirect(url_for("invoices.invoices"))

    try:
        invoice = get_invoice_by_id(invoice_id)

        if not invoice:
            flash("Invoice not found.", "error")
            return redirect(url_for("invoices.invoices"))

        old_status = invoice["status"]

        if old_status == new_status:
            flash(f"Invoice '{invoice['invoice_number']}' is already {new_status}.", "info")
            return redirect(url_for("invoices.invoices"))

        update_invoice_status(invoice_id, new_status)

        flash(f"Invoice '{invoice['invoice_number']}' status updated successfully.", "success")
        logger.info(f"Invoice status updated successfully | Invoice ID: {invoice_id} | Invoice Number: '{invoice['invoice_number']}' | Old Status: {old_status} | New Status: {new_status} | User: {session['user']['username']}")

        return redirect(url_for("invoices.invoices"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating invoice status | Invoice ID: {invoice_id} | New Status: {new_status} | User: {session['user']['username']}")
        return redirect(url_for("invoices.invoices"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating invoice status | Invoice ID: {invoice_id} | New Status: {new_status} | User: {session['user']['username']}")
        return redirect(url_for("invoices.invoices"))


