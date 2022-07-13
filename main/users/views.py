"""
    users blueprint
    views
"""


# global imports
from flask import Blueprint, current_app, request


# local imports
from .adapter import AllUsersAdapter, UserByPKAdapter


bp_users = Blueprint("bp_users", __name__)


@bp_users.route("/", methods=["GET"])
def index_users_get_response():

    limit = request.args.get("limit", 5, type=int)
    offset = request.args.get("offset", 0, type=int)
    filter_by = request.args.get("filter_by", "default", type=str)
    order_by = request.args.get("order_by", "default", type=str)

    with current_app.app_context():
        json_object = AllUsersAdapter(limit, offset, filter_by, order_by).jsonify()

    return json_object, 200


@bp_users.route("/<int:pk>", methods=["GET"])
def index_user_by_pk(pk):

    with current_app.app_context():
        json_object = UserByPKAdapter(pk).jsonify()

    return json_object, 200
