# Getting started

Install pyserde from PyPI. pyserde requires Python>=3.6.

```sh
pip install pyserde
```

Additional data formats besides JSON need additional dependencies installed. Install `msgpack`, `toml`, or `yaml` extras to work with the appropriate data formats; you can skip formats that you don't plan to use. For example, if you want to use Toml and YAML:

```sh
pip install "pyserde[toml,yaml]"
```

Or all at once:

```sh
pip install "pyserde[all]"
```

Define your class with pyserde's `@serialize` and `@deserialize` decorators. Be careful that module name is `serde`, not `pyserde`. `pyserde` depends on `dataclasses` module. If you are new to dataclass, I would recommend to read [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) first.

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

pyserde generates methods necessary for serialization by `@serialize` and methods necessary for deserialization by `@deserialize` when a class is loaded into python interpreter. The code generation occurs only once and there is no overhead when you use the generated methods. Now your class is serializable and deserializable in the data formats supported by pyserde.

> **Note:** If you need only either of serialization or deserialization functionality, you can omit one of those decorators.
>
> e.g. If you don't need deserialization, you can add `@serialization` decorator only. But, calling deserialize API e.g. `from_json` for `Foo` will raise an error.
> ```python
> @serialize
> @dataclass
> class Foo:
>     i: int
>     s: str
>     f: float
>     b: bool
> ```

Next, import pyserde (de)serialize API. For JSON:

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

Pass `Foo` class and JSON string in `from_json` to deserialize JSON into the object.
```python
s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
print(from_json(Foo, s))
```

That's it! pyserde offers many more features. If you're interested, please read the rest of the documentation.

