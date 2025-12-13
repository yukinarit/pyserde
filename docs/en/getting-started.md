# Getting started

## Installation

Install pyserde from PyPI. pyserde requires Python>=3.10.

```
pip install pyserde
```

If you're using uv, run this command.
```
uv add pyserde
```

Additional data formats besides JSON and Pickle need additional dependencies installed. Install `msgpack`, `toml` or `yaml` extras to work with the appropriate data formats; you can skip formats that you don't plan to use. For example, if you want to use Toml and YAML:

```
pip install "pyserde[toml,yaml]"
```

With uv
```
uv add pyserde --extra toml --extra yaml
```

Or all at once:

```
pip install "pyserde[all]"
```

With uv
```
uv add pyserde --extra all
```

Here are the available extras
* `all`: Install `msgpack`, `toml`, `yaml`, `numpy`, `orjson`, and `sqlalchemy` extras
* `msgpack`: Install [msgpack](https://github.com/msgpack/msgpack-python)
* `toml`: Install [tomli](https://github.com/hukkin/tomli) and [tomli-w](https://github.com/hukkin/tomli-w)
	* NOTE: [tomllib](https://docs.python.org/3/library/tomllib.html) is used for python 3.11 onwards
* `yaml`: Install [pyyaml](https://github.com/yaml/pyyaml)
* `numpy`: Install [numpy](https://github.com/numpy/numpy)
* `orjson`: Install [orjson](https://github.com/ijl/orjson)
* `sqlalchemy`: Install [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy)

## Define your first pyserde class

Define your class with pyserde's `@serde` decorators. Be careful that module name is `serde`, not `pyserde`. `pyserde` heavily depends on the standard library's `dataclasses` module. If you are new to dataclass, I would recommend to read [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) first.

```python
from serde import serde

@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

pyserde generates methods necessary for (de)serialization by `@serde` when a class is loaded into python interpreter. The code generation occurs only once and there is no overhead when you use the class. Now your class is serializable and deserializable in all the data formats supported by pyserde.

> **NOTE:** If you need only either serialization or deserialization functionality, you can use `@serialize` or `@deserialize` instead of `@serde` decorator.
>
> e.g. If you do only serialization, you can use `@serialize` decorator. But calling deserialize API e.g. `from_json` for `Foo` will raise an error.
> ```python
> from serde import serialize
>
> @serialize
> class Foo:
>     i: int
>     s: str
>     f: float
>     b: bool
> ```

## PEP585 and PEP604

[PEP585](https://www.python.org/dev/peps/pep-0585/) style annotations and the [PEP604](https://www.python.org/dev/peps/pep-0604/) union operator are supported for python>=3.10. With PEP585 and PEP604, you can write a pyserde class pretty neatly.
```python
@serde
class Foo:
    a: int
    b: list[str]
    c: tuple[int, float, str, bool]
    d: dict[str, list[tuple[str, int]]]
    e: str | None
```

## Use pyserde class

Next, import pyserde (de)serialize APIs. For JSON:

```python
from serde.json import from_json, to_json
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

> 💡 Tip: which type checker should I use?
> pyserde depends on [PEP681 dataclass_transform](https://peps.python.org/pep-0681/). [mypy](https://github.com/python/mypy) does not fully support dataclass_transform as of Jan. 2024. My personal recommendation is [pyright](https://github.com/microsoft/pyright).
