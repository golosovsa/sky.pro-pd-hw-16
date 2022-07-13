"""
    users blueprint
    views
"""


# global imports
from flask import Blueprint


# local imports
from .adapter import AllUsersAdapter


bp_users = Blueprint("bp_users", __name__)


@bp_users.route("/", methods=["GET"])
def index_users_get_response():

    return str(AllUsersAdapter(10, 0, 0)._data)

