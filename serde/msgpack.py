"""
Serialize and Deserialize in MsgPack format. This module depends on
[msgpack](https://pypi.org/project/msgpack/) package.
"""
from typing import Any, Dict, Type

import msgpack

from .compat import T
from .core import SerdeError
from .de import Deserializer, from_dict, from_tuple
from .se import Serializer, to_dict, to_tuple

__all__ = ["from_msgpack", "to_msgpack"]


class MsgPackSerializer(Serializer):
    @classmethod
    def serialize(cls, obj, use_bin_type: bool = True, ext_type_code: int = None, **opts) -> bytes:
        if ext_type_code is not None:
            obj_bytes = msgpack.packb(obj, use_bin_type=use_bin_type, **opts)
            obj_or_ext = msgpack.ExtType(ext_type_code, obj_bytes)
        else:
            obj_or_ext = obj
        return msgpack.packb(obj_or_ext, use_bin_type=use_bin_type, **opts)


class MsgPackDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, raw: bool = False, use_list: bool = False, **opts):
        return msgpack.unpackb(s, raw=raw, use_list=use_list, **opts)


def to_msgpack(
    obj: Any, se: Type[Serializer] = MsgPackSerializer, named: bool = True, ext_dict: Dict[Type, int] = None, **opts
) -> bytes:
    """
    Serialize the object into MsgPack.

    You can pass any serializable `obj`. If `ext_dict` option is specified, `obj` is encoded as a `msgpack.ExtType`
    If you supply other keyword arguments, they will be passed in `msgpack.packb` function.

    If `named` is True, field names are preserved, namely the object is encoded as `dict` then serialized into MsgPack.
    If `named` is False, the object is encoded as `tuple` then serialized into MsgPack. `named=False` will produces
    compact binary.

    If you want to use the other msgpack package, you can subclass `MsgPackSerializer` and implement your own logic.
    """
    ext_type_code = None
    if ext_dict is not None:
        obj_type = type(obj)
        ext_type_code = ext_dict.get(obj_type)
        if ext_type_code is None:
            raise SerdeError(f"Could not find type code for {obj_type.__name__} in ext_dict")

    to_func = to_dict if named else to_tuple
    return se.serialize(to_func(obj, reuse_instances=False, convert_sets=True), ext_type_code=ext_type_code, **opts)


def from_msgpack(
    c: Type[T],
    s: str,
    de: Type[Deserializer] = MsgPackDeserializer,
    named: bool = True,
    ext_dict: Dict[int, Type] = None,
    **opts,
) -> Type[T]:
    """
    Deserialize from MsgPack into the object.

    `c` is a class obejct and `s` is MsgPack binary. If `ext_dict` option is specified, `c` is ignored and type is
    inferred from `msgpack.ExtType` If you supply other keyword arguments, they will be passed in
    `msgpack.unpackb` function.

    If you want to use the other msgpack package, you can subclass `MsgPackDeserializer` and implement your own logic.
    """
    if ext_dict is not None:
        ext = de.deserialize(s, **opts)
        ext_type = ext_dict.get(ext.code)
        if ext_type is None:
            raise SerdeError(f"Could not find type for code {ext.code} in ext_dict")
        return from_msgpack(ext_type, ext.data, de, named, **opts)
    else:
        from_func = from_dict if named else from_tuple
        return from_func(c, de.deserialize(s, **opts), reuse_instances=False)
