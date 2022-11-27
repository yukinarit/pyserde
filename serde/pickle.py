"""
Serialize and Deserialize in Pickle format.
"""
import pickle
from typing import Type

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_pickle", "to_pickle"]


class PickleSerializer(Serializer):
    @classmethod
    def serialize(cls, obj, **opts) -> bytes:
        return pickle.dumps(obj, **opts)


class PickleDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, data, **opts):
        return pickle.loads(data, **opts)


def to_pickle(obj, se: Type[Serializer] = PickleSerializer, **opts) -> str:
    return se.serialize(to_dict(obj, reuse_instances=False), **opts)


def from_pickle(c: Type[T], s: str, de: Type[Deserializer] = PickleDeserializer, **opts) -> T:
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
