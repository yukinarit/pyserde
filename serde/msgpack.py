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
        if "ext_dict" in opts:
            opts.pop("ext_dict")
            obj_bytes = msgpack.packb(asf(obj), use_bin_type=use_bin_type, **opts)
            maybe_ext = msgpack.ExtType(int(obj._type), obj_bytes)
        else:
            maybe_ext = asf(obj)
        return msgpack.packb(maybe_ext, use_bin_type=use_bin_type, **opts)


class MsgPackDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, raw=False, use_list=False, **opts):
        unp = msgpack.unpackb(s, raw=raw, use_list=use_list, **opts)
        logger.debug('unpack from msgpack: {unp}')
        return unp


def to_msgpack(obj: Any, se=MsgPackSerializer, **opts) -> bytes:
    """
    If `ext_dict` option is specified, `obj` is encoded as a `msgpack.ExtType`
    """
    return se.serialize(obj, **opts)


def from_msgpack(c: Type[T], s: str, de=MsgPackDeserializer, named=True, **opts) -> Type[T]:
    """
    If `ext_dict` option is specified, `c` is ignored and type is inferred from `msgpack.ExtType`
    """
    if "ext_dict" in opts:
        ext_dict = opts.pop("ext_dict")
        ext = de.deserialize(s, **opts)
        c = ext_dict[ext.code]
        return from_msgpack(c, ext.data, de, named, **opts)
    else:
        fromf = from_dict if named else from_tuple
        return fromf(c, de.deserialize(s, **opts))
