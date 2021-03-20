"""
.. include:: ../README.md

"""
from .core import SerdeError, init, logger  # noqa
from .de import deserialize, from_dict, from_tuple, is_deserializable  # noqa
from .se import asdict, astuple, is_serializable, serialize, to_dict, to_tuple  # noqa

""" Version of pyserde. """
__version__ = '0.3.1'

__all__ = [
    'serialize',
    'deserialize',
    'is_serializable',
    'is_deserializable',
    'from_dict',
    'from_tuple',
    'to_dict',
    'to_tuple',
    'SerdeError',
    'asdict',
    'astuple',
]
