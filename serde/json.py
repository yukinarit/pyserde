"""
Serialize and Deserialize in JSON format.
"""
import json
from typing import Any, Type

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict


class JsonSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, **opts) -> str:
        return json.dumps(obj, **opts)


class JsonDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        return json.loads(s, **opts)


def to_json(obj: Any, se: Serializer = JsonSerializer, **opts) -> str:
    return se.serialize(to_dict(obj, reuse_instances=False, convert_sets=True), **opts)


def from_json(c: Type[T], s: str, de: Deserializer = JsonDeserializer, **opts) -> T:
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
