"""
Serialize and Deserialize in TOML format. This module depends on [toml](https://pypi.org/project/toml/) package.
"""
from typing import Type

import toml

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_toml", "to_toml"]


class TomlSerializer(Serializer):
    @classmethod
    def serialize(cls, obj, **opts) -> str:
        return toml.dumps(obj, **opts)


class TomlDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        return toml.loads(s, **opts)


def to_toml(obj, se: Type[Serializer] = TomlSerializer, **opts) -> str:
    """
    Serialize the object into TOML.

    You can pass any serializable `obj`. If you supply keyword arguments other than `se`,
    they will be passed in `toml.dumps` function.

    If you want to use the other toml package, you can subclass `TomlSerializer` and implement your own logic.
    """
    return se.serialize(to_dict(obj, reuse_instances=False), **opts)


def from_toml(c: Type[T], s: str, de: Type[Deserializer] = TomlDeserializer, **opts) -> T:
    """
    Deserialize from TOML into the object.

    `c` is a class obejct and `s` is TOML string. If you supply keyword arguments other than `de`,
    they will be passed in `toml.loads` function.

    If you want to use the other toml package, you can subclass `TomlDeserializer` and implement your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
