"""
.. include:: ../README.md
"""
from .core import SerdeError, asdict, astuple, init, logger, typecheck  # noqa
from .de import deserialize, from_obj, is_deserializable  # noqa
from .se import is_serializable, serialize  # noqa

""" Version of pyserde. """
__version__ = '0.0.7'
