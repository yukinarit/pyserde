<h1 align="center"><code>pyserde</code></h1>
<p align="center">Yet another serialization library on top of <a href="https://docs.python.org/3/library/dataclasses.html">dataclasses</a>, inspired by <a href="https://github.com/serde-rs/serde">serde-rs</a>.</p>
<p align="center">
  <a href="https://pypi.org/project/pyserde/">
    <img alt="pypi" src="https://img.shields.io/pypi/v/pyserde.svg">
  </a>
  <a href="https://pypi.org/project/pyserde/">
    <img alt="pypi" src="https://img.shields.io/pypi/pyversions/pyserde.svg">
  </a>
  <a href="https://github.com/yukinarit/pyserde/actions/workflows/test.yml">
    <img alt="GithubActions" src="https://github.com/yukinarit/pyserde/actions/workflows/test.yml/badge.svg">
  </a>
  <a href="https://codecov.io/gh/yukinarit/pyserde">
    <img alt="CodeCov" src="https://codecov.io/gh/yukinarit/pyserde/branch/main/graph/badge.svg">
  </a>
</p>
<p align="center">
  <a href="https://yukinarit.github.io/pyserde/guide/en">Guide🇬🇧</a> | <a href="https://yukinarit.github.io/pyserde/guide/ja">ガイド🇯🇵</a> | <a href="https://yukinarit.github.io/pyserde/api/serde.html">API Reference</a> | <a href="https://github.com/yukinarit/pyserde/tree/main/examples">Examples</a>
</p>

## Overview

`pyserde` is a simple yet powerful serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html). It allows you to convert Python objects to and from JSON, YAML, and other formats easily and efficiently.

Declare your class with `@serde` decorator and annotate fields using [PEP484](https://peps.python.org/pep-0484/) as below.

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

That's it!  If you're interested in pyserde, please check our documentation!
Happy coding with pyserde! 🚀
* [Getting started](https://yukinarit.github.io/pyserde/guide/en/getting-started.html)
* [API Reference](https://yukinarit.github.io/pyserde/api/serde.html)
* [Examples](https://github.com/yukinarit/pyserde/tree/main/examples)

## Features

- Supported data formats
    - dict
    - tuple
    - JSON
	- Yaml
	- Toml
	- MsgPack
    - Pickle
- Supported types
    - Primitives (`int`, `float`, `str`, `bool`)
    - Containers
        - `list`, `collections.abc.Sequence`, `collections.abc.MutableSequence`, `tuple`
        - `set`, `collections.abc.Set`, `collections.abc.MutableSet`
        - `dict`, `collections.abc.Mapping`, `collections.abc.MutableMapping`
        - [`frozenset`](https://docs.python.org/3/library/stdtypes.html#frozenset), [`defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
    - [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
    - [`typing.Union`](https://docs.python.org/3/library/typing.html#typing.Union)
    - User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
    - [`typing.NewType`](https://docs.python.org/3/library/typing.html#newtype) for primitive types
    - [`typing.Any`](https://docs.python.org/3/library/typing.html#the-any-type)
    - [`typing.Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
    - [`typing.Generic`](https://docs.python.org/3/library/typing.html#user-defined-generic-types)
    - [`typing.ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar)
    - [`dataclasses.InitVar`](https://docs.python.org/3/library/dataclasses.html#init-only-variables)
    - [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum) and [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
    - Standard library
        - [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
        - [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
        - [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
        - [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects), [`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects), [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
        - [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)
    - PyPI library
        - [`numpy`](https://github.com/numpy/numpy) types
        - [`SQLAlchemy`](https://github.com/sqlalchemy/sqlalchemy) Declarative Dataclass Mapping (experimental)
- [Class Attributes](https://github.com/yukinarit/pyserde/blob/main/docs/en/class-attributes.md)
- [Field Attributes](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md)
- [Decorators](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md)
- [Type Check](https://github.com/yukinarit/pyserde/blob/main/docs/en/type-check.md)
- [Union Representation](https://github.com/yukinarit/pyserde/blob/main/docs/en/union.md)
- [Forward reference](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md#how-can-i-use-forward-references)
- [PEP563 Postponed Evaluation of Annotations](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md#pep563-postponed-evaluation-of-annotations)
- [PEP585 Type Hinting Generics In Standard Collections](https://github.com/yukinarit/pyserde/blob/main/docs/en/getting-started.md#pep585-and-pep604)
- [PEP604 Allow writing union types as X | Y](https://github.com/yukinarit/pyserde/blob/main/docs/en/getting-started.md#pep585-and-pep604)
- [PEP681 Data Class Transform](https://github.com/yukinarit/pyserde/blob/main/docs/en/decorators.md#serde)
- [PEP695 Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [Case Conversion](https://github.com/yukinarit/pyserde/blob/main/docs/en/class-attributes.md#rename_all)
- [Rename](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#rename)
- [Alias](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#alias)
- Skip (de)serialization ([skip](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip), [skip_if](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip_if), [skip_if_false](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip_if_false), [skip_if_default](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#skip_if_default))
- [Custom field (de)serializer](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#serializerdeserializer)
- [Custom class (de)serializer](https://github.com/yukinarit/pyserde/blob/main/docs/en/class-attributes.md#class_serializer--class_deserializer)
- [Custom global (de)serializer](https://github.com/yukinarit/pyserde/blob/main/docs/en/extension.md#custom-global-deserializer)
- [Flatten](https://github.com/yukinarit/pyserde/blob/main/docs/en/field-attributes.md#flatten)

## Extensions

* [pyserde-timedelta](https://github.com/yukinarit/pyserde-timedelta): (de)serializing datetime.timedelta in ISO 8601 duration format.

## Contributors ✨

Thanks goes to these wonderful people:

<a href="https://github.com/yukinarit/pyserde/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yukinarit/pyserde" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## LICENSE

This project is licensed under the [MIT license](https://github.com/yukinarit/pyserde/blob/main/LICENSE).
