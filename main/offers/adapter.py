"""
    offers blueprint
    adapter
"""


# global imports
from sqlalchemy import func, or_, and_, desc, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query, aliased, load_only, Session

# local imports
from sqlalchemy.sql import label

from grm import BaseAdapter, to_dict_from_alchemy_model as to_dict
from main.models import db, User, Order, Offer
from main.models_checkers import check_pk


class AllOffersAdapter(BaseAdapter):

    filter_by_list = ["default", "user", "order", "rejected", "approved", "user_rejected", "user_approved"]
    order_by_list = ["default", "user", "order", "order_date", "order_date_asc"]

    def __init__(self, limit=10, offset=0, filter_by="default", order_by="default", user_pk=None, order_pk=None):

        if limit < 1:
            limit = 10

        if offset < 0:
            offset = 0

        if filter_by not in self.filter_by_list:
            filter_by = self.filter_by_list[0]

        if order_by not in self.order_by_list:
            order_by = self.order_by_list[0]

        query: Query = Offer.query
        query = query.with_entities(
            Offer,
            func.concat(User.first_name, " ", User.last_name).label('user_full_name'),
            (Order.executor_id == Offer.executor_id).label("is_approved"),
            Order.start_date
        )\
            .join(User, User.id == Offer.executor_id, isouter=True)\
            .join(Order, Order.id == Offer.order_id, isouter=True)

        if filter_by == "default":
            pass
        elif filter_by == "user" and type(user_pk) is int:
            query: Query = query.filter(Offer.executor_id == user_pk)
        elif filter_by == "order" and type(order_pk) is int:
            query: Query = query.filter(Offer.order_id == order_pk)
        elif filter_by == "rejected":
            query: Query = query.filter((Order.executor_id == Offer.executor_id) == False)
        elif filter_by == "approved":
            query: Query = query.filter((Order.executor_id == Offer.executor_id) == True)
        elif filter_by == "user_rejected" and type(user_pk) is int:
            query: Query = query.filter(
                (Order.executor_id == Offer.executor_id) == False,
                Offer.executor_id == user_pk
            )
        elif filter_by == "user_approved":
            query: Query = query.filter(
                (Order.executor_id == Offer.executor_id) == True,
                Offer.executor_id == user_pk
            )

        if order_by == "default" or order_by == "user":
            query: Query = query.order_by('user_full_name')
        elif order_by == "order":
            query: Query = query.order_by(Offer.order_id)
        elif order_by == "order_date":
            query: Query = query.order_by(desc(Order.start_date))
        elif order_by == "order_date_asc":
            query: Query = query.order_by(Order.start_date)

        query: Query = query.limit(limit).offset(offset)

        self._data = [{
            **to_dict(row[0]),
            "executor": row[1],
            "is_approved": row[2],
            "start": row[3],
        } for row in query.all()]


class OfferByPKAdapter(BaseAdapter):

    def __init__(self, pk):

        if pk < 1:
            self._data = None
            return

        self._data = to_dict(Offer.query.get(pk))


class PKOfferListAdapter(BaseAdapter):

    def __init__(self, filter_by, user_pk, order_pk):

        if filter_by not in AllOffersAdapter.filter_by_list:
            filter_by = AllOffersAdapter.filter_by_list[0]

        query: Query = Offer.query.with_entities(func.count(Offer.id))\
            .join(Order, Order.id == Offer.order_id, isouter=True)

        if filter_by == "default":
            pass
        elif filter_by == "user" and type(user_pk) is int:
            query: Query = query.filter(Offer.executor_id == user_pk)
        elif filter_by == "order" and type(order_pk) is int:
            query: Query = query.filter(Offer.order_id == order_pk)
        elif filter_by == "rejected":
            query: Query = query.filter((Order.executor_id == Offer.executor_id) == False)
        elif filter_by == "approved":
            query: Query = query.filter((Order.executor_id == Offer.executor_id) == True)
        elif filter_by == "user_rejected" and type(user_pk) is int:
            query: Query = query.filter(
                (Order.executor_id == Offer.executor_id) == False,
                Offer.executor_id == user_pk
            )
        elif filter_by == "user_approved":
            query: Query = query.filter(
                (Order.executor_id == Offer.executor_id) == True,
                Offer.executor_id == user_pk
            )

        self._data = {
            "count": query.scalar(),
            "user_pk": user_pk,
            "order_pk": order_pk,
            "filter_by": filter_by
        }


class AddOfferAdapter(BaseAdapter):

    def __init__(self, json_object):

        order_id = json_object.get("order_id", None)
        executor_id = json_object.get("executor_id", None)

        check_result = [result for result in [
            check_pk(order_id),
            check_pk(executor_id)
        ] if result is not None]

        if len(check_result) != 0:
            self._data = {
                "status": "error",
                "message": "\n".join(check_result)
            }
            return

        try:
            order: Order = Order.query.get(order_id)
        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": "\n".join(["Order not found", str(exception)])
            }
            return

        try:
            executor: User = User.query.get(executor_id)
        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": "\n".join(["Executor not found", str(exception)])
            }
            return

        if order.executor_id == executor.id:
            self._data = {
                "status": "error",
                "message": "Executor already in the order"
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
                    Offer(
                        order_id=order_id,
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


class UpdateOfferAdapter(BaseAdapter):

    def __init__(self, json_object, pk):
        check_result = check_pk(pk)

        if isinstance(check_result, str):
            self._data = {
                "status": "error",
                "message": check_result
            }
            return

        try:
            offer: Offer = Offer.query.get(pk)

        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": str(exception)
            }
            return

        order_id = json_object.get("order_id", None)
        executor_id = json_object.get("executor_id", None)

        if not any([order_id, executor_id]):
            self._data = {
                "status": "error",
                "message": "Missing data"
            }
            return

        check_result = [result for result in [
            check_pk(order_id) if order_id is not None else None,
            check_pk(executor_id) if executor_id  is not None else None
        ] if result is not None]

        if len(check_result) != 0:
            self._data = {
                "status": "error",
                "message": "\n".join(check_result)
            }
            return

        if order_id:
            try:
                order: Order = Order.query.get(order_id)
            except SQLAlchemyError as exception:
                self._data = {
                    "status": "error",
                    "message": "\n".join(["Order not found", str(exception)])
                }
                return
        else:
            order = Order.query.get(offer.order_id)

        if executor_id:
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
        else:
            executor: User = User.query.get(offer.executor_id)

        if order_id or executor_id:
            if order.executor_id == executor.id:
                self._data = {
                    "status": "error",
                    "message": "Executor already in the order"
                }
                return

        if order_id:
            offer.order_id = order_id

        if executor_id:
            if executor.role != "executor":
                self._data = {
                    "status": "error",
                    "message": "You have chosen not the executor"
                }
                return
            offer.executor_id = executor_id

        session: Session = db.session
        with session():

            try:
                session.add(
                    Offer(offer)
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


class DeleteOfferAdapter(BaseAdapter):

    def __init__(self, pk):

        check_result = check_pk(pk)

        if isinstance(check_result, str):
            self._data = {
                "status": "error",
                "message": check_result
            }
            return

        try:
            offer: Offer = Offer.query.get(pk)

        except SQLAlchemyError as exception:
            self._data = {
                "status": "error",
                "message": str(exception)
            }
            return

        session: Session = db.session
        with session():
            try:
                session.delete(offer)
                session.commit()

            except SQLAlchemyError as exception:
                session.rollback()
                self._data = {
                    "status": "error",
                    "message": str(exception)
                }
                return

        self._data = {"status": "ok", "message": None}
