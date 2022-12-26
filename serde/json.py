"""
Serialize and Deserialize in JSON format.
"""
from typing import Any, Union

from typing_extensions import Type

from .compat import T
from .de import Deserializer, from_dict
from .numpy import encode_numpy
from .se import Serializer, to_dict

try:  # pragma: no cover
    import orjson

    def json_dumps(obj, **opts) -> str:
        if "option" not in opts:
            opts["option"] = orjson.OPT_SERIALIZE_NUMPY
        return orjson.dumps(obj, **opts).decode()

    def json_loads(s, **opts) -> Any:
        return orjson.loads(s, **opts)

except ImportError:
    import json

    def json_dumps(obj, **opts):
        if "default" not in opts:
            opts["default"] = encode_numpy
        # compact output
        ensure_ascii = opts.pop("ensure_ascii", False)
        separators = opts.pop("separators", (",", ":"))
        return json.dumps(obj, ensure_ascii=ensure_ascii, separators=separators, **opts)

    def json_loads(s, **opts):
        return json.loads(s, **opts)


__all__ = ["from_json", "to_json"]


class JsonSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, **opts) -> str:
        return json_dumps(obj, **opts)


class JsonDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s: Union[bytes, str], **opts):
        return json_loads(s, **opts)


def to_json(obj: Any, se: Type[Serializer] = JsonSerializer, **opts) -> str:
    """
    Serialize the object into JSON str. [orjson](https://github.com/ijl/orjson) will be used if installed.

    You can pass any serializable `obj`. If you supply other keyword arguments, they will be passed in `dumps`
    function.
    By default, numpy objects are serialized, this behaviour can be customized with the `option` argument with [orjson](https://github.com/ijl/orjson#numpy),
    or the `default` argument with Python standard json library.

    If you want to use another json package, you can subclass `JsonSerializer` and implement your own logic.
    """
    return se.serialize(to_dict(obj, reuse_instances=False, convert_sets=True), **opts)


def from_json(c: Type[T], s: Union[str, bytes], de: Type[Deserializer] = JsonDeserializer, **opts) -> T:
    """
    Deserialize from JSON into the object. [orjson](https://github.com/ijl/orjson) will be used if installed.

    `c` is a class obejct and `s` is JSON bytes or str. If you supply other keyword arguments, they will be passed in
    `loads` function.

    If you want to use another json package, you can subclass `JsonDeserializer` and implement your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
