import logging
import mysql.connector

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_all_inventory_transactions, get_inventory_transaction_by_id, create_inventory_transaction_with_stock_update, get_product_by_id, get_user_by_id, get_all_products, get_all_users
from logging_config import LOGGER_NAME
from utils.decorators import login_required



inventory_transactions_bp = Blueprint("inventory_transactions", __name__)
logger = logging.getLogger(LOGGER_NAME)


def render_inventory_transactions_page(transactions_list, selected_product_id=None, selected_user_id=None, selected_start_date="", selected_end_date=""):
    products_list = get_all_products()
    users_list = get_all_users()

    products_map = {
        product["id"]: product["name"]
        for product in products_list
    }

    users_map = {
        user["id"]: user["username"]
        for user in users_list
    }

    stock_in_count = sum(
        1 for transaction in transactions_list
        if transaction["transaction_type"] in ["stock_in", "adjustment_in"]
    )
    stock_out_count = sum(
        1 for transaction in transactions_list
        if transaction["transaction_type"] in ["stock_out", "adjustment_out"]
    )
    today_transaction_count = sum(
        1 for transaction in transactions_list
        if transaction["created_at"].date() == datetime.today().date()
    )

    return render_template(
        "inventory_transactions.html",
        transactions=transactions_list,
        products=products_list,
        users=users_list,
        products_map=products_map,
        users_map=users_map,
        selected_product_id=selected_product_id,
        selected_user_id=selected_user_id,
        selected_start_date=selected_start_date,
        selected_end_date=selected_end_date,
        stock_in_count=stock_in_count,
        stock_out_count=stock_out_count,
        today_transaction_count=today_transaction_count
    )


@inventory_transactions_bp.route("/", methods=["GET"])
@login_required
def inventory_transactions():
    product_id = request.args.get("product_id", "").strip()
    user_id = request.args.get("user_id", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    try:
        selected_product_id = int(product_id) if product_id else None
        selected_user_id = int(user_id) if user_id else None
    except ValueError:
        flash("Invalid filter selection.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    try:
        if start_date:
            datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    if start_date and end_date and start_date > end_date:
        flash("Start date cannot be later than end date.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    transactions_list = get_all_inventory_transactions(
        product_id=selected_product_id,
        user_id=selected_user_id,
        start_date=start_date or None,
        end_date=end_date or None
    )

    return render_inventory_transactions_page(
        transactions_list,
        selected_product_id=selected_product_id,
        selected_user_id=selected_user_id,
        selected_start_date=start_date,
        selected_end_date=end_date
    )


@inventory_transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_inventory_transaction_route():
    products_list = get_all_products()

    if request.method == "GET":
        return render_template("add_inventory_transaction.html", products=products_list)

    transaction_type = request.form.get("transaction_type", "").strip()
    product_id = request.form.get("product_id", "").strip()
    quantity = request.form.get("quantity", "").strip()
    reason = request.form.get("reason", "").strip()
    transaction_reference = request.form.get("transaction_reference", "").strip()
    note = request.form.get("note", "").strip()
    user_id = session["user"]["user_id"]

    if not transaction_type or not product_id or not quantity or not reason or not transaction_reference:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    if transaction_type not in ["stock_in", "stock_out", "adjustment_in", "adjustment_out"]:
        flash("Invalid transaction type.", "error")
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    if reason not in [
        "purchase",
        "sale",
        "return_in",
        "return_out",
        "damaged_goods",
        "lost_goods",
        "recount_correction",
        "manual_adjustment",
        "other"
    ]:
        flash("Invalid transaction reason.", "error")
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    if reason == "other" and not note:
        flash("Please provide a note when reason is 'other'.", "error")
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except ValueError:
        flash("Invalid transaction data. Please check your inputs.", "error")
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    if quantity <= 0:
        flash("Quantity must be greater than 0.", "error")
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    product = get_product_by_id(product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    try:
        transaction_result = create_inventory_transaction_with_stock_update(
            transaction_type,
            product_id,
            user_id,
            quantity,
            reason,
            transaction_reference,
            note
        )

        product = transaction_result["product"]
        current_stock = transaction_result["old_stock"]
        new_stock = transaction_result["new_stock"]

        flash("Inventory transaction created successfully.", "success")
        logger.info(
            f"Inventory transaction created successfully | "
            f"Type: '{transaction_type}' | "
            f"Reason: '{reason}' | "
            f"Reference: '{transaction_reference}' | "
            f"Product ID: {product_id} | "
            f"Product: '{product['name']}' | "
            f"SKU: '{product['sku']}' | "
            f"Quantity: {quantity} | "
            f"Old Stock: {current_stock} | "
            f"New Stock: {new_stock} | "
            f"User: {session['user']['username']}"
        )
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    except ValueError as error:
        flash(str(error), "error")
        logger.warning(
            f"Inventory transaction rejected | "
            f"Type: '{transaction_type}' | "
            f"Reason: '{reason}' | "
            f"Reference: '{transaction_reference}' | "
            f"Product ID: {product_id} | "
            f"Quantity: {quantity} | "
            f"User: {session['user']['username']} | "
            f"Rejection: {error}"
        )
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(
            f"Database error while creating inventory transaction | "
            f"Type: '{transaction_type}' | "
            f"Reason: '{reason}' | "
            f"Reference: '{transaction_reference}' | "
            f"Product ID: {product_id} | "
            f"Product: '{product['name']}' | "
            f"SKU: '{product['sku']}' | "
            f"Quantity: {quantity} | "
            f"User: {session['user']['username']}"
        )
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(
            f"Unexpected error while creating inventory transaction | "
            f"Type: '{transaction_type}' | "
            f"Reason: '{reason}' | "
            f"Reference: '{transaction_reference}' | "
            f"Product ID: {product_id} | "
            f"Product: '{product['name']}' | "
            f"SKU: '{product['sku']}' | "
            f"Quantity: {quantity} | "
            f"User: {session['user']['username']}"
        )
        return redirect(url_for("inventory_transactions.add_inventory_transaction_route"))


@inventory_transactions_bp.route("/product/<int:product_id>")
@login_required
def inventory_transactions_by_product(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    return redirect(url_for("inventory_transactions.inventory_transactions", product_id=product_id))


@inventory_transactions_bp.route("/user/<int:user_id>")
@login_required
def inventory_transactions_by_user(user_id):
    user = get_user_by_id(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    return redirect(url_for("inventory_transactions.inventory_transactions", user_id=user_id))


@inventory_transactions_bp.route("/date-range", methods=["POST"])
@login_required
def inventory_transactions_by_date_range():
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()

    try:
        if start_date:
            datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    if start_date and end_date and start_date > end_date:
        flash("Start date cannot be later than end date.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    return redirect(
        url_for(
            "inventory_transactions.inventory_transactions",
            start_date=start_date or "",
            end_date=end_date or ""
        )
    )


@inventory_transactions_bp.route("/<int:transaction_id>")
@login_required
def inventory_transaction_detail(transaction_id):
    transaction = get_inventory_transaction_by_id(transaction_id)
    if not transaction:
        flash("Transaction not found.", "error")
        return redirect(url_for("inventory_transactions.inventory_transactions"))

    product = get_product_by_id(transaction["product_id"])
    user = get_user_by_id(transaction["user_id"])

    return render_template(
        "inventory_transaction_detail.html",
        transaction=transaction,
        product=product,
        user=user,
    )
