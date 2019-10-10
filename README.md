# pyserde

[![image](https://img.shields.io/pypi/v/pyserde.svg)](https://pypi.org/project/pyserde/)
[![image](https://img.shields.io/pypi/pyversions/pyserde.svg)](https://pypi.org/project/pyserde/)
[![Build Status](https://travis-ci.org/yukinarit/pyserde.svg?branch=master)](https://travis-ci.org/yukinarit/pyserde)
[![Build status](https://ci.appveyor.com/api/projects/status/w4i5x8x9d4sbxhn2?svg=true)](https://ci.appveyor.com/project/yukinarit/pyserde)
[![Coverage Status](https://coveralls.io/repos/github/yukinarit/pyserde/badge.svg?branch=master)](https://coveralls.io/github/yukinarit/pyserde?branch=master)

Serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html).

## Installation

```bash
$ pip install pyserde
```

## QuickStart

You can serialize/deserialize your class to/from various message formant (e.g. Json, MsgPack) quite easily!

```python
# main.py
# /usr/bin/env python

from dataclasses import dataclass
from serde import deserialize, serialize
from serde.json import from_json, to_json

# Mark the class serializable/deserializable.
@deserialize
@serialize
@dataclass
class Hoge:
    i: int
    s: str
    f: float
    b: bool

h = Hoge(i=10, s='hoge', f=100.0, b=True)

print(f"Into Json: {to_json(h)}")

s = '{"i": 10, "s": "hoge", "f": 100.0, "b": true}'

print(f"From Json: {from_json(Hoge, s)}")
```

```bash
$ python main.py
Into Json: {"i": 10, "s": "hoge", "f": 100.0, "b": true}
From Json: Hoge(i=10, s='hoge', f=100.0, b=True)
```

## Benchmark

Serialize and Deserialize [a small struct](https://github.com/yukinarit/pyserde/blob/bench/bench/dataclasses_class.py#L7-L12) into and from json 10,000 times.

### Environment

* macOS 10.14 Mojave
* Intel 2.3GHz 8-core Intel Core i9
* DDR4 32GB RAM

### Result

| Serialize | Deserialize |
|-----------|-------------|
| <img src="./bench/charts/serialize_small.png"> | <img src="./bench/charts/deserialize_small.png"> |

* `raw` Manual serialize and deserialize. Fastest in theory.
* [`dacite`](https://github.com/konradhalas/dacite)
* [`mashumaro`](https://github.com/Fatal1ty/mashumaro)

You can check [the code](bench/bench.py) for more information.

## Features

* Data format
	* [Json](./examples/jsonfile.py)
	* [Toml](./examples/tomlfile.py)
	* [Yaml](./examples/yamlfile.py)
	* [MsgPack](./examples/msgpack.py)
* Class attributes
	* [Case conversion](#case-conversion) e.g. camelCase, kebab-case
* Field attributes
    * [Rename](#rename-field)
    * [Skip](#skip)
    * [Skip-if](#skip-if)
    * [Skip if value is evaluated as False](#skip-if-value-is-evaluated-as-false)

### Case conversion

```python
>>> @serialize(rename_all = 'camelcase')
... @dataclass
... class Hoge:
...     int_field: int
...     str_field: str
>>>
>>> to_json(Hoge(int_field=10, str_field='hoge'))
'{"intField": 10, "strField": "hoge"}'
```

### Rename field

```python
>>> @serialize
... @dataclass
... class Hoge:
...     # Use 'class_name' because 'class' is a keyword.
...     class_name: str = field(metadata={'serde_rename': 'class'})
>>> to_json(Hoge(class_name='Hoge'))
'{"class": "Hoge"}'
```

For complete example, please see [./examples/rename.py](./examples/rename.py)

### Skip

```python
>>> @serialize
... @dataclass
... class Resource:
...     name: str
...     hash: str
...     metadata: Dict[str, str] = field(default_factory=dict, metadata={'serde_skip': True})

>>> resources = [
...     Resource("Stack Overflow", "b6469c3f31653d281bbbfa6f94d60fea130abe38"),
...     Resource("GitHub", "5cb7a0c47e53854cd00e1a968de5abce1c124601", metadata={"headquarters": "San Francisco"}) ]
>>> to_json(resources)
'[{"name": "Stack Overflow", "hash": "b6469c3f31653d281bbbfa6f94d60fea130abe38"}, {"name": "GitHub", "hash": "5cb7a0c47e53854cd00e1a968de5abce1c124601"}]'
```

For complete example, please see [./examples/skip.py](./examples/skip.py)

### Skip if

```python
>>> @serialize
... @dataclass
... class World:
...     player: str
...     buddy: str = field(default='', metadata={'serde_skip_if': lambda v: v == 'Pikachu'})

>>> world = World('satoshi', 'Pikachu')
>>> to_json(world)
'{"player": "satoshi"}'

>>> world = World('green', 'Charmander')
>>> print(to_json(world))
'{"player": "green", "buddy": "Charmander"}'
```

For complete example, please see [./examples/skip.py](./examples/skip.py)

### Skip if value is evaluated as False

```python
>>> @serialize
... @dataclass
... class World:
...     player: str
...     enemies: List[str] = field(default_factory=list, metadata={'serde_skip_if_false': True})

>>> world = World('satoshi', ['Rattata', 'Pidgey'])
>>> to_json(world)
'{"player": "satoshi", "enemies": ["Rattata", "Pidgey"]}'

>>> world = World('green', [])
>>> print(to_json(world))
'{"player": "green"}'
```

For complete example, please see [./examples/skip.py](./examples/skip.py)

## Documentation

https://yukinarit.github.io/pyserde/
