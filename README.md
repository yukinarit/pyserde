# pyserde

[![image](https://img.shields.io/pypi/v/pyserde.svg)](https://pypi.org/project/pyserde/)
[![image](https://img.shields.io/pypi/pyversions/pyserde.svg)](https://pypi.org/project/pyserde/)
[![Build Status](https://travis-ci.org/yukinarit/pyserde.svg?branch=master)](https://travis-ci.org/yukinarit/pyserde)
[![Build status](https://ci.appveyor.com/api/projects/status/w4i5x8x9d4sbxhn2?svg=true)](https://ci.appveyor.com/project/yukinarit/pyserde)
[![Coverage Status](https://coveralls.io/repos/github/yukinarit/pyserde/badge.svg?branch=master)](https://coveralls.io/github/yukinarit/pyserde?branch=master)

Serialization Library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html).

## QuickStart

Install pyserde from PyPI.

```bash
$ pip install pyserde
```

You can serialize and deserialize a dataclass in various message formats quite easily!

```python
# main.py
# /usr/bin/env python
from dataclasses import dataclass
from serde import deserialize, serialize
from serde.json import from_json, to_json

@deserialize
@serialize
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool

h = Foo(i=10, s='foo', f=100.0, b=True)
print(f"Into Json: {to_json(h)}")

s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
print(f"From Json: {from_json(Foo, s)}")
```

```bash
$ python main.py
Into Json: {"i": 10, "s": "foo", "f": 100.0, "b": true}
From Json: Foo(i=10, s='foo', f=100.0, b=True)
```

## Benchmark

Serialize and Deserialize a [struct](https://github.com/yukinarit/pyserde/blob/master/bench/dataclasses_class.py#L7-L12) in json 10,000 times.

* macOS 10.14 Mojave
* Intel 2.3GHz 8-core Intel Core i9
* DDR4 32GB RAM

| Serialize | Deserialize |
|-----------|-------------|
| <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/serialize_small.png"> | <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/deserialize_small.png"> |

* `raw`: Manual serialize and deserialize. Fastest in theory.
* [`dacite`](https://github.com/konradhalas/dacite): Library to crate data class from dictionary.
* [`mashumaro`](https://github.com/Fatal1ty/mashumaro): Another seralization library based on dataclass.

You can check [the benchmark code](bench/bench.py) for more information.

## Features

<details open><summary><b><code>Supported types</code></b></summary><br />

* primitives (int, float, str, bool)
* containers (List, Tuple, Dict)
* [`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
* [`Dataclass`](https://docs.python.org/3/library/dataclasses.html)

</details>

<details open><summary><b><code>Supported data formats</code></b></summary><br />

```python
from dataclasses import dataclass
from serde import deserialize, serialize

@deserialize
@serialize
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool

h = Foo(i=10, s='foo', f=100.0, b=True)
```

* JSON
    ```python
    from serde.json import from_json, to_json
    print(f"Into Json: {to_json(h)}")
    print(f"From Json: {from_json(Foo, s)}")
    ```

* Yaml
    ```python
    from serde.yaml import from_yaml, to_yaml
    print(f"Into Yaml: {to_yaml(h)}")
    print(f"From Yaml: {from_yaml(Foo, s)}")
    ```

* Toml
    ```python
    from serde.toml import from_toml, to_toml
    print(f"Into Toml: {to_toml(h)}")
    print(f"From Toml: {from_toml(Foo, s)}")
    ```

* MsgPack
    ```python
    from serde.msgpack import from_msgpack, to_msgpack
    print(f"Into MsgPack: {to_msgpack(h)}")
    print(f"From MsgPack: {from_msgpack(Foo, s)}")
    ```

</details>

<details open><summary><b><code>Case Conversion</code></b></summary><br />

Converting `snake_case` fields into supported case styles e.g. `camelCase` and `kebab-case`.

```python
@serialize(rename_all = 'camelcase')
@dataclass
class Foo:
    int_field: int
    str_field: str

f = Foo(int_field=10, str_field='foo')
print(to_json(f))
```

Here, the output is all `camelCase`.

```json
'{"intField": 10, "strField": "foo"}'
```
</details>

<details open><summary><b><code>Rename Field</code></b></summary><br />

In case you want to use a keyword as field such as `class`, you can use `serde_rename` field attribute.

```python
@serialize
@dataclass
class Foo:
    class_name: str = field(metadata={'serde_rename': 'class'})

print(to_json(Foo(class_name='Foo')))
```

Output json is having `class` instead of `class_name`.

```json
{"class": "Foo"}
```

For complete example, please see [./examples/rename.py](./examples/rename.py)

</details>

<details><summary><b><code>Skip</code></b></summary><br />

You can skip serialization for a certain field, you can use `serde_skip`.

```python
@serialize
@dataclass
class Resource:
    name: str
    hash: str
    metadata: Dict[str, str] = field(default_factory=dict, metadata={'serde_skip': True})

resources = [
    Resource("Stack Overflow", "hash1"),
    Resource("GitHub", "hash2", metadata={"headquarters": "San Francisco"}) ]
print(to_json(resources))
```

Here, `metadata` is not present in output json.

```json
[{"name": "Stack Overflow", "hash": "hash1"}, {"name": "GitHub", "hash": "hash2"}]
```

For complete example, please see [./examples/skip.py](./examples/skip.py)

</details>

<details><summary><b><code>Conditional Skip</code></b></summary><br />

If you conditionally skip some fields, you can pass function or lambda in `serde_skip_if`.

```python
@serialize
@dataclass
class World:
    player: str
    buddy: str = field(default='', metadata={'serde_skip_if': lambda v: v == 'Pikachu'})

world = World('satoshi', 'Pikachu')
print(to_json(world))

world = World('green', 'Charmander')
print(to_json(world))
```

As you can see below, field is skipped in serialization if `buddy` is "Pikachu".

```json
{"player": "satoshi"}
{"player": "green", "buddy": "Charmander"}
```

For complete example, please see [./examples/skip.py](./examples/skip.py)

</details>

## Documentation

https://yukinarit.github.io/pyserde/
