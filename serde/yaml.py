"""
Serialize and Deserialize in YAML format.
"""
from typing import List, Type  # noqa

import yaml

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict


class YamlSerializer(Serializer):
    @classmethod
    def serialize(cls, obj, **opts) -> str:
        return yaml.safe_dump(obj, **opts)


class YamlDeserializer(Deserializer):
    @classmethod
    def deserialize(cls, s, **opts):
        return yaml.safe_load(s, **opts)


def to_yaml(obj, se: Serializer = YamlSerializer, **opts) -> str:
    """
    Take an object and return yaml string.

    >>> from dataclasses import dataclass
    >>> from serde import serialize
    >>>
    >>> @serialize
    ... @dataclass
    ... class Settings:
    ...     host: str
    ...     port: int
    ...     upstream: List[str]
    >>>
    >>> to_yaml(Settings(host='localhost', port=8080, upstream=['localhost:8081', 'localhost:8082']))
    'host: localhost\\nport: 8080\\nupstream:\\n- localhost:8081\\n- localhost:8082\\n'
    >>>
    """
    return se.serialize(to_dict(obj, reuse_instances=False), **opts)


def from_yaml(c: Type[T], s: str, de: Deserializer = YamlDeserializer, **opts) -> T:
    """
    Take yaml string and return deserialized object..

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Settings:
    ...     host: str
    ...     port: int
    ...     upstream: List[str]
    >>>
    >>> s = 'host: localhost\\nport: 8080\\nupstream:\\n- localhost:8081\\n- localhost:8082\\n'
    >>> from_yaml(Settings, s)
    Settings(host='localhost', port=8080, upstream=['localhost:8081', 'localhost:8082'])
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
