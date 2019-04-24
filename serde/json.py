import json
from typing import Any, Type

from dataclasses import asdict

from .core import T
from .de import Deserializer, from_obj
from .se import Serializer, is_serializable


class JsonSerializer(Serializer):
    def serialize(self, obj: Any, **opts) -> str:
        return json.dumps(asdict(obj), **opts)


class JsonDeserializer(Deserializer):
    def deserialize(self, s, **opts):
        return json.loads(s, **opts)


def to_json(obj: Any, serializer=JsonSerializer) -> str:
    if is_serializable(obj):
        return obj.__serde_serialize__(serializer)
    else:
        return json.dumps(obj)


def from_json(c: Type[T], s: str, de: Type[Deserializer] = JsonDeserializer) -> T:
    return from_obj(c, s, de)
