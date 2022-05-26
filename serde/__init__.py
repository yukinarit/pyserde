"""
`pyserde` is a yet another serialization library on top of
[dataclasses](https://docs.python.org/3/library/dataclasses.html),
inspired by [serde-rs](https://github.com/serde-rs/serde).

## Overview

Declare a class with `@dataclasses.dataclass` and pyserde's `@serde` decorators.

>>> from serde import serde
>>>
>>> @serde
... @dataclass
... class Foo:
...     i: int
...     s: str
...     f: float
...     b: bool

You can serialize `Foo` object into JSON.

>>> from serde.json import to_json
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'

You can deserialize JSON into `Foo` object.
>>> from serde.json import from_json
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)

## Modules

The following modules provide the core functionalities of `pyserde`.
* `serde.se`: All about serialization.
* `serde.de`: All about deserialization.
* `serde.core`: Core module used by `serde.se` and `serde.de`.
* `serde.compat`: Compatibility layer which handles mostly typing.

The following modules (de)serialize functions.
* `serde.json`: Serialize and Deserialize in JSON.
* `serde.msgpack`: Serialize and Deserialize in MsgPack.
* `serde.yaml`: Serialize and Deserialize in YAML.
* `serde.toml`: Serialize and Deserialize in TOML.

Other modules
* `serde.inspect`: Prints generated code by pyserde.
"""

from dataclasses import dataclass

from .compat import SerdeError, SerdeSkip
from .core import (
    AdjacentTagging,
    ExternalTagging,
    InternalTagging,
    Untagged,
    field,
    init,
    logger,
    should_impl_dataclass,
)
from .de import default_deserializer, deserialize, from_dict, from_tuple, is_deserializable
from .se import asdict, astuple, default_serializer, is_serializable, serialize, to_dict, to_tuple

__all__ = (
    "SerdeError",
    "SerdeSkip",
    "AdjacentTagging",
    "ExternalTagging",
    "InternalTagging",
    "Untagged",
    "field",
    "default_deserializer",
    "deserialize",
    "from_dict",
    "from_tuple",
    "is_deserializable",
    "asdict",
    "astuple",
    "default_serializer",
    "is_serializable",
    "serialize",
    "to_dict",
    "to_tuple",
    "serde",
    "compat",
    "core",
    "de",
    "inspect",
    "json",
    "msgpack",
    "numpy",
    "se",
    "toml",
    "yaml",
)


def serde(_cls=None, **kwargs):
    """
    serde decorator. Keyword arguments are passed in `serialize` and `deserialize`.
    """

    def wrap(cls):
        if should_impl_dataclass(cls):
            dataclass(cls)
        serialize(cls, **kwargs)
        deserialize(cls, **kwargs)
        return cls

    if _cls is None:
        return wrap  # type: ignore

    return wrap(_cls)
