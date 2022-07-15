"""
    orders blueprint
    views
"""


# global imports
from flask import Blueprint, request, current_app


# local imports
from .adapter import \
    AllOrdersAdapter, \
    OrderByPKAdapter, \
    PKOrderListAdapter, \
    AddOrderAdapter, \
    UpdateOrderAdapter, \
    DeleteOrderAdapter

bp_orders = Blueprint("bp_orders", __name__)


@bp_orders.route("/", methods=["GET"])
def index_all_orders():

    limit = request.args.get("limit", 5, type=int)
    offset = request.args.get("offset", 0, type=int)
    filter_by = request.args.get("filter_by", "default", type=str)
    order_by = request.args.get("order_by", "default", type=str)
    user_pk = request.args.get("user_pk", None, type=int)

    with current_app.app_context():
        json_object = AllOrdersAdapter(limit, offset, filter_by, order_by, user_pk).jsonify()

    return json_object, 200


@bp_orders.route("/<int:pk>", methods=["GET"])
def index_order_by_pk(pk):

    with current_app.app_context():
        json_object = OrderByPKAdapter(pk).jsonify()

    return json_object, 200


@bp_orders.route("/count", methods=["GET"])
def index_get_orders_count():

    filter_by = request.args.get("filter_by", "default", type=str)
    user_pk = request.args.get("user_pk", None, type=int)

    with current_app.app_context():
        json_object = PKOrderListAdapter(filter_by, user_pk).jsonify()

    return json_object, 200


@bp_orders.route("/", methods=["POST"])
def index_add_new_order():

    with current_app.app_context():
        json_object = AddOrderAdapter(request.json).jsonify()

    return json_object, 200


@bp_orders.route("/<int:pk>", methods=["PUT"])
def index_update_order_by_pk(pk):

    with current_app.app_context():
        json_object = UpdateOrderAdapter(request.json, pk).jsonify()

    return json_object, 200


@bp_orders.route("/<int:pk>", methods=["DELETE"])
def index_delete_order_by_pk(pk):

    with current_app.app_context():
        json_object = DeleteOrderAdapter(pk).jsonify()

    return json_object, 200
