"""
.. include:: ../README.md

"""
from .compat import SerdeError, SerdeSkip  # noqa
from .core import init, logger  # noqa
from .de import default_deserialize, deserialize, from_dict, from_tuple, is_deserializable  # noqa
from .se import asdict, astuple, default_serialize, is_serializable, serialize, to_dict, to_tuple  # noqa

""" Version of pyserde. """
__version__ = '0.3.2'

__all__ = [
    'serialize',
    'deserialize',
    'default_serialize',
    'default_deserialize',
    'is_serializable',
    'is_deserializable',
    'from_dict',
    'from_tuple',
    'to_dict',
    'to_tuple',
    'SerdeError',
    'SerdeSkip',
    'asdict',
    'astuple',
]
