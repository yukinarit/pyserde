# Decorators

## `@serde`

`@serde` is a shortcut of `@serialize` and `@deserialize` decorators.

This code
```python
@serde
@dataclass
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

`@serde` decorator does those for you:
* Automatically add @serialize and @deserialize decorators to a class
* Automatically add @dataclass decorator to a class
* You can pass both (de)serialize attributes to the decorator
    * `serializer` attribute is ignored in `@deserialize` and `deserializer` attribute is ignored in `@serialize`

```python
@serde(serializer=serializer, deserializer=deserializer)
@dataclass
class Foo:
    ...
```

> **Note:** `@serde` actually works without @dataclass decorator, because it detects and add @dataclass to the declared class automatically. However, mypy will produce `Too many arguments` or `Unexpected keyword argument` error. This is due to the current mypy limitation. See the following documentation for more information.
https://mypy.readthedocs.io/en/stable/additional_features.html#caveats-known-issues
>
> ```python
> @serde
> class Foo:
>     ...
> ```
>
> But if you're a PEP681 compliant type checker (e.g. pyright) user, you don't get the type error because pyserde supports [PEP681 dataclass_transform](https://peps.python.org/pep-0681/)


## `@serialize`/`@deserialize`

`@serialize` and `@deserialize` are used by `@serde` under the hood. It's recommended to use the decorators in such cases:
* You only need either serialization or deserialization functionality
* You want to have different class attributes

```python
@deserialize(rename_all = "snakecase")
@serialize(rename_all = "camelcase")
class Foo:
    ...
```

## `@dataclass` without `@serde`

pyserde can (de)serialize dataclasses without `@serde` since v0.9.9. This feature is convenient when you want to use classes declared in external libraries or a type checker doesn't work with `@serde` decorator. See [this example](https://github.com/yukinarit/pyserde/blob/main/examples/plain_dataclass.py).

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