"""
Serialize and Deserialize in TOML format.
"""
from typing import Type

import toml

from .compat import T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict


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
    Take an object and return toml string.

    >>> from typing import List
    >>> from dataclasses import dataclass
    >>> from serde import serialize
    >>> from serde.toml import to_toml
    >>>
    >>> @serialize
    ... @dataclass
    ... class General:
    ...     host: str
    ...     port: int
    ...     upstream: List[str]
    >>>
    >>> @serialize
    ... @dataclass
    ... class Settings:
    ...     general: General
    >>>
    >>> to_toml(Settings(General(host='localhost', port=8080, upstream=['localhost:8081', 'localhost:8082'])))
    '[general]\\nhost = \"localhost\"\\nport = 8080\\nupstream = [ \"localhost:8081\", \"localhost:8082\",]\\n'
    >>>
    """
    return se.serialize(to_dict(obj, reuse_instances=False), **opts)


def from_toml(c: Type[T], s: str, de: Type[Deserializer] = TomlDeserializer, **opts) -> T:
    """
    Take toml string and return deserialized object.

    >>> from typing import List
    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>> from serde.toml import to_toml
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Settings:
    ...     host: str
    ...     port: int
    ...     upstream: List[str]
    >>>
    >>> s = 'host = \"localhost\"\\nport = 8080\\nupstream = [ \"localhost:8081\", \"localhost:8082\",]\\n'
    >>> from_toml(Settings, s)
    Settings(host='localhost', port=8080, upstream=['localhost:8081', 'localhost:8082'])
    >>>
    """
    return from_dict(c, de.deserialize(s, **opts), reuse_instances=False)
