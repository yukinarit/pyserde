"""
Serialize and Deserialize in JSON format.
"""
import json
# import orjson
from typing import Any, Type

from .core import T
from .de import Deserializer, from_dict
from .se import Serializer, asdict

try:
    import orjson as _default_json_lib
except ImportError:
    import json as _default_json_lib


class JsonSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, jsonlib=None, named=True, **opts) -> str:
        _jsonlib = jsonlib or _default_json_lib
        return _jsonlib.dumps(asdict(obj), **opts)


class JsonDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, jsonlib=None, named=True, **opts):
        _jsonlib = jsonlib or _default_json_lib
        return _jsonlib.loads(s, **opts)


def to_json(obj: Any, se=JsonSerializer, **opts) -> str:
    return se.serialize(obj, **opts)


def from_json(c: Type[T], s: str, de=JsonDeserializer, **opts) -> T:
    return from_dict(c, de.deserialize(s, **opts))
