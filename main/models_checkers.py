"""
    Main blueprint
    checkers for models
"""
from __future__ import annotations

import operator
import re
from datetime import datetime
from functools import reduce


low_vowels = "aeiouyаеёиоуыэюя"
email_regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
phone_regex = re.compile(r"^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$")


def check_name(name: str) -> str | None:
    """ Check human name 
    :rtype: object
    """

    # 0. Is name None or not str?

    if not name or not isinstance(name, str):
        return "No name or wrong type"

    name = name.lower()

    # 1. Are there wrong symbols inside?

    result = reduce(
        operator.add,
        [not (
                ("a" <= character <= "z") or
                ("а" <= character <= "я") or
                character in "'"
        ) for character in name]
    )

    if result > 0:
        return "There are wrong symbols inside"

    # 2. Are there more than one space

    result = name.count(" ")

    if result > 0:
        return "There are more than zero spaces"

    # 3. Are there ru and en characters inside?

    result = reduce(
        lambda acc, item: (acc[0] + item[0], acc[1] + item[1]),
        [(
            ("a" <= character <= "z"),
            ("а" <= character <= "я")
        ) for character in name]
    )

    if result[0] and result[1]:
        return "There are ru and en characters inside"

    # 4. Are there more than 2 vowels in a row?

    result = max(reduce(
        lambda acc, item: (acc[0] + 1, *acc[1:], ) if item in "aeiouyаеёиоуыэюя" else (0, *acc),
        [character for character in name],
        (0,)
    ))

    if result > 2:
        return "There are more than 2 vowels in a row"

    # 5. Are there more than 2 consonants in a row?

    result = max(reduce(
        lambda acc, item: (acc[0] + 1, *acc[1:],) if item not in "aeiouyаеёиоуыэюя'" else (0, *acc),
        [character for character in name],
        (0,)
    ))

    if result > 2:
        return "There are more than 2 consonants in a row"


def check_age(age: int) -> str | None:
    """ Check human age """

    # 0. Is age None or not int
    if age is None or not isinstance(age, int):
        return "There isn't age or wrong type"

    # 1. not enough age?

    if age < 18:
        return "Not enough age"

    # 2. Are you too old?

    if age > 65:
        return "You are too old"


def check_email(email: str) -> str | None:
    """ Check E-Mail """

    if not email or not isinstance(email, str):
        return "No E-Mail or wrong type"

    if not re.fullmatch(email_regex, email):
        return "Wrong E-Mail."


def check_role(role: str) -> str | None:
    """ Check role """

    if not role or not isinstance(role, str):
        return "No role or wrong type"

    if role not in ["customer", "executor"]:
        return "Wrong role, select 'customer' or 'performer'"


def check_phone(phone: str) -> str | None:
    """ Check phone """

    if not phone or not isinstance(phone, str):
        return "No phone or wrong type"

    if not re.fullmatch(phone_regex, phone):
        return "Wrong phone."


def check_pk(pk: int) -> str | None:
    """ Check pk """
    if pk is None or not isinstance(pk, int):
        return "There isn't pk or wrong type"


def check_description(text: str) -> str | None:
    """Check description """

    if text is None or not isinstance(text, str):
        return "There isn't description or wrong type"

    text = text.split()

    if len(text) <= 5:
        return "Description must be more than 5 words"


def check_date(the_date: datetime, other_date=None) -> str | None:

    if the_date is None or not isinstance(the_date, datetime):
        return "There isn't date or wrong type"

    today = other_date or datetime.today()

    if the_date < today:
        return "You cannot create an order in the past"


def check_address(address: str) -> str | None:

    if address is None or not isinstance(address, str):
        return "There isn't address or wrong type"

    address = address.strip().split()

    if len(address) < 4:
        return "There is something wrong with your address"

    if not address[0].isdigit():
        return "The first element of the address can be your post office zip code"


def check_price(price: int) -> str | None:

    if price is None or not isinstance(price, int):
        return "There isn't price or wrong type"

    if price < 100:
        return "Do it yourself for that kind of money"

