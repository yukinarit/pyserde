
`pyserde` is a simple yet powerful serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html). Simply adding pyserde's `@serialize` and `@deserialize` decorators make your class (de)serializable.

```python
@deserialize
@serialize
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

You can serialize `Foo` object into JSON.

```python
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
{"i": 10, "s": "foo", "f": 100.0, "b": true}
```

You can deserialize JSON into `Foo`.
```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Features

pyserde supports other data formats (YAML, Toml, MsgPack) and offers many more features!

- [Supported types](supported-types.md)
- [Supported data formats](supported-data-formats.md)
- [Features](features/summary.md)
    - [Python 3.9 type hiting](features/python3.9-type-hinting.md)
    - [Postponed evaluation of type annotation](features/postponed-evaluation-of-type-annotation.md)
    - [Forward reference](features/forward-reference.md)
    - [Case Conversion](features/case-conversion.md)
    - [Rename](features/rename.md)
    - [Skip](features/skip.md)
    - [Conditional Skip](features/conditional-skip.md)
    - [Custom field (de)serializer](features/custom-field-serializer.md)
    - [Custom class (de)serializer](features/custom-class-serializer.md)
    - [Flatten](features/flatten.md)
