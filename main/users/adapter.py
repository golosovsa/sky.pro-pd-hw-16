"""
    users blueprint
    adapter
"""
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.orm import Query, aliased

from grm import BaseAdapter, to_dict_from_alchemy_model as to_dict
from main.models import db, User, Order, Offer


class AllUsersAdapter(BaseAdapter):

    _filter_by = ["default", "customer", "executor"]
    _order_by = ["default", "age", "age_asc", "owner", "owner_asc", "executor", "executor_asc", "offers"]

    def __init__(self, limit=5, offset=0, filter_by="all", order_by="default"):

        if limit < 1:
            limit = 5

        if offset < 0:
            offset = 0

        if filter_by not in self._filter_by:
            filter_by = self._filter_by[0]

        if order_by not in self._order_by:
            order_by = self._order_by[0]

        query: Query = User.query

        orders_owner = aliased(Order)
        orders_executor = aliased(Order)

        query = query.with_entities(
            User,
            func.count(orders_owner.id),
            func.count(orders_executor.id),
            func.count(Offer.id))\
            .join(orders_owner, orders_owner.customer_id == User.id, isouter=True) \
            .join(orders_executor, orders_executor.executor_id == User.id, isouter=True) \
            .join(Offer, Offer.executor_id == User.id, isouter=True)

        if filter_by == "all":
            pass
        elif filter_by == "customer":
            query: Query = query.filter(User.role == "customer")
        elif filter_by == "executor":
            query: Query = query.filter(User.role == "executor")

        query: Query = query.group_by(User.id)

        if order_by == "default":
            query: Query = query.order_by(User.first_name, User.last_name)
        elif order_by == "age":
            query: Query = query.order_by(desc(User.age))
        elif order_by == "age_asc":
            query: Query = query.order_by(User.age)
        elif order_by == "owner":
            query: Query = query.order_by(desc(func.count(orders_owner.id)))
        elif order_by == "owner_asc":
            query: Query = query.order_by(func.count(orders_owner.id))
        elif order_by == "executor":
            query: Query = query.order_by(desc(func.count(orders_executor.id)))
        elif order_by == "executor_asc":
            query: Query = query.order_by(func.count(orders_executor.id))
        elif order_by == "offers":
            query: Query = query.order_by(desc(func.count(Offer.id)))
        elif order_by == "offers_asc":
            query: Query = query.order_by(func.count(Offer.id))

        query: Query = query.limit(limit).offset(offset)

        print(query)

        self._data = [
            {
                **to_dict(row[0]),
                "orders_owner": row[1],
                "orders_executor": row[2],
                "offers_total": row[3]
            }
            for row in query.all()
        ]


class UserByPKAdapter(BaseAdapter):

    def __init__(self, pk):

        if pk < 1:
            self._data = None
            return

        self._data = to_dict(User.query.get(pk))
