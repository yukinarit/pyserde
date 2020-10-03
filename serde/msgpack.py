"""
Serialize and Deserialize in MsgPack format.
"""
from typing import Any, Type

import msgpack

from .core import T, logger
from .de import Deserializer, from_dict, from_tuple
from .se import Serializer, asdict, astuple


class MsgPackSerializer(Serializer):
    @classmethod
    def serialize(cls, obj, named=True, use_bin_type=True, **opts) -> str:
        asf = asdict if named else astuple
        return msgpack.packb(asf(obj), use_bin_type=use_bin_type, **opts)


class MsgPackDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, raw=False, use_list=False, **opts):
        unp = msgpack.unpackb(s, raw=raw, use_list=use_list, **opts)
        logger.debug('unpack from msgpack: {unp}')
        return unp


def to_msgpack(obj: Any, se=MsgPackSerializer, **opts) -> bytes:
    return se.serialize(obj, **opts)


def from_msgpack(c: Type[T], s: str, de=MsgPackDeserializer, named=True, **opts) -> Type[T]:
    fromf = from_dict if named else from_tuple
    return fromf(c, de.deserialize(s, **opts))
