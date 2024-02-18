"""
Serialize and Deserialize in TOML format. This module depends on
[tomli](https://github.com/hukkin/tomli) (for python<=3.10) and
[tomli-w](https://github.com/hukkin/tomli-w) packages.
"""
import sys
from typing import Type, overload, Optional, Any

import tomli_w

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_toml", "to_toml"]


if sys.version_info[:2] >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class TomlSerializer(Serializer[str]):
    @classmethod
    def serialize(cls, obj: Any, **opts: Any) -> str:
        return tomli_w.dumps(obj, **opts)


class TomlDeserializer(Deserializer[str]):
    @classmethod
    def deserialize(cls, data: str, **opts: Any) -> Any:
        return tomllib.loads(data, **opts)


def to_toml(
    obj: Any, cls: Optional[Any] = None, se: Type[Serializer[str]] = TomlSerializer, **opts: Any
) -> str:
    """
    Serialize the object into TOML.

    You can pass any serializable `obj`. If you supply keyword arguments other than `se`,
    they will be passed in `toml_w.dumps` function.

    If you want to use the other toml package, you can subclass `TomlSerializer` and implement
    your own logic.
    """
    return se.serialize(to_dict(obj, c=cls, reuse_instances=False), **opts)


@overload
def from_toml(c: Type[T], s: str, de: Type[Deserializer[str]] = TomlDeserializer, **opts: Any) -> T:
    ...


# For Union, Optional etc.
@overload
def from_toml(c: Any, s: str, de: Type[Deserializer[str]] = TomlDeserializer, **opts: Any) -> Any:
    ...


def from_toml(c: Any, s: str, de: Type[Deserializer[str]] = TomlDeserializer, **opts: Any) -> Any:
    """
    Deserialize from TOML into the object.

    `c` is a class obejct and `s` is TOML string. If you supply keyword arguments other than `de`,
    they will be passed in `toml.loads` function.

    If you want to use the other toml package, you can subclass `TomlDeserializer` and implement
    your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
