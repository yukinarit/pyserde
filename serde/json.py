import json
from typing import Type, Any, Dict, Tuple
from dataclasses import asdict

from .core import T, JsonValue
from .se import Serializer
from .de import Deserializer


class JsonSerializer(Serializer):
    def serialize(self, obj: Any) -> str:
        return json.dumps(asdict(obj))


class JsonDeserializer(Deserializer):
    def deserialize(self, s: str) -> Dict[str, JsonValue]:
        return json.loads(s)


def to_json(obj: Any, serializer=JsonSerializer) -> str:
    return obj.__serde_serialize__(serializer)


def from_json(c: Type[T], s: str,
              de: Type[Deserializer]=JsonDeserializer) -> T:
    # dct = de().deserialize(s)
    # return c.__serde_from_dict__(dct)
    return c.__serde_from_dict__(json.loads(s))


def astuple(v):
    """
    Convert decoded JSON `dict` to `tuple`.
    """
    if isinstance(v, dict):
        return tuple(astuple(v) for v in v.values())
    else:
        return v
