"""
Serialize and Deserialize in YAML format. This module depends on [pyyaml](https://pypi.org/project/PyYAML/) package.
"""
from typing import Type

import yaml

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_yaml", "to_yaml"]


class YamlSerializer(Serializer):
    @classmethod
    def serialize(cls, obj, **opts) -> str:
        return yaml.safe_dump(obj, **opts)


class YamlDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        return yaml.safe_load(s, **opts)


def to_yaml(obj, se: Type[Serializer] = YamlSerializer, **opts) -> str:
    """
    Serialize the object into YAML.

    You can pass any serializable `obj`. If you supply keyword arguments other than `se`,
    they will be passed in `yaml.safe_dump` function.

    If you want to use the other yaml package, you can subclass `YamlSerializer` and implement your own logic.
    """
    return se.serialize(to_dict(obj, reuse_instances=False), **opts)


def from_yaml(c: Type[T], s: str, de: Type[Deserializer] = YamlDeserializer, **opts) -> T:
    """
    `c` is a class obejct and `s` is YAML string. If you supply keyword arguments other than `de`,
    they will be passed in `yaml.safe_load` function.

    If you want to use the other yaml package, you can subclass `YamlDeserializer` and implement your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
