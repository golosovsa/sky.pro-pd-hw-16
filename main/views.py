"""
    Main blueprint
    views
"""


# global imports
from flask import Blueprint

# local imports
from .users.views import bp_users
from .orders.views import bp_orders

bp_main = Blueprint("bp_main", __name__)

bp_main.register_blueprint(bp_users, url_prefix="/users/")
bp_main.register_blueprint(bp_orders, url_prefix="/orders/")

