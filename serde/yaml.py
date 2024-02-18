"""
Serialize and Deserialize in YAML format. This module depends on
[pyyaml](https://pypi.org/project/PyYAML/) package.
"""
from typing import overload, Type, Optional, Any

import yaml

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_yaml", "to_yaml"]


class YamlSerializer(Serializer[str]):
    @classmethod
    def serialize(cls, obj: Any, **opts: Any) -> str:
        return yaml.safe_dump(obj, **opts)  # type: ignore


class YamlDeserializer(Deserializer[str]):
    @classmethod
    def deserialize(cls, data: str, **opts: Any) -> Any:
        return yaml.safe_load(data, **opts)


def to_yaml(
    obj: Any, cls: Optional[Any] = None, se: Type[Serializer[str]] = YamlSerializer, **opts: Any
) -> str:
    """
    Serialize the object into YAML.

    You can pass any serializable `obj`. If you supply keyword arguments other than `se`,
    they will be passed in `yaml.safe_dump` function.

    If you want to use the other yaml package, you can subclass `YamlSerializer` and implement
    your own logic.
    """
    return se.serialize(to_dict(obj, c=cls, reuse_instances=False), **opts)


@overload
def from_yaml(c: Type[T], s: str, de: Type[Deserializer[str]] = YamlDeserializer, **opts: Any) -> T:
    ...


# For Union, Optional etc.
@overload
def from_yaml(c: Any, s: str, de: Type[Deserializer[str]] = YamlDeserializer, **opts: Any) -> Any:
    ...


def from_yaml(c: Any, s: str, de: Type[Deserializer[str]] = YamlDeserializer, **opts: Any) -> Any:
    """
    `c` is a class obejct and `s` is YAML string. If you supply keyword arguments other than `de`,
    they will be passed in `yaml.safe_load` function.

    If you want to use the other yaml package, you can subclass `YamlDeserializer` and implement
    your own logic.
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
