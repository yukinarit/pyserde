# Supported data formats

`dict`, `tuple`, `JSON`, `Yaml`, `Toml`, `MsgPack` `Pickle`がサポートされています。

```python

@serde
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

## dict

```python
>>> from serde import to_dict, from_dict

>>> to_dict(Foo(i=10, s='foo', f=100.0, b=True))
from_dict(Foo, {"i": 10, "s": "foo", "f": 100.0, "b": True})

>>> from_dict(Foo, {"i": 10, "s": "foo", "f": 100.0, "b": True})
Foo(i=10, s='foo', f=100.0, b=True)
```

## tuple

```python
>>> from serde import to_tuple, from_tuple

>>> to_tuple(Foo(i=10, s='foo', f=100.0, b=True))
(10, 'foo', 100.0, True)

>>> from_tuple(Foo, (10, 'foo', 100.0, True))
Foo(i=10, s='foo', f=100.0, b=True)
```

## JSON

```python
>>> from serde.json import to_json, from_json

>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'

>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Yaml

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

```python

>>> from serde.msgpack import from_msgpack, to_msgpack

>>> to_msgpack(Foo(i=10, s='foo', f=100.0, b=True))
b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3'

>>> from_msgpack(Foo, b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Pickle

```python
>>> from serde.pickle import from_pickle, to_pickle

>>> to_pickle(Foo(i=10, s='foo', f=100.0, b=True))
b"\x80\x04\x95'\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x01i\x94K\n\x8c\x01s\x94\x8c\x03foo\x94\x8c\x01f\x94G@Y\x00\x00\x00\x00\x00\x00\x8c\x01b\x94\x88u."

>>> from_pickle(Foo, b"\x80\x04\x95'\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x01i\x94K\n\x8c\x01s\x94\x8c\x03foo\x94\x8c\x01f\x94G@Y\x00\x00\x00\x00\x00\x00\x8c\x01b\x94\x88u.")
Foo(i=10, s='foo', f=100.0, b=True)
```
