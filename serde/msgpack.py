from dataclasses import asdict
from typing import Any, Type

import msgpack

from .core import T, logger
from .de import Deserializer, from_dict
from .se import Serializer


class MsgPackSerializer(Serializer):
    @classmethod
    def serialize(cls, obj: Any, **opts) -> str:
        return msgpack.packb(asdict(obj), use_bin_type=True, **opts)


class MsgPackDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        unp = msgpack.unpackb(s, raw=False, use_list=False, **opts)
        logger.debug('unpack from msgpack: {unp}')
        return unp


def to_msgpack(obj: Any, serializer=MsgPackSerializer, **opts) -> bytes:
    return obj.__serde_serialize__(serializer, **opts)


def from_msgpack(c: Type[T], s: str, de: Type[Deserializer] = MsgPackDeserializer, **opts) -> Type[T]:
    return from_dict(c, de.deserialize(s, **opts))
