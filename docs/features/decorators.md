# Decorators

## `@serde`

@serde is a shortcut of @serialize and @deserialize decorators. This code
```python
@serde
class Foo:
    ...
```

is equivalent to the following code.

```python
@deserialize
@serialize
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
class Foo:
    ...
```

* If you want to have extra attributes to the dataclass decorator, you can have both `@dataclass` and `@serde` decorators

```python
@serde
@dataclass(unsafe_hash=True)
class Foo:
    ...
```

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
