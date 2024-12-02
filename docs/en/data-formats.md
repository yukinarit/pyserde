# Data Formats

pyserde supports several data formats for serialization and deserialization, including `dict`, `tuple`, `JSON`, `YAML`, `TOML`, `MsgPack`, and `Pickle`. Each API can take additional keyword arguments, which are forwarded to the underlying packages used by pyserde.

e.g. If you want to preserve the field order in YAML, you can pass `sort_key=True` in `serde.yaml.to_yaml`

```python
serde.yaml.to_yaml(foo, sort_key=True)
```

`sort_key=True` will be passed in the [yaml.safedump](https://github.com/yukinarit/pyserde/blob/a9f44d52d109144a4c3bb93965f831e91d13960b/serde/yaml.py#L18)

## dict

```python
>>> from serde import to_dict, from_dict

>>> to_dict(Foo(i=10, s='foo', f=100.0, b=True))
{"i": 10, "s": "foo", "f": 100.0, "b": True}

>>> from_dict(Foo, {"i": 10, "s": "foo", "f": 100.0, "b": True})
Foo(i=10, s='foo', f=100.0, b=True)
```

See [serde.to_dict](https://yukinarit.github.io/pyserde/api/serde/se.html#to_dict) / [serde.from_dict](https://yukinarit.github.io/pyserde/api/serde/de.html#from_dict) for more information.

## tuple

```python
>>> from serde import to_tuple, from_tuple

>>> to_tuple(Foo(i=10, s='foo', f=100.0, b=True))
(10, 'foo', 100.0, True)

>>> from_tuple(Foo, (10, 'foo', 100.0, True))
Foo(i=10, s='foo', f=100.0, b=True)
```

See [serde.to_tuple](https://yukinarit.github.io/pyserde/api/serde/se.html#to_tuple) / [serde.from_tuple](https://yukinarit.github.io/pyserde/api/serde/de.html#from_tuple) for more information.

## JSON

```python
>>> from serde.json import to_json, from_json

>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'

>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

See [serde.json.to_json](https://yukinarit.github.io/pyserde/api/serde/json.html#to_json) / [serde.json.from_json](https://yukinarit.github.io/pyserde/api/serde/json.html#from_json) for more information.

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

See [serde.yaml.to_yaml](https://yukinarit.github.io/pyserde/api/serde/yaml.html#to_yaml) / [serde.yaml.from_yaml](https://yukinarit.github.io/pyserde/api/serde/yaml.html#from_yaml) for more information.

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

See [serde.toml.to_toml](https://yukinarit.github.io/pyserde/api/serde/toml.html#to_toml) / [serde.toml.from_toml](https://yukinarit.github.io/pyserde/api/serde/toml.html#from_toml) for more information.

## MsgPack

```python

>>> from serde.msgpack import from_msgpack, to_msgpack

>>> to_msgpack(Foo(i=10, s='foo', f=100.0, b=True))
b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3'

>>> from_msgpack(Foo, b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3')
Foo(i=10, s='foo', f=100.0, b=True)
```

See [serde.msgpack.to_msgpack](https://yukinarit.github.io/pyserde/api/serde/msgpack.html#to_msgpack) / [serde.msgpack.from_msgpack](https://yukinarit.github.io/pyserde/api/serde/msgpack.html#from_msgpack) for more information.

## Pickle

New in v0.9.6

```python
>>> from serde.pickle import from_pickle, to_pickle

>>> to_pickle(Foo(i=10, s='foo', f=100.0, b=True))
b"\x80\x04\x95'\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x01i\x94K\n\x8c\x01s\x94\x8c\x03foo\x94\x8c\x01f\x94G@Y\x00\x00\x00\x00\x00\x00\x8c\x01b\x94\x88u."

>>> from_pickle(Foo, b"\x80\x04\x95'\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x01i\x94K\n\x8c\x01s\x94\x8c\x03foo\x94\x8c\x01f\x94G@Y\x00\x00\x00\x00\x00\x00\x8c\x01b\x94\x88u.")
Foo(i=10, s='foo', f=100.0, b=True)
```

See [serde.pickle.to_pickle](https://yukinarit.github.io/pyserde/api/serde/pickle.html#to_pickle) / [serde.pickle.from_pickle](https://yukinarit.github.io/pyserde/api/serde/pickle.html#from_pickle) for more information.

## Needs a new data format support?

We don't plan to supprot a data format such as XML to keep pyserde as simple as possible. If you need a new data format support, we recommend to create a separate python package. If the data format is interchangable to dict or tuple, implementing the serialize/desrialize API is not that difficult. See [YAML's implementation](https://github.com/yukinarit/pyserde/blob/main/serde/yaml.py) to know how to implement.
