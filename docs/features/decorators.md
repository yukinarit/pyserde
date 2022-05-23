# Decorators

## `@serde`

@serde is a shortcut of @serialize and @deserialize decorators. This code
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
>
> ```python
> @serde
> class Foo:
>     ...
> ```


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
