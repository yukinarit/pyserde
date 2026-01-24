# Introduction

`pyserde` is a simple yet powerful serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html). It allows you to convert Python objects to and from JSON, YAML, and other formats easily and efficiently.

pyserde focuses on dataclass-first workflows and keeps runtime overhead low by generating serializers when classes are loaded.

Highlights:
- Multiple formats (`dict`, `tuple`, JSON, YAML, TOML, MsgPack, Pickle)
- Rich type support (Optional, Union, Literals, enums, datetime, numpy, etc.)
- Runtime type checking and extensibility hooks

Declare your class with `@serde` decorator and annotate fields using [PEP484](https://peps.python.org/pep-0484/) as below.

```python
from serde import serde

@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

You can serialize `Foo` object into JSON.

```python
>>> from serde.json import to_json
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'
```

You can deserialize JSON into `Foo` object.
```python
>>> from serde.json import from_json
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

pyserde also provides in-memory formats like `dict` and `tuple`, plus YAML, TOML, MsgPack, and Pickle when their extras are installed.

```python
>>> from serde import to_dict, from_dict
>>> to_dict(Foo(i=10, s='foo', f=100.0, b=True))
{"i": 10, "s": "foo", "f": 100.0, "b": True}
>>> from_dict(Foo, {"i": 10, "s": "foo", "f": 100.0, "b": True})
Foo(i=10, s='foo', f=100.0, b=True)
```

## Next Steps

* [Getting started](getting-started.md)
* [API Reference](https://yukinarit.github.io/pyserde/api/serde.html)
* [Examples](https://github.com/yukinarit/pyserde/tree/main/examples)
* [FAQ](faq.md)
