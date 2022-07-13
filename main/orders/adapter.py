"""
    orders blueprint
    adapter
"""


# global imports
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.orm import Query, aliased, load_only


# local imports
from grm import BaseAdapter, to_dict_from_alchemy_model as to_dict
from main.models import db, User, Order, Offer


class AllOrdersAdapter(BaseAdapter):

    filter_by_list = ["default", "customer", "executor"]
    order_by_list = ["default", "start", "start_asc", "end", "end_asc", "price", "price_asc"]

    def __init__(self, limit=10, offset=0, filter_by="default", order_by="default", user_pk=None):

        if limit < 1:
            limit = 10

        if offset < 0:
            offset = 0

        if filter_by not in self.filter_by_list:
            filter_by = self.filter_by_list[0]

        if order_by not in self.order_by_list:
            order_by = self.order_by_list[0]

        query: Query = Order.query

        customer = aliased(User)
        executor = aliased(User)

        query = query.with_entities(
            Order,
            func.concat(customer.first_name, " ", customer.last_name),
            func.concat(executor.first_name, " ", executor.last_name)
        )\
            .join(customer, customer.id == Order.customer_id, isouter=True)\
            .join(executor, executor.id == Order.executor_id, isouter=True)

        if filter_by == "default":
            pass
        elif filter_by == "customer" and type(user_pk) is int:
            query: Query = query.filter(Order.customer_id == user_pk)
        elif filter_by == "executor" and type(user_pk) is int:
            query: Query = query.filter(Order.executor_id == user_pk)

        if order_by == "default" or order_by == "start_asc":
            query: Query = query.order_by(Order.start_date)
        elif order_by == "start":
            query: Query = query.order_by(desc(Order.start_date))
        elif order_by == "end":
            query: Query = query.order_by(desc(Order.end_date))
        elif order_by == "end_asc":
            query: Query = query.order_by(Order.end_date)
        elif order_by == "price":
            query: Query = query.order_by(desc(Order.price))
        elif order_by == "price_asc":
            query: Query = query.order_by(Order.price)

        query: Query = query.limit(limit).offset(offset)

        self._data = [{
            **to_dict(row[0]),
            "customer": row[1],
            "executor": row[2]
        } for row in query.all()]


class OrderByPKAdapter(BaseAdapter):

    def __init__(self, pk):

        if pk < 1:
            self._data = None
            return

        self._data = to_dict(Order.query.get(pk))


class PKOrderListAdapter(BaseAdapter):

    def __init__(self, filter_by="default", user_pk=None):

        if filter_by not in AllOrdersAdapter.filter_by_list:
            filter_by = AllOrdersAdapter.filter_by_list[0]

        query: Query = User.query.with_entities(func.count(Order.id))

        if filter_by == "default":
            pass
        elif filter_by == "customer" and type(user_pk) is int:
            query: Query = query.filter(Order.customer_id == user_pk)
        elif filter_by == "executor" and type(user_pk) is int:
            query: Query = query.filter(Order.executor_id == user_pk)

        print(query)

        self._data = {"count": query.scalar(), "pk": user_pk}
