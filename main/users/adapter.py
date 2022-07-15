"""
    users blueprint
    adapter
"""

# global imports
from typing import Optional

from sqlalchemy import func, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query, aliased, Session

# local imports
from grm import BaseAdapter, to_dict_from_alchemy_model as to_dict
from main.models import db, User, Order, Offer
from main.models_checkers import \
    check_name, check_age, check_email, check_role, \
    check_phone, check_pk


class AllUsersAdapter(BaseAdapter):
    filter_by_list = ["default", "customer", "executor"]
    order_by_list = ["default", "age", "age_asc", "owner", "owner_asc", "executor", "executor_asc", "offers"]

    def __init__(self, limit=5, offset=0, filter_by="default", order_by="default"):

        if limit < 1:
            limit = 5

        if offset < 0:
            offset = 0

        if filter_by not in self.filter_by_list:
            filter_by = self.filter_by_list[0]

        if order_by not in self.order_by_list:
            order_by = self.order_by_list[0]

        query: Query = User.query

        orders_owner = aliased(Order)
        orders_executor = aliased(Order)

        query = query.with_entities(
            User,
            func.count(orders_owner.id),
            func.count(orders_executor.id),
            func.count(Offer.id)) \
            .join(orders_owner, orders_owner.customer_id == User.id, isouter=True) \
            .join(orders_executor, orders_executor.executor_id == User.id, isouter=True) \
            .join(Offer, Offer.executor_id == User.id, isouter=True)

        if filter_by == "default":
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


class PKUserListAdapter(BaseAdapter):

    def __init__(self, filter_by="default"):

        if filter_by not in AllUsersAdapter.filter_by_list:
            filter_by = AllUsersAdapter.filter_by_list[0]

        query: Query = User.query
        query = query.with_entities(func.count(User.id))

        if filter_by == "default":
            pass
        elif filter_by == "customer":
            query: Query = query.filter(User.role == "customer")
        elif filter_by == "executor":
            query: Query = query.filter(User.role == "executor")

        # self._data = [row[0] for row in query.all()]
        self._data = {"count": query.scalar()}


class AddUserAdapter(BaseAdapter):

    def __init__(self, json_object):

        first_name = json_object.get("first_name", None)
        last_name = json_object.get("last_name", None)
        age = json_object.get("age", None)
        email = json_object.get("email", None)
        role = json_object.get("role", None)
        phone = json_object.get("phone", None)

        check_result = [result for result in [
            check_name(first_name),
            check_name(last_name),
            check_age(age),
            check_email(email),
            check_role(role),
            check_phone(phone)
        ] if result is not None]

        if len(check_result) != 0:
            self._data = {
                "status": "error",
                "message": "\n".join(check_result)
            }
            return

        session: Session = db.session
        with session():

            try:
                session.add(
                    User(
                        first_name=json_object["first_name"],
                        last_name=json_object["last_name"],
                        age=json_object["age"],
                        email=json_object["email"],
                        role=json_object["role"],
                        phone=json_object["phone"],
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


class UpdateUserAdapter(BaseAdapter):

    def __init__(self, json_object, pk):

        check_result = check_pk(pk)

        if isinstance(check_result, str):
            self._data = {
                "status": "error",
                "message": check_result
            }
            return

        first_name = json_object.get("first_name", None)
        last_name = json_object.get("last_name", None)
        age = json_object.get("age", None)
        email = json_object.get("email", None)
        role = json_object.get("role", None)
        phone = json_object.get("phone", None)

        if not any([first_name, last_name, age, email, role, phone]):
            self._data = {
                "status": "error",
                "message": "Missing data"
            }
            return

        check_result = [result for result in [
            check_name(first_name) if first_name is not None else None,
            check_name(last_name) if last_name is not None else None,
            check_age(age) if age is not None else None,
            check_email(email) if email is not None else None,
            check_role(role) if role is not None else None,
            check_phone(phone) if phone is not None else None
        ] if result is not None]

        if len(check_result) != 0:
            self._data = {
                "status": "error",
                "message": "\n".join(check_result)
            }
            return

        try:
            user = User.query.get(pk)

        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": str(exception)
            }
            return

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        if age:
            user.age = age

        if email:
            user.email = email

        if role:
            user.role = role

        if phone:
            user.phone = phone

        session: Session = db.session
        with session():
            try:
                session.add(user)
                session.commit()

            except SQLAlchemyError as exception:
                session.rollback()
                self._data = {
                    "status": "error",
                    "message": str(exception)
                }
                return

        self._data = {"status": "ok", "message": None}


class DeleteUserAdapter(BaseAdapter):

    def __init__(self, pk):

        check_result = check_pk(pk)

        if isinstance(check_result, str):
            self._data = {
                "status": "error",
                "message": check_result
            }
            return

        try:
            user = User.query.get(pk)

        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": str(exception)
            }
            return

        session: Session = db.session
        with session():
            try:
                session.delete(user)
                session.commit()

            except SQLAlchemyError as exception:
                session.rollback()
                self._data = {
                    "status": "error",
                    "message": str(exception)
                }
                return

        self._data = {"status": "ok", "message": None}
