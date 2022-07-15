"""
    App custom serialization
"""


# global imports
import datetime

from flask.json import JSONEncoder
from datetime import date

# flask json custom serialization


class CustomJSONEncoder(JSONEncoder):
    """ Custom flask JSON encoder, correct date format """
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.strftime("%d.%m.%Y")
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def to_date(the_date: str) -> datetime:
    """ Convert str to datetime object """
    return datetime.datetime.strptime(the_date, "%d.%m.%Y")



