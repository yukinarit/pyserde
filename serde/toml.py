import toml

from typing import Any, Type, List  # noqa
from dataclasses import asdict

from .core import T
from .de import Deserializer, from_obj
from .se import Serializer, is_serializable


class TomlSerializer(Serializer):
    def serialize(self, obj, **opts) -> str:
        return toml.dumps(asdict(obj), **opts)


class TomlDeserializer(Deserializer):
    def deserialize(self, s, **opts):
        return toml.loads(s, **opts)


def to_toml(obj: Any, serializer=TomlSerializer) -> str:
    """
    Take an object and return toml string.

    >>> from dataclasses import dataclass
    >>> from serde import serialize
    >>> from serde.toml import to_toml
    >>>
    >>> @serialize
    ... @dataclass
    ... class Settings:
    ...     general: 'General'
    >>>
    >>> @serialize
    ... @dataclass
    ... class General:
    ...     host: str
    ...     port: int
    ...     upstream: List[str]
    >>>
    >>> to_toml(Settings(General(host='localhost', port=8080, upstream=['localhost:8081', 'localhost:8082'])))
    '[general]\\nhost = \"localhost\"\\nport = 8080\\nupstream = [ \"localhost:8081\", \"localhost:8082\",]\\n'
    >>>
    """
    if is_serializable(obj):
        return obj.__serde_serialize__(serializer)
    else:
        return toml.dumps(obj)


def from_toml(c: Type[T], s: str, de: Type[Deserializer] = TomlDeserializer) -> T:
    """
    Take toml string and return deserialized object..

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
    return from_obj(c, s, de)
