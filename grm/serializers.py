"""
    GRM package
    serializers
"""

# global imports
from sqlalchemy import inspect


def to_dict_from_alchemy_model(model):
    if model is None:
        return None
    return {attr.key: getattr(model, attr.key) for attr in inspect(model).mapper.column_attrs}
