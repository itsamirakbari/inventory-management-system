import logging

from datetime import datetime, timedelta
from flask import Blueprint, render_template
from db import get_total_products_count, get_active_products_count, get_low_stock_products_count, get_today_transactions_count, get_recent_inventory_transactions, get_low_stock_products, get_out_of_stock_products
from logging_config import LOGGER_NAME
from utils.decorators import login_required


dashboard_bp = Blueprint('dashboard', __name__)
logger =logging.getLogger(LOGGER_NAME)


@dashboard_bp.route("/")
@login_required
def dashboard():
    total_products = get_total_products_count()
    active_products = get_active_products_count()
    low_stock_products_count = get_low_stock_products_count()
    today_transactions = get_today_transactions_count()

    recent_transactions = get_recent_inventory_transactions()

    today = datetime.today().date()
    yesterday = today - timedelta(days=1)

    for transaction in recent_transactions:
        transaction_date = transaction["created_at"].date()

        if transaction_date == today:
            transaction["display_day"] = "Today"
        elif transaction_date == yesterday:
            transaction["display_day"] = "Yesterday"
        else:
            transaction["display_day"] = transaction["created_at"].strftime("%d.%m.%Y")

        transaction["display_time"] = transaction["created_at"].strftime("%I:%M %p")

    out_of_stock_products = get_out_of_stock_products()
    low_stock_products = get_low_stock_products()

    for product in out_of_stock_products:
        product["alert_type"] = "out_of_stock"

    for product in low_stock_products:
        product["alert_type"] = "low_stock"

    dashboard_alerts = out_of_stock_products + low_stock_products
    dashboard_alerts = dashboard_alerts[:5]

    return render_template("dashboard.html",
                           total_products=total_products,
                           active_products=active_products,
                           low_stock_products_count=low_stock_products_count,
                           today_transactions=today_transactions,
                           recent_transactions=recent_transactions,
                           dashboard_alerts=dashboard_alerts
    )