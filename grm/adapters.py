"""
    GRM package
    adapters
"""


# global imports
from flask import jsonify


class BaseAdapter:

    _data = None

    def jsonify(self):
        jsonify(self._data)
