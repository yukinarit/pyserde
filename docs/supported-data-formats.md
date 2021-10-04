# Supported data formats

Currently `JSON`, `Yaml`, `Toml` and `MsgPack` are supported.

```python
from serde import serialize, deserialize
from dataclasses import dataclass

@deserialize
@serialize
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

## JSON

Call `to_json` to serialize `Foo` object into JSON string and `from_json` to deserialize JSON string into `Foo` object. For more information, please visit [serde.json](https://yukinarit.github.io/pyserde/api/serde/json.html) module.

```python
>>> from serde.json import to_json, from_json

>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
{"i": 10, "s": "foo", "f": 100.0, "b": true}

>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Yaml

Call `to_yaml` to serialize `Foo` object into Yaml string and `from_yaml` to deserialize Yaml string into `Foo` object. For more information, please visit [serde.yaml](https://yukinarit.github.io/pyserde/api/serde/yaml.html) module.

```python
>>> from serde.yaml import from_yaml, to_yaml

>>> to_yaml(Foo(i=10, s='foo', f=100.0, b=True))
b: true
f: 100.0
i: 10
s: foo

>>> from_yaml(Foo, 'b: true\nf: 100.0\ni: 10\ns: foo')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Toml

Call `to_toml` to serialize `Foo` object into Toml string and `from_toml` to deserialize Toml string into `Foo` object. For more information, please visit [serde.toml](https://yukinarit.github.io/pyserde/api/serde/toml.html) module.

```python
>>> from serde.toml import from_toml, to_toml

>>> to_toml(Foo(i=10, s='foo', f=100.0, b=True))
i = 10
s = "foo"
f = 100.0
b = true

>>> from_toml(Foo, 'i = 10\ns = "foo"\nf = 100.0\nb = true')
Foo(i=10, s='foo', f=100.0, b=True)
```

## MsgPack

Call `to_msgpack` to serialize `Foo` object into MsgPack and `from_msgpack` to deserialize MsgPack into `Foo` object. For more information, please visit [serde.msgpack](https://yukinarit.github.io/pyserde/api/serde/msgpack.html) module.

```python

>>> from serde.msgpack import from_msgpack, to_msgpack

>>> to_msgpack(Foo(i=10, s='foo', f=100.0, b=True))
b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3'

>>> from_msgpack(Foo, b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3')
Foo(i=10, s='foo', f=100.0, b=True)
```
