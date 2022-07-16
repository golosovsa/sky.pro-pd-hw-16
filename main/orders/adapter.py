"""
    orders blueprint
    adapter
"""


# global imports
import datetime

from sqlalchemy import func, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query, aliased, Session

# local imports
from app_custom_serialization import to_date
from grm import BaseAdapter, to_dict_from_alchemy_model as to_dict
from main.models import db, User, Order
from main.models_checkers import check_description, check_date, check_address, check_price, check_pk


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

        query: Query = Order.query.with_entities(func.count(Order.id))

        if filter_by == "default":
            pass
        elif filter_by == "customer" and type(user_pk) is int:
            query: Query = query.filter(Order.customer_id == user_pk)
        elif filter_by == "executor" and type(user_pk) is int:
            query: Query = query.filter(Order.executor_id == user_pk)

        self._data = {"count": query.scalar(), "pk": user_pk}


class AddOrderAdapter(BaseAdapter):

    def __init__(self, json_object):

        start_date = datetime.datetime.today()
        end_date = json_object.get("end_date", None)

        try:
            end_date = to_date(end_date)
        except (TypeError, ValueError) as exception:
            self._data = {
                "status": "error",
                "message": "End date is corrupt"
            }
            return

        description = json_object.get("description", None)
        address = json_object.get("address", None)
        price = json_object.get("price", None)
        customer_id = json_object.get("customer_id", None)
        executor_id = json_object.get("executor_id", None)

        check_result = [result for result in [
            check_description(description),
            check_date(end_date, start_date),
            check_address(address),
            check_price(price),
            check_pk(customer_id),
            check_pk(executor_id)
        ] if result is not None]

        if len(check_result) != 0:
            self._data = {
                "status": "error",
                "message": "\n".join(check_result)
            }
            return

        try:
            customer: User = User.query.get(customer_id)
            if customer is None:
                raise SQLAlchemyError()
        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": "Customer not found"
            }
            return

        try:
            executor: User = User.query.get(executor_id)
            if executor is None:
                raise SQLAlchemyError()
        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": "Executor not found"
            }
            return

        if customer == executor:
            self._data = {
                "status": "error",
                "message": "You can't place an order for yourself"
            }
            return

        if customer.role != "customer":
            self._data = {
                "status": "error",
                "message": "You are not a customer"
            }
            return

        if executor.role != "executor":
            self._data = {
                "status": "error",
                "message": "You have chosen not the executor"
            }
            return

        session: Session = db.session
        with session():

            try:
                session.add(
                    Order(
                        name=" ".join(description.strip().split()[:4]),
                        description=description,
                        start_date=start_date,
                        end_date=end_date,
                        address=address,
                        price=price,
                        customer_id=customer_id,
                        executor_id=executor_id
                    )
                )

                session.commit()

            except SQLAlchemyError as exception:
                session.rollback()
                self._data = {
                    "status": "error",
                    "message": str(exception)
                }
                return

        self._data = {"status": "ok", "message": None}


class UpdateOrderAdapter(BaseAdapter):

    def __init__(self, json_object, pk):
        check_result = check_pk(pk)

        if isinstance(check_result, str):
            self._data = {
                "status": "error",
                "message": check_result
            }
            return

        try:
            order: Order = Order.query.get(pk)
            if order is None:
                raise SQLAlchemyError()
        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": "Order not found"
            }
            return

        description = json_object.get("description", None)
        end_date = json_object.get("end_date")
        address = json_object.get("address", None)
        price = json_object.get("price", None)
        customer_id = json_object.get("customer_id", None)
        executor_id = json_object.get("executor_id", None)

        if not any([description, address, price, customer_id, executor_id]):
            self._data = {
                "status": "error",
                "message": "Missing data"
            }
            return

        check_result = [result for result in [
            check_description(description) if description is not None else None,
            check_date(end_date, order.start_date) if end_date is not None else None,
            check_address(address) if address is not None else None,
            check_price(price) if price is not None else None,
            check_pk(customer_id) if customer_id is not None else None,
            check_pk(executor_id) if executor_id is not None else None
        ] if result is not None]

        if len(check_result) != 0:
            self._data = {
                "status": "error",
                "message": "\n".join(check_result)
            }
            return

        if description:
            order.description = description
            order.name = " ".join(description.strip().split()[:4])

        if end_date:
            order.end_date = end_date

        if address:
            order.address = address

        if price:
            order.price = price

        if customer_id:
            try:
                customer: User = User.query.get(customer_id)
                if customer is None:
                    raise SQLAlchemyError()
            except SQLAlchemyError as exception:
                self._data = {
                    "status": "error",
                    "message": "Customer not found"
                }
                return
        else:
            customer = User.query.get(order.customer_id)

        if executor_id:
            try:
                executor: User = User.query.get(executor_id)
                if executor is None:
                    raise SQLAlchemyError()
            except SQLAlchemyError as exception:
                self._data = {
                    "status": "error",
                    "message": "Customer not found"
                }
                return
        else:
            executor = User.query.get(order.executor_id)

        if customer_id or executor_id:
            if customer == executor:
                self._data = {
                    "status": "error",
                    "message": "You can't place an order for yourself"
                }
                return

        if customer_id:
            if customer.role != "customer":
                self._data = {
                    "status": "error",
                    "message": "You are not a customer"
                }
                return
            order.customer_id = customer_id

        if executor_id:
            if executor.role != "executor":
                self._data = {
                    "status": "error",
                    "message": "You have chosen not the executor"
                }
                return
            order.executor_id = executor_id

        session: Session = db.session
        with session():

            try:
                session.add(order)
                session.commit()

            except SQLAlchemyError as exception:
                session.rollback()
                self._data = {
                    "status": "error",
                    "message": str(exception)
                }
                return

        self._data = {"status": "ok", "message": None}


class DeleteOrderAdapter(BaseAdapter):

    def __init__(self, pk):

        check_result = check_pk(pk)

        if isinstance(check_result, str):
            self._data = {
                "status": "error",
                "message": check_result
            }
            return

        try:
            order = Order.query.get(pk)
            if order is None:
                raise SQLAlchemyError()
        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": str(exception)
            }
            return

        session: Session = db.session
        with session():
            try:
                session.delete(order)
                session.commit()

            except SQLAlchemyError as exception:
                session.rollback()
                self._data = {
                    "status": "error",
                    "message": str(exception)
                }
                return

        self._data = {"status": "ok", "message": None}
