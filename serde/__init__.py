"""
pyserde is a yet another serialization library on top of
[dataclasses](https://docs.python.org/3/library/dataclasses.html).

Declare a class with pyserde's `@serialize` and `@deserialize` decorators.

>>> from dataclasses import dataclass
>>> from serde import serialize, deserialize
>>>
>>> @deserialize
... @serialize
... @dataclass
... class Foo:
...     i: int
...     s: str
...     f: float
...     b: bool

You can serialize `Foo` object into JSON.

>>> from serde.json import to_json
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i": 10, "s": "foo", "f": 100.0, "b": true}'

You can deserialize JSON into `Foo`.
>>> from serde.json import from_json
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)

The following modules provide the core functionalities of `pyserde`.
* `serde.se`: It's all about serialization.
* `serde.de`: It's all about deserialization.
* `serde.core`: Core module used by `serde.se` and `serde.de`.
* `serde.compat`: Provides compatibility layer handling typing.

The following modules provides data format supports.
* `serde.json`: Serialize and Deserialize in JSON.
* `serde.msgpack`: Serialize and Deserialize in MsgPack.
* `serde.yaml`: Serialize and Deserialize in YAML.
* `serde.toml`: Serialize and Deserialize in TOML.
"""

from .compat import SerdeError, SerdeSkip  # noqa
from .core import init, logger  # noqa
from .de import default_deserializer, deserialize, from_dict, from_tuple, is_deserializable  # noqa
from .se import asdict, astuple, default_serializer, is_serializable, serialize, to_dict, to_tuple  # noqa
