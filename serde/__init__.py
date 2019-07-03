"""
.. include:: ../README.md
"""
from .core import SerdeError, init, logger, typecheck  # noqa
from .de import deserialize, from_obj, is_deserializable  # noqa
from .se import asdict, astuple, is_serializable, serialize  # noqa

""" Version of pyserde. """
__version__ = '0.0.7'
