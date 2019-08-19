import json
from typing import Any, Type

from .core import T
from .de import Deserializer, from_obj
from .se import Serializer, asdict, is_serializable


class JsonSerializer(Serializer):
    def serialize(self, obj: Any, **opts) -> str:
        return json.dumps(asdict(obj), **opts)


class JsonDeserializer(Deserializer):
    def deserialize(self, s, **opts):
        return json.loads(s, **opts)


def to_json(obj: Any, cls=JsonSerializer) -> str:
    return cls().serialize(obj)


def from_json(c: Type[T], s: str, de: Type[Deserializer] = JsonDeserializer, **opts) -> T:
    return from_obj(c, s, de, **opts)
