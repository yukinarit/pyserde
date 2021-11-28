"""
`pyserde` is a yet another serialization library on top of
[dataclasses](https://docs.python.org/3/library/dataclasses.html).

## Overview

Declare a class with pyserde's `@serialize` and `@deserialize` decorators.

>>> from serde import serde
>>>
>>> @serde
... class Foo:
...     i: int
...     s: str
...     f: float
...     b: bool

You can serialize `Foo` object into JSON.

>>> from serde.json import to_json
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i": 10, "s": "foo", "f": 100.0, "b": true}'

You can deserialize JSON into `Foo` object.
>>> from serde.json import from_json
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)

## Modules

The following modules provide the core functionalities of `pyserde`.
* `serde.se`: All about serialization.
* `serde.de`: All about deserialization.
* `serde.core`: Core module used by `serde.se` and `serde.de`.
* `serde.compat`: Provides compatibility layer which handles typing.

The following modules provides functionalities for supported data formats.
* `serde.json`: Serialize and Deserialize in JSON.
* `serde.msgpack`: Serialize and Deserialize in MsgPack.
* `serde.yaml`: Serialize and Deserialize in YAML.
* `serde.toml`: Serialize and Deserialize in TOML.
"""

import dataclasses
import sys

from .compat import SerdeError, SerdeSkip  # noqa
from .core import field, init, logger  # noqa
from .de import default_deserializer, deserialize, from_dict, from_tuple, is_deserializable  # noqa
from .se import asdict, astuple, default_serializer, is_serializable, serialize, to_dict, to_tuple  # noqa

if sys.version_info[:2] == (3, 6):
    import backports.datetime_fromisoformat

    backports.datetime_fromisoformat.MonkeyPatch.patch_fromisoformat()


def serde(_cls=None, **kwargs):
    def wrap(cls):
        dataclasses.dataclass(cls)
        serialize(cls, **kwargs)
        deserialize(cls, **kwargs)
        return cls

    if _cls is None:
        return wrap  # type: ignore

    return wrap(_cls)
