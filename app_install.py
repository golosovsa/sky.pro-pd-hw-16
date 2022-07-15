"""
    install_app
"""

# global imports
import datetime
from operator import itemgetter
from flask import Flask
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path
import os
import dotenv
import json


# local imports
from main.models import db, User, Order, Offer
from app import create_app

app: Flask = create_app()
db.init_app(app)


def create_tables():
    """ Create all tables """

    print("Create tables ... ", end="")

    if os.getenv("DB_CREATED_ALL") is None:

        session: Session = db.session
        with session.begin():

            try:
                db.create_all()
                session.commit()
            except SQLAlchemyError as exception:
                session.rollback()
                print("Failed")
                raise exception
            else:
                dotenv.set_key(".env", "DB_CREATED_ALL", "YES")

    print("Done")


def fill_tables():
    """ Fill all tables from json """

    print("Fill tables ... ", end="")

    if os.getenv("DB_FILLED_ALL") is None:

        data_path = Path.cwd() / "data/json_source"

        data_file = data_path / "users.json"

        with data_file.open("rt", encoding="utf-8") as fin:
            data_users = json.load(fin)

        data_file = data_path / "orders.json"

        with data_file.open("rt", encoding="utf-8") as fin:
            data_orders = json.load(fin)

        data_file = data_path / "offers.json"

        with data_file.open("rt", encoding="utf-8") as fin:
            data_offers = json.load(fin)

        data_users = sorted(data_users, key=itemgetter("id"))
        data_orders = sorted(data_orders, key=itemgetter("id"))
        data_offers = sorted(data_offers, key=itemgetter("id"))

        session: Session = db.session
        with session.begin():
            try:
                for user in data_users:
                    del user["id"]
                    session.add(User(**user))
                    session.flush()

            except SQLAlchemyError as exception:
                session.rollback()
                print("Failed")
                raise exception

            else:
                session.commit()

        with session.begin():
            try:
                for order in data_orders:
                    del order["id"]
                    order["customer_id"] += 1
                    order["executor_id"] += 1
                    order["start_date"] = datetime.datetime.strptime(order["start_date"], "%m/%d/%Y").date()
                    order["end_date"] = datetime.datetime.strptime(order["end_date"], "%m/%d/%Y").date()
                    session.add(Order(**order))
                    session.flush()

            except SQLAlchemyError as exception:
                session.rollback()
                print("Failed")
                raise exception

            else:
                session.commit()

        with session.begin():
            try:
                for offer in data_offers:
                    del offer["id"]
                    offer["order_id"] += 1
                    offer["executor_id"] += 1
                    session.add(Offer(**offer))
                    session.flush()

            except SQLAlchemyError as exception:
                session.rollback()
                print("Failed")
                raise exception

            else:
                session.commit()

    dotenv.set_key(".env", "DB_FILLED_ALL", "YES")
    print("Done")


with app.app_context():
    create_tables()
    fill_tables()

print("Setup completed.")
