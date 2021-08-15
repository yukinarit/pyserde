"""
Serialize and Deserialize in JSON format.
"""
import json
from typing import Any, Type

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_json", "to_json"]


class JsonSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, **opts) -> str:
        return json.dumps(obj, **opts)


class JsonDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        return json.loads(s, **opts)


def to_json(obj: Any, se: Type[Serializer] = JsonSerializer, **opts) -> str:
    """
    Serialize the object into JSON.

    You can pass any serializable `obj`. If you supply other keyword arguments, they will be passed in `json.dumps`
    function.

    If you want to use the other json package, you can subclass `JsonSerializer` and implement your own logic.
    """
    return se.serialize(to_dict(obj, reuse_instances=False, convert_sets=True), **opts)


def from_json(c: Type[T], s: str, de: Type[Deserializer] = JsonDeserializer, **opts) -> T:
    """
    Deserialize from JSON into the object.

    `c` is a class obejct and `s` is JSON string.  If you supply other keyword arguments, they will be passed in
    `json.loads` function.

    If you want to use the other json package, you can subclass `JsonDeserializer` and implement your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
