# Decorators

## `@serde`

`@serde` is a wrapper of `@serialize` and `@deserialize` decorators.

This code
```python
@serde
class Foo:
    ...
```

is equivalent to the following code.

```python
@deserialize
@serialize
@dataclass
class Foo:
    ...
```

`@serde` decorator does these for you:
* Add `@serialize` and `@deserialize` decorators to a class
* Add `@dataclass` decorator to a class if a class doesn't have `@dataclass`
* You can pass both (de)serialize attributes to the decorator
    * `serializer` attribute is ignored in `@deserialize` and `deserializer` attribute is ignored in `@serialize`

```python
@serde(serializer=serializer, deserializer=deserializer)
@dataclass
class Foo:
    ...
```

> **NOTE:** `@serde` actually works without @dataclass decorator, because it detects and add @dataclass to the declared class automatically. However, mypy will produce `Too many arguments` or `Unexpected keyword argument` error. This is due to [the mypy limitation](https://mypy.readthedocs.io/en/stable/additional_features.html#caveats-known-issues).
>
> ```python
> @serde
> class Foo:
>     ...
> ```
>
> But if you use a PEP681 compliant type checker (e.g. pyright), you don't get the type error because pyserde supports [PEP681 dataclass_transform](https://peps.python.org/pep-0681/)


## `@serialize`/`@deserialize`

`@serialize` and `@deserialize` are used by `@serde` under the hood. We recommend to use those two decorators in the following cases. Otherwise `@serde` is recommended.
* You only need either serialization or deserialization functionality
* You want to have different class attributes as below

```python
@deserialize(rename_all = "snakecase")
@serialize(rename_all = "camelcase")
class Foo:
    ...
```

## (de)serializing class without `@serde`

pyserde can (de)serialize dataclasses without `@serde` since v0.10.0. This feature is convenient when you want to use classes declared in external libraries or a type checker doesn't work with `@serde` decorator. See [this example](https://github.com/yukinarit/pyserde/blob/main/examples/plain_dataclass.py).

How does it work? It's quite simple that pyserde add `@serde` decorator if a class doesn't has it. It may take for a while for the first API call, but the generated code will be cached internally. So it won't be a problem. See the following example to deserialize a class in a third party package.

```python
@dataclass
class External:
    ...

to_dict(External()) # works without @serde
```

Note that you can't specify class attributes e.g. `rename_all` in this case. If you want to add a class attribute to an external dataclass, there is a technique to do that by extending dataclass. See [this example](https://github.com/yukinarit/pyserde/blob/main/examples/plain_dataclass_class_attribute.py).

```python
@dataclass
class External:
    some_value: int

@serde(rename_all="kebabcase")
@dataclass
class Wrapper(External):
    pass
```

## How can I use forward references?

pyserde supports forward references. If you replace a nested class name with with string, pyserde looks up and evaluate the decorator after nested class is defined.

```python
from __future__ import annotations # make sure to import annotations

@dataclass
class Foo:
    i: int
    s: str
    bar: Bar  # Bar can be specified although it's declared afterward.

@serde
@dataclass
class Bar:
    f: float
    b: bool

# Evaluate pyserde decorators after `Bar` is defined.
serde(Foo)
```

## PEP563 Postponed Evaluation of Annotations

pyserde supports [PEP563 Postponed evaluation of annotation](https://peps.python.org/pep-0563/).

```python
from __future__ import annotations
from serde import serde

@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool

    def foo(self, cls: Foo):  # You can use "Foo" type before it's defined.
        print('foo')
```

See [examples/lazy_type_evaluation.py](https://github.com/yukinarit/pyserde/blob/main/examples/lazy_type_evaluation.py) for complete example.
