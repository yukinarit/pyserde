"""
Serialize and Deserialize in JSON format.
"""
from typing import Any, AnyStr, overload, Optional, Union

from typing_extensions import Type

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict
from .numpy import encode_numpy

try:  # pragma: no cover
    import orjson

    def json_dumps(obj: Any, **opts: Any) -> str:
        if "option" not in opts:
            opts["option"] = orjson.OPT_SERIALIZE_NUMPY
        return orjson.dumps(obj, **opts).decode()  # type: ignore

    def json_loads(s: Union[str, bytes], **opts: Any) -> Any:
        return orjson.loads(s, **opts)

except ImportError:
    import json

    def json_dumps(obj: Any, **opts: Any) -> str:
        if "default" not in opts:
            opts["default"] = encode_numpy
        # compact output
        ensure_ascii = opts.pop("ensure_ascii", False)
        separators = opts.pop("separators", (",", ":"))
        return json.dumps(obj, ensure_ascii=ensure_ascii, separators=separators, **opts)

    def json_loads(s: Union[str, bytes], **opts: Any) -> Any:
        return json.loads(s, **opts)


__all__ = ["from_json", "to_json"]


class JsonSerializer(Serializer[str]):
    @classmethod
    def serialize(cls, obj: Any, **opts: Any) -> str:
        return json_dumps(obj, **opts)


class JsonDeserializer(Deserializer[AnyStr]):
    @classmethod
    def deserialize(cls, data: AnyStr, **opts: Any) -> Any:
        return json_loads(data, **opts)


def to_json(
    obj: Any, cls: Optional[Any] = None, se: Type[Serializer[str]] = JsonSerializer, **opts: Any
) -> str:
    """
    Serialize the object into JSON str. [orjson](https://github.com/ijl/orjson)
    will be used if installed.

    You can pass any serializable `obj`. If you supply other keyword arguments,
    they will be passed in `dumps` function.
    By default, numpy objects are serialized, this behaviour can be customized with the `option`
    argument with [orjson](https://github.com/ijl/orjson#numpy), or the `default` argument with
    Python standard json library.

    If you want to use another json package, you can subclass `JsonSerializer` and implement
    your own logic.
    """
    return se.serialize(to_dict(obj, c=cls, reuse_instances=False, convert_sets=True), **opts)


@overload
def from_json(
    c: Type[T], s: AnyStr, de: Type[Deserializer[AnyStr]] = JsonDeserializer, **opts: Any
) -> T:
    ...


# For Union, Optional etc.
@overload
def from_json(
    c: Any, s: AnyStr, de: Type[Deserializer[AnyStr]] = JsonDeserializer, **opts: Any
) -> Any:
    ...


def from_json(
    c: Any, s: AnyStr, de: Type[Deserializer[AnyStr]] = JsonDeserializer, **opts: Any
) -> Any:
    """
    Deserialize from JSON into the object. [orjson](https://github.com/ijl/orjson) will be used
    if installed.

    `c` is a class obejct and `s` is JSON bytes or str. If you supply other keyword arguments,
    they will be passed in `loads` function.

    If you want to use another json package, you can subclass `JsonDeserializer` and implement
    your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
