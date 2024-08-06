# Introduction

`pyserde` is a simple yet powerful serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html). It allows you to convert Python objects to and from JSON, YAML, and other formats easily and efficiently.

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

## Next Steps

* [Getting started](getting-started.md)
* [API Reference](https://yukinarit.github.io/pyserde/api/serde.html)
* [Examples](https://github.com/yukinarit/pyserde/tree/main/examples)
* [FAQ](faq.md)
