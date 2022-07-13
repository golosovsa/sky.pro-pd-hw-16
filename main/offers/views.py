"""
    offers blueprint
    views
"""


# global imports
from flask import Blueprint, request, current_app


# local imports
from .adapter import AllOffersAdapter, OfferByPKAdapter, PKOfferListAdapter

bp_offers = Blueprint("bp_offers", __name__)


@bp_offers.route("/", methods=["GET"])
def index_all_offers():

    limit = request.args.get("limit", 5, type=int)
    offset = request.args.get("offset", 0, type=int)
    filter_by = request.args.get("filter_by", "default", type=str)
    order_by = request.args.get("order_by", "default", type=str)
    user_pk = request.args.get("user_pk", None, type=int)
    order_pk = request.args.get("order_pk", None, type=int)

    with current_app.app_context():
        json_data = AllOffersAdapter(limit, offset, filter_by, order_by, user_pk, order_pk).jsonify()

    return json_data, 200


@bp_offers.route("/<int:pk>", methods=["GET"])
def index_offer_by_pk(pk):

    with current_app.app_context():
        json_object = OfferByPKAdapter(pk).jsonify()

    return json_object, 200


@bp_offers.route("/count", methods=["GET"])
def index_get_offers_count():

    filter_by = request.args.get("filter_by", "default", type=str)
    user_pk = request.args.get("user_pk", None, type=int)
    order_pk = request.args.get("order_pk", None, type=int)

    with current_app.app_context():
        json_object = PKOfferListAdapter(filter_by, user_pk, order_pk).jsonify()

    return json_object, 200
