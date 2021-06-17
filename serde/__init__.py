"""
.. include:: ../README.md

"""
from .compat import SerdeError, SerdeSkip  # noqa
from .core import init, logger  # noqa
from .de import default_deserializer, deserialize, from_dict, from_tuple, is_deserializable  # noqa
from .se import asdict, astuple, default_serializer, is_serializable, serialize, to_dict, to_tuple  # noqa

""" Version of pyserde. """
__version__ = '0.4.0'

__all__ = [
    'serialize',
    'deserialize',
    'default_serializer',
    'default_deserializer',
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
