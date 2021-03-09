## pyserde

[![image](https://img.shields.io/pypi/v/pyserde.svg)](https://pypi.org/project/pyserde/)
[![image](https://img.shields.io/pypi/pyversions/pyserde.svg)](https://pypi.org/project/pyserde/)
![Tests](https://github.com/yukinarit/pyserde/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/yukinarit/pyserde/branch/master/graph/badge.svg)](https://codecov.io/gh/yukinarit/pyserde)

Yet another serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html).

## TL;DR

Put additional `@serialize` and `@deserialize` decorator in your ordinary dataclass.

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

Now you can convert an object to JSON,

```python
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
{"i": 10, "s": "foo", "f": 100.0, "b": true}
```

Converted back from JSON to the object quite easily!

```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```

pyserde supports other data formats (YAML, Toml, MsgPack) and offers many more features!

## Benchmark

* macOS 10.14 Mojave
* Intel 2.3GHz 8-core Intel Core i9
* DDR4 32GB RAM

Serialize and deserialize a [struct](https://github.com/yukinarit/pyserde/blob/master/bench/dataclasses_class.py#L7-L12) into and from json 10,000 times.

| Serialize | Deserialize |
|-----------|-------------|
| <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/se-small.png"> | <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/de-small.png"> |

Serialize the struct into tuple and dictionary.

| to_tuple | to_dict |
|-----------|-------------|
| <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/astuple-small.png"> | <img src="https://raw.githubusercontent.com/yukinarit/pyserde/master/bench/charts/asdict-small.png"> |

* `raw`: Serialize and deserialize manually. Fastest in theory.
* `dataclass`: Serialize using dataclass's asdict.
* `pyserde`: This library.
* [`dacite`](https://github.com/konradhalas/dacite): Simple creation of data classes from dictionaries.
* [`mashumaro`](https://github.com/Fatal1ty/mashumaro): Fast and well tested serialization framework on top of dataclasses.
* [`marshallow`](https://github.com/marshmallow-code/marshmallow): A lightweight library for converting complex objects to and from simple datatypes.
* [`attrs`](https://github.com/python-attrs/attrs): Python Classes Without Boilerplate.
* [`cattrs`](https://github.com/Tinche/cattrs): Complex custom class converters for attrs.

To run benchmark in your environment:

```sh
git clone git@github.com:yukinarit/pyserde.git
cd pyserde/bench
pipenv install
pipenv run python bench.py --full
```

You can check [the benchmarking code](https://github.com/yukinarit/pyserde/blob/master/bench/bench.py) for more information.

## Getting started

Install pyserde from PyPI. pyserde requires Python>=3.6.

```sh
pip install pyserde
```

Additional data formats besides JSON need additional dependencies installed. Install `msgpack`, `toml`, or `yaml` extras to work with the appropriate data formats; you can skip formats that you don't plan to use. For example, if you want to use Toml and YAML:

```sh
pip install pyserde[toml,yaml]
```

Or all at once:

```sh
pip install pyserde[all]
```

Put additional `@serialize` and `@deserialize` decorator in your ordinary dataclass. Be careful that module name is `serde`, not `pyserde`. If you are new to dataclass, I would recommend to read [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) first.

```python
from serde import serialize, deserialize
from dataclasses import dataclass

@deserialize
@serialize
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

pyserde generates methods necessary for serialization by `@serialize` and methods necessary for deserialization by `@deserialize` when a class is loaded into python interpreter. Generation occurs exactly only once (This is more like how decorator work, not pyserde) and there is no overhead when you actually use the generated methods. Now your class is serializable and deserializable in the data formats supported by pyserde.

Next, import pyserde helper methods. For JSON:
```python
from serde.json import from_json, to_json
```

Similarly, you can use other data formats.
```python
from serde.yaml import from_yaml, to_yaml
from serde.toml import from_toml, to_toml
from serde.msgpack import from_msgpack to_msgpack
```

Use `to_json` to serialize the object into JSON.
```
f = Foo(i=10, s='foo', f=100.0, b=True)
print(to_json(f))
```

Pass `Foo` class and JSON string in `from_json` to deserialize into Object.
```python
s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
print(from_json(Foo, s))
```

That's it! pyserde offers many more features. If you're interested, please read the rest of the documentation.

## Supported types

* Primitives (int, float, str, bool)
* Containers (List, Set, Tuple, Dict)
* [`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
* User defined class with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
* [Enum](https://docs.python.org/3/library/enum.html#enum.Enum) and [IntEnum](https://docs.python.org/3/library/enum.html#enum.IntEnum)
* More types
    * [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html)
    * [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html)
    * [`uuid.UUID`](https://docs.python.org/3/library/uuid.html)
    * [`datetime.date`](https://docs.python.org/3/library/datetime.html#date-objects) & [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime-objects)
    * [`ipaddress`](https://docs.python.org/3/library/ipaddress.html)

You can write pretty complex class like this:
```python
@deserialize
@serialize
@dataclass
class bar:
    i: int

@deserialize
@serialize
class Foo:
    i: int
    l: List[str]
    t: Tuple[int, float, str, bool]
    d: Dict[str, List[Tuple[str, int]]]
    o: Optional[str]
    nested: Bar
```

For python >= 3.9, you can use [PEP585](https://www.python.org/dev/peps/pep-0585/) style type annotations for standard collections.

```python
@deserialize
@serialize
class Foo:
    i: int
    l: list[str]
    t: tuple[int, float, str, bool]
    d: dict[str, list[tuple[str, int]]]
    o: Optional[str]
    nested: Bar
```

## Supported data formats

### JSON

```python
from serde.json import from_json, to_json
print(to_json(f))
print(from_json(Foo, s))
```

### Yaml

```python
from serde.yaml import from_yaml, to_yaml
print(to_yaml(f))
print(from_yaml(Foo, s))
```

### Toml

```python
from serde.toml import from_toml, to_toml
print(to_toml(f))
print(from_toml(Foo, s))
```

### MsgPack

```python
from serde.msgpack import from_msgpack, to_msgpack
print(to_msgpack(f))
print(from_msgpack(Foo, s))
```

## Case Conversion

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

## Rename Field

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


## Skip

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

## Conditional Skip

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

## FAQ

### How can I see the code generated by pyserde?

pyserde provides `inspect` submodule that works as commandline:
```
python -m serde.inspect <PATH_TO_FILE> <CLASS>
```

e.g. in pyserde project

```
cd pyserde
pipenv shell
python -m serde.inspect examples/simple.py Foo
```

Output
```
Loading simple.Foo from examples.
def to_iter(obj, reuse_instances=True, convert_sets=False):
    if reuse_instances is Ellipsis:
        reuse_instances = True
    if convert_sets is Ellipsis:
        convert_sets = False

    if not is_dataclass(obj):
        return copy.deepcopy(obj)

    Foo = serde_scope.types["Foo"]
    res = []
    res.append(obj.i)
    res.append(obj.s)
    res.append(obj.f)
    res.append(obj.b)
    return tuple(res)
```

## LICENSE

MIT
