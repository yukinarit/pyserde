"""
Serialize and Deserialize in JSON format using orjson.
"""
from typing import Any, Type, Union

import orjson
from orjson import (
    OPT_APPEND_NEWLINE,
    OPT_INDENT_2,
    OPT_NAIVE_UTC,
    OPT_NON_STR_KEYS,
    OPT_OMIT_MICROSECONDS,
    OPT_PASSTHROUGH_DATACLASS,
    OPT_PASSTHROUGH_DATETIME,
    OPT_PASSTHROUGH_SUBCLASS,
    OPT_SERIALIZE_NUMPY,
    OPT_SORT_KEYS,
    OPT_STRICT_INTEGER,
    OPT_UTC_Z,
)

from .compat import T
from .core import StrSerializableTypes
from .de import Deserializer, from_dict
from .numpy import HAVE_NUMPY
from .se import Serializer, to_dict

__all__ = [
    "from_json",
    "to_json",
    "OPT_APPEND_NEWLINE",
    "OPT_INDENT_2",
    "OPT_NAIVE_UTC",
    "OPT_NON_STR_KEYS",
    "OPT_OMIT_MICROSECONDS",
    "OPT_PASSTHROUGH_DATACLASS",
    "OPT_PASSTHROUGH_DATETIME",
    "OPT_PASSTHROUGH_SUBCLASS",
    "OPT_SERIALIZE_NUMPY",
    "OPT_SORT_KEYS",
    "OPT_STRICT_INTEGER",
    "OPT_UTC_Z",
]


class OrjsonSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, **opts) -> bytes:
        return orjson.dumps(obj, **opts)


class OrjsonDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        return orjson.loads(s, **opts)


def default(obj: Any):
    if isinstance(obj, StrSerializableTypes):
        return str(obj)
    if isinstance(obj, set):
        return list(obj)

    raise TypeError(f"Type is not JSON serializable: {type(obj)}")


def to_json(obj: Any, se: Type[Serializer] = OrjsonSerializer, direct: bool = True, **opts) -> bytes:
    """
    Serialize the object into JSON.

    You can pass any serializable `obj`. If you supply other keyword arguments, they will be passed to the
    `json.dumps` function.

    By default, `direct=False` means that dataclass objects will first be converted to a dictionary before
    passing them to orjson.

    Passing `direct=True` passes dataclass objects directly to orjson for serialization.  In almost all cases,
    this will be faster, but will

    In most cases, `direct=False` will be slower, but may be necessary in rare situations.
    """
    if HAVE_NUMPY:
        opts["option"] = opts.get("option", 0) | OPT_SERIALIZE_NUMPY

    if direct:
        if "default" not in opts:
            opts["default"] = default
        return se.serialize(obj, **opts)

    return se.serialize(to_dict(obj, reuse_instances=False, convert_sets=True, convert_numpy=False), **opts)


def from_json(
    c: Type[T], s: Union[str, bytes, bytearray, memoryview], de: Type[Deserializer] = OrjsonDeserializer, **opts
) -> T:
    """
    Deserialize from JSON into the object.

    `c` is a class object and `s` is JSON string.  If you supply other keyword arguments, they will be passed to
    the `json.loads` function.

    If you want to use another json package, you can subclass `JsonDeserializer` and implement your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)  # type: ignore
