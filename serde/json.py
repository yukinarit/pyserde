import json
from typing import Any, Type

from .core import T
from .de import Deserializer, from_dict
from .se import Serializer, asdict


class JsonSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, named=True, **opts) -> str:
        return json.dumps(asdict(obj), **opts)


class JsonDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, named=True, **opts):
        return json.loads(s, **opts)


def to_json(obj: Any, cls: Type[JsonSerializer] = JsonSerializer, **opts) -> str:
    return cls.serialize(obj)


def from_json(c: Type[T], s: str, de: Type[Deserializer] = JsonDeserializer, **opts) -> T:
    return from_dict(c, de.deserialize(s, **opts))
