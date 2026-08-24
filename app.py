import logging

from flask import Flask, render_template
from config import Config
from logging_config import setup_logging, LOGGER_NAME
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.categories import categories_bp
from routes.suppliers import suppliers_bp
from routes.products import products_bp
from routes.inventory_transactions import inventory_transactions_bp
from routes.profile import profile_bp



app = Flask(__name__)
app.config.from_object(Config)

setup_logging()
logger = logging.getLogger(LOGGER_NAME)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(categories_bp, url_prefix="/categories")
app.register_blueprint(suppliers_bp, url_prefix="/suppliers")
app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(inventory_transactions_bp, url_prefix="/inventory_transactions")
app.register_blueprint(profile_bp, url_prefix="/profile")




@app.route("/")
def home():
    return render_template("home.html")




#---------RUN---------
if __name__ == "__main__":
    app.run(debug=True)



