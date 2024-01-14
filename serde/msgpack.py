"""
Serialize and Deserialize in MsgPack format. This module depends on
[msgpack](https://pypi.org/project/msgpack/) package.
"""
from typing import Any, Type, Optional, overload
from beartype.typing import Dict

import msgpack

from .compat import T
from .compat import SerdeError
from .de import Deserializer, from_dict, from_tuple
from .numpy import encode_numpy
from .se import Serializer, to_dict, to_tuple

__all__ = ["from_msgpack", "to_msgpack"]


class MsgPackSerializer(Serializer[bytes]):
    @classmethod
    def serialize(
        cls, obj: Any, use_bin_type: bool = True, ext_type_code: Optional[int] = None, **opts: Any
    ) -> bytes:
        if "default" not in opts:
            opts["default"] = encode_numpy
        if ext_type_code is not None:
            obj_bytes = msgpack.packb(obj, use_bin_type=use_bin_type, **opts)
            obj_or_ext = msgpack.ExtType(ext_type_code, obj_bytes)
        else:
            obj_or_ext = obj
        return msgpack.packb(obj_or_ext, use_bin_type=use_bin_type, **opts)


class MsgPackDeserializer(Deserializer[bytes]):
    @classmethod
    def deserialize(
        cls, data: bytes, raw: bool = False, use_list: bool = False, **opts: Any
    ) -> Any:
        return msgpack.unpackb(data, raw=raw, use_list=use_list, **opts)


def to_msgpack(
    obj: Any,
    cls: Optional[Any] = None,
    se: Type[Serializer[bytes]] = MsgPackSerializer,
    named: bool = True,
    ext_dict: Optional[Dict[Type[Any], int]] = None,
    **opts: Any,
) -> bytes:
    """
    Serialize the object into MsgPack.

    You can pass any serializable `obj`. If `ext_dict` option is specified, `obj` is encoded
    as a `msgpack.ExtType` If you supply other keyword arguments, they will be passed in
    `msgpack.packb` function.

    If `named` is True, field names are preserved, namely the object is encoded as `dict` then
    serialized into MsgPack.  If `named` is False, the object is encoded as `tuple` then serialized
    into MsgPack. `named=False` will produces compact binary.

    If you want to use the other msgpack package, you can subclass `MsgPackSerializer` and
    implement your own logic.
    """
    ext_type_code = None
    if ext_dict is not None:
        obj_type = type(obj)
        ext_type_code = ext_dict.get(obj_type)
        if ext_type_code is None:
            raise SerdeError(f"Could not find type code for {obj_type.__name__} in ext_dict")

    kwargs: Any = {"c": cls, "reuse_instances": False, "convert_sets": True}
    dict_or_tuple = to_dict(obj, **kwargs) if named else to_tuple(obj, **kwargs)
    return se.serialize(
        dict_or_tuple,
        ext_type_code=ext_type_code,
        **opts,
    )


@overload
def from_msgpack(
    c: Type[T],
    s: bytes,
    de: Type[Deserializer[bytes]] = MsgPackDeserializer,
    named: bool = True,
    ext_dict: Optional[Dict[int, Type[Any]]] = None,
    **opts: Any,
) -> T:
    ...


@overload
def from_msgpack(
    c: Any,
    s: bytes,
    de: Type[Deserializer[bytes]] = MsgPackDeserializer,
    named: bool = True,
    ext_dict: Optional[Dict[int, Type[Any]]] = None,
    **opts: Any,
) -> Any:
    ...


def from_msgpack(
    c: Any,
    s: bytes,
    de: Type[Deserializer[bytes]] = MsgPackDeserializer,
    named: bool = True,
    ext_dict: Optional[Dict[int, Type[Any]]] = None,
    **opts: Any,
) -> Any:
    """
    Deserialize from MsgPack into the object.

    `c` is a class obejct and `s` is MsgPack binary. If `ext_dict` option is specified,
    `c` is ignored and type is inferred from `msgpack.ExtType` If you supply other keyword
    arguments, they will be passed in `msgpack.unpackb` function.

    If you want to use the other msgpack package, you can subclass `MsgPackDeserializer`
    and implement your own logic.
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
