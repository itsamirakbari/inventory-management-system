import mysql.connector
import logging

from contextlib import closing
from flask import current_app
from logging_config import LOGGER_NAME

logger = logging.getLogger(f"{LOGGER_NAME}.db")


def get_connection():
    return mysql.connector.connect(
        host=current_app.config["MYSQL_HOST"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DATABASE"]
    )


def fetch_one(query, params=None):
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                cursor.execute(query, params)

                return cursor.fetchone()

    except mysql.connector.Error:
        logger.exception("Database error in fetch_one()")
        raise


def fetch_all(query, params=None):
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                cursor.execute(query, params)

                return cursor.fetchall()

    except mysql.connector.Error:
        logger.exception("Database error in fetch_all()")
        raise


def execute(query, params=None):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params)
        connection.commit()

        return cursor.rowcount

    except mysql.connector.Error:
        if connection is not None and connection.is_connected():
            try:
                connection.rollback()
            except mysql.connector.Error:
                logger.exception("Database rollback failed in execute()")

        logger.exception("Database error in execute()")
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def execute_insert(query, params=None):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query, params)
        inserted_id = cursor.lastrowid

        connection.commit()

        return inserted_id

    except mysql.connector.Error:
        if connection is not None and connection.is_connected():
            try:
                connection.rollback()
            except mysql.connector.Error:
                logger.exception("Database rollback failed in execute_insert()")

        logger.exception("Database error in execute_insert()")
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


#______Users______
def get_user_by_id(user_id):
    query = """
        SELECT * FROM users WHERE id = %s
    """

    return fetch_one(query, (user_id,))


def get_user_by_username(username):
    query = """
        SELECT * FROM users WHERE username = %s
    """

    return fetch_one(query, (username,))


def get_user_by_email(email):
    query = """
        SELECT * FROM users WHERE email = %s
    """

    return fetch_one(query, (email,))


def get_all_users():
    query = """
        SELECT * FROM users
        ORDER BY username ASC
    """

    return fetch_all(query)


def create_user(username, email, password_hash):
    query = """
        INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)
    """

    return execute(query, (username, email, password_hash))


def update_user_password(user_id, password_hash):
    query = """
        UPDATE users SET password_hash = %s WHERE id = %s
    """

    return execute(query, (password_hash, user_id))


def update_user_email(user_id, email):
    query = """
        UPDATE users
        SET email = %s
        WHERE id = %s
    """

    return execute(query, (email, user_id))


#______Categories______
def get_all_categories():
    query = """
        SELECT * FROM categories
        ORDER BY name ASC
    """

    return fetch_all(query)


def get_category_by_id(category_id):
    query = """
        SELECT * FROM categories WHERE id = %s
    """

    return fetch_one(query, (category_id,))

def get_category_by_name(category_name):
    query = """
        SELECT * FROM categories WHERE name = %s
    """

    return fetch_one(query, (category_name,))


def create_category(category_name, category_description):
    query = """
        INSERT INTO categories (name, description) VALUES (%s, %s)
    """

    return execute(query, (category_name, category_description))


def update_category(category_id, category_name, category_description):
    query = """
        UPDATE categories SET name = %s, description = %s WHERE id = %s
    """

    return execute(query, (category_name, category_description, category_id))


def delete_category(category_id):
    query = """
        DELETE FROM categories WHERE id = %s
    """

    return execute(query, (category_id,))


#______Suppliers______
def get_all_suppliers():
    query = """
        SELECT * FROM suppliers
        ORDER BY company_name ASC
    """

    return fetch_all(query)


def get_supplier_by_id(supplier_id):
    query = """
        SELECT * FROM suppliers WHERE id = %s
    """

    return fetch_one(query, (supplier_id,))

def get_supplier_by_name(supplier_name):
    query = """
        SELECT * FROM suppliers WHERE company_name = %s
    """

    return fetch_one(query, (supplier_name,))


def create_supplier(
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
):
    query = """
        INSERT INTO
        suppliers (company_name, contact_person, email, phone, street, house_number, postal_code, city, country, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    return execute(query, (company_name, contact_person, email, phone, street, house_number, postal_code, city, country, description))


def update_supplier(
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
):
    query = """
        UPDATE suppliers
        SET company_name = %s,
            contact_person = %s,
            email = %s,
            phone = %s,
            street = %s,
            house_number = %s,
            postal_code = %s,
            city = %s,
            country = %s,
            description = %s
        WHERE id = %s
    """

    return execute(query, (company_name, contact_person, email, phone, street, house_number, postal_code, city, country, description, supplier_id))


def delete_supplier(supplier_id):
    query = """
        DELETE FROM suppliers WHERE id = %s
    """

    return execute(query, (supplier_id,))


# ______Customers______
def get_all_customers():
    query = """
        SELECT * FROM customers
        ORDER BY customer_name ASC
    """

    return fetch_all(query)


def get_active_customers():
    query = """
        SELECT * FROM customers WHERE is_active = 1
        ORDER BY customer_name ASC
    """

    return fetch_all(query)


def get_customer_by_id(customer_id):
    query = """
        SELECT * FROM customers WHERE id = %s
    """

    return fetch_one(query, (customer_id,))


def get_customer_by_name_and_address(customer_name, street, house_number, postal_code, city, country):
    query = """
        SELECT * FROM customers
        WHERE customer_name = %s
        AND street = %s
        AND house_number = %s
        AND postal_code = %s
        AND city = %s
        AND country = %s
    """

    return fetch_one(query, (customer_name, street, house_number, postal_code, city, country))


def create_customer(
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
):
    query = """
        INSERT INTO
        customers (customer_name, contact_person, email, phone, street, house_number, postal_code, city, country, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    return execute(query, (customer_name, contact_person, email, phone, street, house_number, postal_code, city, country, description))


def update_customer(
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
):
    query = """
        UPDATE customers
        SET customer_name = %s,
            contact_person = %s,
            email = %s,
            phone = %s,
            street = %s,
            house_number = %s,
            postal_code = %s,
            city = %s,
            country = %s,
            description = %s
        WHERE id = %s
    """

    return execute(query, (customer_name, contact_person, email, phone, street, house_number, postal_code, city, country, description, customer_id))


def update_customer_status(customer_id, is_active):
    query = """
        UPDATE customers
        SET is_active = %s
        WHERE id = %s
    """

    return execute(query, (is_active, customer_id))


#______Products______
def get_all_products():
    query = """
        SELECT * FROM products
        ORDER BY name ASC
    """

    return fetch_all(query)


def get_available_products():
    query = """
        SELECT id, name, sku, price, stock_quantity
        FROM products
        WHERE is_active = 1
        AND stock_quantity > 0
        ORDER BY name ASC
    """

    return fetch_all(query)


def get_product_by_id(product_id):
    query = """
        SELECT * FROM products WHERE id = %s
    """

    return fetch_one(query, (product_id,))


def get_product_by_sku(sku):
    query = """
        SELECT * FROM products WHERE sku = %s
    """

    return fetch_one(query, (sku,))


def create_product(
        product_name,
        sku,
        price,
        stock_quantity,
        category_id,
        supplier_id
):
    query = """
        INSERT INTO
        products (name, sku, price, stock_quantity, category_id, supplier_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    return execute(query, (product_name, sku, price, stock_quantity, category_id, supplier_id))


def update_product(product_id, product_name, sku, price, stock_quantity, category_id, supplier_id):
    query = """
        UPDATE products
        SET name = %s,
            sku = %s,
            price = %s,
            stock_quantity = %s,
            category_id = %s,
            supplier_id = %s
        WHERE id = %s
    """

    return execute(query, (product_name, sku, price, stock_quantity, category_id, supplier_id, product_id))


def delete_product(product_id):
    query = """
        DELETE FROM products WHERE id = %s
    """

    return execute(query, (product_id,))


def update_product_status(product_id, is_active):
    query = """
        UPDATE products
        SET is_active = %s
        WHERE id = %s
    """

    return execute(query, (is_active, product_id))


# ______Invoices______
def get_all_invoices():
    query = """
        SELECT
            invoices.id,
            invoices.invoice_number,
            invoices.customer_id,
            invoices.user_id,
            invoices.invoice_date,
            invoices.status,
            invoices.total_amount,
            invoices.note,
            invoices.created_at,
            invoices.updated_at,
            customers.customer_name,
            users.username
        FROM invoices
        JOIN customers ON customers.id = invoices.customer_id
        JOIN users ON users.id = invoices.user_id
        ORDER BY invoices.invoice_date DESC, invoices.id DESC
    """

    return fetch_all(query)


def get_invoice_by_id(invoice_id):
    query = """
        SELECT
            invoices.id,
            invoices.invoice_number,
            invoices.customer_id,
            invoices.user_id,
            invoices.invoice_date,
            invoices.status,
            invoices.total_amount,
            invoices.note,
            invoices.created_at,
            invoices.updated_at,
            customers.customer_name,
            customers.contact_person,
            customers.email,
            customers.phone,
            customers.street,
            customers.house_number,
            customers.postal_code,
            customers.city,
            customers.country,
            users.username
        FROM invoices
        JOIN customers ON customers.id = invoices.customer_id
        JOIN users ON users.id = invoices.user_id
        WHERE invoices.id = %s
    """

    return fetch_one(query, (invoice_id,))


def get_invoice_items(invoice_id):
    query = """
        SELECT
            invoice_items.id,
            invoice_items.invoice_id,
            invoice_items.product_id,
            invoice_items.quantity,
            invoice_items.unit_price,
            invoice_items.created_at,
            products.name AS product_name,
            products.sku AS product_sku
        FROM invoice_items
        JOIN products ON products.id = invoice_items.product_id
        WHERE invoice_items.invoice_id = %s
        ORDER BY invoice_items.id ASC
    """

    return fetch_all(query, (invoice_id,))


def create_invoice(
        invoice_number,
        customer_id,
        user_id,
        invoice_date,
        total_amount,
        note
):
    query = """
        INSERT INTO
        invoices (invoice_number, customer_id, user_id, invoice_date, total_amount, note)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    return execute_insert(query, (invoice_number, customer_id, user_id, invoice_date, total_amount, note))


def create_invoice_item(
        invoice_id,
        product_id,
        quantity,
        unit_price
):
    query = """
        INSERT INTO
        invoice_items (invoice_id, product_id, quantity, unit_price)
        VALUES (%s, %s, %s, %s)
    """

    return execute(query, (invoice_id, product_id, quantity, unit_price))


def update_invoice_status(invoice_id, status):
    allowed_statuses = ("open", "paid")

    if status not in allowed_statuses:
        raise ValueError("Invalid invoice status.")

    query = """
        UPDATE invoices
        SET status = %s
        WHERE id = %s
    """

    return execute(query, (status, invoice_id))


#______Inventory_transactions______
def get_inventory_transaction_by_id(transaction_id):
    query = """
        SELECT * FROM inventory_transactions WHERE id = %s
    """

    return fetch_one(query, (transaction_id,))


def get_all_inventory_transactions(product_id=None, user_id=None, start_date=None, end_date=None):
    query = """
        SELECT * FROM inventory_transactions
    """

    conditions = []
    params = []

    if product_id is not None:
        conditions.append("product_id = %s")
        params.append(product_id)

    if user_id is not None:
        conditions.append("user_id = %s")
        params.append(user_id)


    if start_date and end_date:
        conditions.append("DATE(created_at) BETWEEN %s AND %s")
        params.extend([start_date, end_date])
    elif start_date:
        conditions.append("DATE(created_at) >= %s")
        params.append(start_date)
    elif end_date:
        conditions.append("DATE(created_at) <= %s")
        params.append(end_date)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return fetch_all(query, tuple(params) if params else None)


def create_inventory_transaction_with_stock_update(
        transaction_type,
        product_id,
        user_id,
        quantity,
        reason,
        transaction_reference,
        note
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        connection.start_transaction()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, sku, stock_quantity, is_active
            FROM products
            WHERE id = %s
            FOR UPDATE
            """,
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            raise ValueError("Product not found.")

        if not product["is_active"]:
            raise ValueError("Inactive products cannot receive new inventory transactions.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        current_stock = product["stock_quantity"]

        if transaction_type in ("stock_in", "adjustment_in"):
            new_stock = current_stock + quantity
        elif transaction_type in ("stock_out", "adjustment_out"):
            new_stock = current_stock - quantity
        else:
            raise ValueError("Invalid transaction type.")

        if new_stock < 0:
            raise ValueError("Not enough stock for this transaction.")

        cursor.execute(
            """
            INSERT INTO inventory_transactions (
                transaction_type,
                product_id,
                user_id,
                quantity,
                reason,
                transaction_reference,
                note
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                transaction_type,
                product_id,
                user_id,
                quantity,
                reason,
                transaction_reference,
                note
            )
        )
        transaction_id = cursor.lastrowid

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = %s
            WHERE id = %s
            """,
            (new_stock, product_id)
        )

        if cursor.rowcount != 1:
            raise RuntimeError("Product stock could not be updated.")

        connection.commit()

        return {
            "transaction_id": transaction_id,
            "product": product,
            "old_stock": current_stock,
            "new_stock": new_stock
        }

    except Exception:
        if connection is not None and connection.is_connected():
            try:
                connection.rollback()
            except mysql.connector.Error:
                logger.exception(
                    "Database rollback failed while creating inventory transaction"
                )
        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


#______Dashboard______
# KPI-Funktionen
def get_total_products_count():
    query = """
        SELECT COUNT(*) AS total_products FROM products
    """
    result = fetch_one(query)

    return result['total_products']


def get_active_products_count():
    query = """
        SELECT COUNT(*) AS active_products FROM products WHERE is_active = 1
    """
    result = fetch_one(query)

    return result['active_products']


def get_low_stock_products_count(low_stock_threshold=5):
    query = """
        SELECT COUNT(*) AS low_stock_products
        FROM products
        WHERE is_active = 1
        AND stock_quantity > 0
        AND stock_quantity <= %s
    """
    result = fetch_one(query, (low_stock_threshold,))

    return result['low_stock_products']


def get_today_transactions_count():
    query = """
        SELECT COUNT(*) AS today_transactions
        FROM inventory_transactions
        WHERE DATE(created_at) = CURDATE()
    """
    result = fetch_one(query)

    return result['today_transactions']


# Recent-Transactions
def get_recent_inventory_transactions(limit=5):
    query = """
        SELECT
            inventory_transactions.id,
            inventory_transactions.transaction_type,
            inventory_transactions.quantity,
            inventory_transactions.reason,
            inventory_transactions.transaction_reference,
            inventory_transactions.created_at,
            products.name AS product_name,
            products.sku AS product_sku,
            users.username AS username
        FROM inventory_transactions

        JOIN products ON products.id = inventory_transactions.product_id
        JOIN users ON users.id = inventory_transactions.user_id

        ORDER BY inventory_transactions.created_at DESC
        LIMIT %s
    """

    return fetch_all(query, (limit,))


# Alerts
def get_low_stock_products(limit=5, low_stock_threshold=5):
    query = """
        SELECT id, name, sku, stock_quantity
        FROM products
        WHERE is_active = 1
        AND stock_quantity > 0
        AND stock_quantity <= %s
        ORDER BY stock_quantity ASC, name ASC
        LIMIT %s
    """

    return fetch_all(query, (low_stock_threshold, limit,))


def get_out_of_stock_products(limit=5):
    query = """
        SELECT id, name, sku, stock_quantity
        FROM products
        WHERE is_active = 1
        AND stock_quantity = 0
        ORDER BY stock_quantity ASC, name ASC
        LIMIT %s
    """

    return fetch_all(query, (limit,))













