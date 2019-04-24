from typing import Any, Tuple, Type

import msgpack
from dataclasses import astuple

from .core import T, logger
from .de import Deserializer, from_obj
from .se import Serializer


class MsgPackSerializer(Serializer):
    def serialize(self, obj: Any, **opts) -> str:
        return msgpack.packb(astuple(obj), **opts)


class MsgPackDeserializer(Deserializer):
    def deserialize(self, s, **opts):
        unp = msgpack.unpackb(s, raw=False, use_list=False, **opts)
        logger.debug('unpack from msgpack: {unp}')
        return unp


def to_msgpack(obj: Any, serializer=MsgPackSerializer, **opts) -> bytes:
    return obj.__serde_serialize__(serializer, **opts)


def from_msgpack(c: Type[T], s: str, de: Type[Deserializer] = MsgPackDeserializer, **opts) -> Type[T]:
    return from_obj(c, s, de)
