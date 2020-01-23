"""
.. include:: ../README.md
"""
from .core import SerdeError, init, logger, typecheck  # noqa
from .de import deserialize, from_dict, from_obj, from_tuple, is_deserializable  # noqa
from .se import asdict, astuple, is_serializable, serialize  # noqa

""" Version of pyserde. """
__version__ = '0.0.12'
