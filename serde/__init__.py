"""
.. include:: ../README.md
"""
from .core import init, astuple, asdict, SerdeError, typecheck  # noqa
from .se import serialize, is_serializable  # noqa
from .de import deserialize, is_deserializable, from_obj  # noqa

""" Version of pyserde. """
__version__ = '0.0.6'
