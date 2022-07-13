"""
    users blueprint
    adapter
"""
from sqlalchemy import func
from sqlalchemy.orm import Query

from grm import BaseAdapter, to_dict_from_alchemy_model as to_dict
from main.models import db, User, Order


class AllUsersAdapter(BaseAdapter):

    def __init__(self, limit, offset, order_by):

        query: Query = User.query

        self._data = query.with_entities(func.count(User.orders_owner), func.count(User.orders_executor)).all()

