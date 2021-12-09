# `pyserde`

Yet another serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html), inspired by [serde-rs](https://github.com/serde-rs/serde).

[![image](https://img.shields.io/pypi/v/pyserde.svg)](https://pypi.org/project/pyserde/)
[![image](https://img.shields.io/pypi/pyversions/pyserde.svg)](https://pypi.org/project/pyserde/)
![Tests](https://github.com/yukinarit/pyserde/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/yukinarit/pyserde/branch/master/graph/badge.svg)](https://codecov.io/gh/yukinarit/pyserde)

[Guide](https://yukinarit.github.io/pyserde/guide) | [API Docs](https://yukinarit.github.io/pyserde/api/serde.html) | [Examples](./examples)

## Overview

Declare a class with pyserde's `@serde` decorator.

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
{"i": 10, "s": "foo", "f": 100.0, "b": true}
```

You can deserialize JSON into `Foo` object.
```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

## Features

- Supported data formats
    - dict
    - tuple
    - JSON
	- Yaml
	- Toml
	- MsgPack
- Supported types
    - Primitives (`int`, `float`, `str`, `bool`)
    - Containers (`List`, `Set`, `Tuple`, `Dict`)
    - [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
    - [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)
    - User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
    - [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) for primitive types
    - [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type)
    - [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
    - Standard library
        - [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
        - [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
        - [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
        - [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects), [`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects), [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
        - [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)
- [decorators](docs/features/decorators.md)
- [Python 3.9 type hinting](docs/features/python3.9-type-hinting.md)
- [Postponed evaluation of type annotation](docs/features/postponed-evaluation-of-type-annotation.md)
- [Forward reference](docs/features/forward-reference.md)
- [Case Conversion](docs/features/case-conversion.md)
- [Rename](docs/features/rename.md)
- [Skip](docs/features/skip.md)
- [Conditional Skip](docs/features/conditional-skip.md)
- [Custom field (de)serializer](docs/features/custom-field-serializer.md)
- [Custom class (de)serializer](docs/features/custom-class-serializer.md)
- [Flatten](docs/features/flatten.md)

## LICENSE

This project is licensed under the [MIT license](https://github.com/yukinarit/pyserde/blob/master/LICENSE).
