"""
Serialize and Deserialize in Pickle format.
"""
import pickle
from typing import overload, Type, Any, Optional

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_pickle", "to_pickle"]


class PickleSerializer(Serializer[bytes]):
    @classmethod
    def serialize(cls, obj: Any, **opts: Any) -> bytes:
        return pickle.dumps(obj, **opts)


class PickleDeserializer(Deserializer[bytes]):
    @classmethod
    def deserialize(cls, data: bytes, **opts: Any) -> Any:
        return pickle.loads(data, **opts)


def to_pickle(
    obj: Any, cls: Optional[Any] = None, se: Type[Serializer[bytes]] = PickleSerializer, **opts: Any
) -> bytes:
    return se.serialize(to_dict(obj, c=cls, reuse_instances=False), **opts)


@overload
def from_pickle(
    c: Type[T], data: bytes, de: Type[Deserializer[bytes]] = PickleDeserializer, **opts: Any
) -> T:
    ...


@overload
def from_pickle(
    c: Any, data: bytes, de: Type[Deserializer[bytes]] = PickleDeserializer, **opts: Any
) -> Any:
    ...


# For Union, Optional etc.
def from_pickle(
    c: Any, data: bytes, de: Type[Deserializer[bytes]] = PickleDeserializer, **opts: Any
) -> Any:
    return from_dict(c, de.deserialize(data, **opts), reuse_instances=False)
