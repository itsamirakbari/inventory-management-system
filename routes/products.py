import logging
import mysql.connector

from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from db import get_all_products, get_product_by_id, get_product_by_sku, create_product, update_product, delete_product, update_product_status, get_all_categories, get_all_suppliers
from logging_config import LOGGER_NAME
from utils.decorators import login_required


products_bp = Blueprint('products', __name__)
logger = logging.getLogger(LOGGER_NAME)


@products_bp.route("/", methods=["GET"])
@login_required
def products():
    products_list = get_all_products()
    categories_list = get_all_categories()
    suppliers_list = get_all_suppliers()

    categories_map = {
        category["id"]: category["name"]
        for category in categories_list
    }

    suppliers_map = {
        supplier["id"]: supplier["company_name"]
        for supplier in suppliers_list
    }

    return render_template(
        "products.html",
        products=products_list,
        categories=categories_list,
        suppliers=suppliers_list,
        categories_map=categories_map,
        suppliers_map=suppliers_map
    )


@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product_route():
    if request.method == "GET":
        categories_list = get_all_categories()
        suppliers_list = get_all_suppliers()
        return render_template("add_product.html", categories=categories_list, suppliers=suppliers_list)

    product_name = request.form.get("name", "").strip()
    product_code = request.form.get("sku", "").strip()
    price = request.form.get("price", "").strip()
    stock_quantity = request.form.get("stock_quantity", "").strip()
    category_id = request.form.get("category_id", "").strip()
    supplier_id = request.form.get("supplier_id", "").strip()

    if not product_name or not product_code or not price or not stock_quantity or not category_id or not supplier_id:
        flash("Please fill all required fields.", "error")
        return redirect(url_for("products.add_product_route"))

    try:
        price = float(price)
        stock_quantity = int(stock_quantity)
        category_id = int(category_id)
        supplier_id = int(supplier_id)
    except ValueError:
        flash("Invalid product data. Please check your inputs.", "error")
        return redirect(url_for("products.add_product_route"))

    existing_product = get_product_by_sku(product_code)

    if existing_product:
        flash(f"Product with SKU '{product_code}' already exists.", "error")
        return redirect(url_for("products.add_product_route"))

    try:
        create_product(product_name, product_code, price, stock_quantity, category_id, supplier_id)
        flash("Product created successfully.", "success")
        logger.info(f"Product created successfully | Product: '{product_name}' | SKU: '{product_code}' | User: {session['user']['username']}")
        return redirect(url_for("products.products"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while creating product | Product: '{product_name}' | SKU: '{product_code}' | User: {session['user']['username']}")
        return redirect(url_for("products.add_product_route"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while creating product | Product: '{product_name}' | SKU: '{product_code}' | User: {session['user']['username']}")
        return redirect(url_for("products.add_product_route"))


@products_bp.route("/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product_route(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products.products"))

    try:
        delete_product(product_id)
        flash("Product deleted successfully.", "success")
        logger.info(f"Product deleted successfully | Product ID: {product_id} | Product: '{product['name']}' | SKU: '{product['sku']}' | User: {session['user']['username']}")
        return redirect(url_for("products.products"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while deleting product | Product ID: {product_id} | Product: '{product['name']}' | SKU: '{product['sku']}' | User: {session['user']['username']}")
        return redirect(url_for("products.products"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while deleting product | Product ID: {product_id} | Product: '{product['name']}' | SKU: '{product['sku']}' | User: {session['user']['username']}")
        return redirect(url_for("products.products"))


@products_bp.route("/update/<int:product_id>", methods=["POST"])
@login_required
def update_product_route(product_id):
    product_name = request.form.get("name", "").strip()
    product_code = request.form.get("sku", "").strip()
    price = request.form.get("price", "").strip()
    stock_quantity = request.form.get("stock_quantity", "").strip()
    category_id = request.form.get("category_id", "").strip()
    supplier_id = request.form.get("supplier_id", "").strip()

    if not (
        product_name,
        product_code,
        price,
        stock_quantity,
        category_id,
        supplier_id
    ):
        flash("Please fill all required fields.", "error")
        return redirect(url_for("products.products"))

    try:
        price = float(price)
        stock_quantity = int(stock_quantity)
        category_id = int(category_id)
        supplier_id = int(supplier_id)
    except ValueError:
        flash("Invalid product data. Please check your inputs.", "error")
        return redirect(url_for("products.products"))

    product = get_product_by_id(product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products.products"))

    existing_product = get_product_by_sku(product_code)

    if existing_product and existing_product["id"] != product_id:
        flash(f"Product with SKU '{product_code}' already exists.", "error")
        return redirect(url_for("products.products"))

    try:
        update_product(
            product_id,
            product_name,
            product_code,
            price,
            stock_quantity,
            category_id,
            supplier_id
        )
        flash("Product updated successfully.", "success")
        logger.info(f"Product updated successfully | Product ID: {product_id} | Old Product: '{product['name']}' | New Product: '{product_name}' | Old SKU: '{product['sku']}' | New SKU: '{product_code}' | User: {session['user']['username']}")
        return redirect(url_for("products.products"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating product | Product ID: {product_id} | Old Product: '{product['name']}' | New Product: '{product_name}' | Old SKU: '{product['sku']}' | New SKU: '{product_code}' | User: {session['user']['username']}")
        return redirect(url_for("products.products"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating product | Product ID: {product_id} | Old Product: '{product['name']}' | New Product: '{product_name}' | Old SKU: '{product['sku']}' | New SKU: '{product_code}' | User: {session['user']['username']}")
        return redirect(url_for("products.products"))


@products_bp.route("/update_product_status/<int:product_id>", methods=["POST"])
@login_required
def update_product_status_route(product_id):
    product = get_product_by_id(product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products.products"))

    is_active = not product["is_active"]

    try:
        update_product_status(product_id, is_active)
        flash(f"Product '{product['name']}' status updated successfully.", "success")
        logger.info(f"Product status updated successfully | Product ID: {product_id} | Product: '{product['name']}' | SKU: '{product['sku']}' | Old Status: {product['is_active']} | New Status: {is_active} | User: {session['user']['username']}")
        return redirect(url_for("products.products"))

    except mysql.connector.Error:
        flash("Database error. Please try again.", "error")
        logger.exception(f"Database error while updating product status | Product ID: {product_id} | Product: '{product['name']}' | SKU: '{product['sku']}' | Old Status: {product['is_active']} | New Status: {is_active} | User: {session['user']['username']}")
        return redirect(url_for("products.products"))

    except Exception:
        flash("An unexpected error occurred.", "error")
        logger.exception(f"Unexpected error while updating product status | Product ID: {product_id} | Product: '{product['name']}' | SKU: '{product['sku']}' | Old Status: {product['is_active']} | New Status: {is_active} | User: {session['user']['username']}")
        return redirect(url_for("products.products"))
