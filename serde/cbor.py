"""
Serialize and Deserialize in CBOR format. This module depends on
[cbor2](https://pypi.org/project/cbor2/) package.
"""

from typing import Any, Optional, overload

import cbor2


from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict


__all__ = ["from_cbor", "to_cbor"]


class CborSerializer(Serializer[bytes]):
    @classmethod
    def serialize(cls, obj: Any, **opts: Any) -> bytes:
        return cbor2.dumps(obj, **opts)


class CborDeserializer(Deserializer[bytes]):
    @classmethod
    def deserialize(cls, data: bytes, **opts: Any) -> Any:
        return cbor2.loads(data, **opts)


def to_cbor(
    obj: Any,
    cls: Optional[Any] = None,
    se: type[Serializer[bytes]] = CborSerializer,
    reuse_instances: bool = False,
    convert_sets: bool = True,
    **opts: Any,
) -> bytes:
    """
    Serialize the object into CBOR.

    You can pass any serializable `obj`. If you supply other keyword arguments,
    they will be passed in `dumps` function.
    """
    return se.serialize(
        to_dict(
            obj,
            c=cls,
            reuse_instances=reuse_instances,
            convert_sets=convert_sets,
        ),
        **opts,
    )


@overload
def from_cbor(
    c: type[T], s: bytes, de: type[Deserializer[bytes]] = CborDeserializer, **opts: Any
) -> T: ...


# For Union, Optional etc.
@overload
def from_cbor(
    c: Any, s: bytes, de: type[Deserializer[bytes]] = CborDeserializer, **opts: Any
) -> Any: ...


def from_cbor(
    c: Any, s: bytes, de: type[Deserializer[bytes]] = CborDeserializer, **opts: Any
) -> Any:
    """
    Deserialize from CBOR into the object.

    `c` is a class object and `s` is bytes. If you supply other keyword arguments,
    they will be passed in `loads` function.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
