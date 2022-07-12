"""
    Main blueprint
    models
"""

# global imports
from flask_sqlalchemy import SQLAlchemy
# local imports
from flask import current_app


db: SQLAlchemy = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint("age >= 18"))
    email = db.Column(db.String(100), nullable=False, unique=False)
    role = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False, unique=True)

    orders_owner = db.relationship("Order", foreign_keys="Order.customer_id")
    orders_executor = db.relationship("Order", foreign_keys="Order.executor_id")
    offers = db.relationship("Offer", foreign_keys="Offer.executor_id")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    executor_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)

    customer = db.relationship("User", foreign_keys="Order.customer_id", back_populates="orders_owner")
    executor = db.relationship("User", foreign_keys="Order.executor_id", back_populates="orders_executor")


class Offer(db.Model):
    __tablename__ = "offers"
    id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.id"), nullable=False)
    executor_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)

    order = db.relationship("Order")
    executor = db.relationship("User", back_populates="offers")
