# Introduction

`pyserde` is a simple yet powerful serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html). Simply adding pyserde's `@serde` decorator makes your class (de)serializable.

```python
@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

You can serialize `Foo` object into JSON.

```python
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'
```

You can deserialize JSON into `Foo` object.
```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Features

- [Supported types](supported-types.md)
    - JSON
	- Yaml
	- Toml
	- MsgPack
- [Supported data formats](supported-data-formats.md)
    - Primitives (`int`, `float`, `str`, `bool`)
    - Containers (`List`, `Set`, `Tuple`, `Dict`)
    - [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
    - [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)
    - User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
    - [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) for primitive types
    - [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type)
    - [`typing.Generic`](https://docs.python.org/3/library/typing.html#user-defined-generic-types)
    - [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
    - Standard library
        - [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
        - [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
        - [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
        - [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects) & [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
        - [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)
- [Attributes](features/attributes.md)
- [Decorators](features/decorators.md)
- [TypeCheck](features/type-check.md)
- [Union Representation](features/union.md)
- [Python 3.10 Union operator](features/union-operator.md)
- [Python 3.9 type hinting](features/python3.9-type-hinting.md)
- [Postponed evaluation of type annotation](features/postponed-evaluation-of-type-annotation.md)
- [Forward reference](features/forward-reference.md)
- [Case Conversion](features/case-conversion.md)
- [Rename](features/rename.md)
- [Skip](features/skip.md)
- [Conditional Skip](features/conditional-skip.md)
- [Custom field (de)serializer](features/custom-field-serializer.md)
- [Custom class (de)serializer](features/custom-class-serializer.md)
- [Flatten](features/flatten.md)
