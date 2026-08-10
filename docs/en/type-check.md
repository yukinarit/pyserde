# Type Checking

pyserde offers runtime type checking since v0.9. It was completely reworked at v0.14 using [beartype](https://github.com/beartype/beartype) and it became more sophisticated and reliable. It is highly recommended to enable type checking always as it helps writing type-safe and robust programs.

If you need to accept untrusted input, prefer `strict` or `coerce` so invalid data fails early.

## `strict`

Strict type checking is to check every field value against the declared type during (de)serialization and object construction. This is the default type check mode since v0.14. What will happen with this mode is if you declare a class with `@serde` decorator without any class attributes, `@serde(type_check=strict)` is assumed and strict type checking is enabled.

```python
@serde
class Foo:
    s: str
```

If you call `Foo` with wrong type of object,
```python
foo = Foo(10)
```

you get an error
```python
beartype.roar.BeartypeCallHintParamViolation: Method __main__.Foo.__init__() parameter s=10 violates type hint <class 'str'>, as int 10 not instance of str.
```

!!! note
    beartype exception instead of SerdeError is raised from constructor because beartype does not provide post validation hook as of Feb. 2024.

similarly, if you call (de)serialize APIs with wrong type of object,

```python
print(to_json(foo))
```

again you get an error

```python
serde.compat.SerdeError: Method __main__.Foo.__init__() parameter s=10 violates type hint <class 'str'>, as int 10 not instance of str.
```

!!! note "Caveats regarding type checks by beartype"
    1. beartype can not validate on mutated properties

        The following code mutates the property "s" at the bottom. beartype can not detect this case.
        ```python
        @serde
        class Foo:
            s: str

        f = Foo("foo")
        f.s = 100
        ```

    2. beartype can not validate every one of elements in containers. This is not a bug. This is desgin principle of beartype. See [Does beartype actually do anything?](https://beartype.readthedocs.io/en/latest/faq/#faq-o1).

## `coerce`

Type coercing automatically converts a value into the declared type during (de)serialization. If the value is incompatible e.g. value is "foo" and type is int, pyserde raises an `SerdeError`.

```python
@serde(type_check=coerce)
class Foo:
    s: str

foo = Foo(10)
# pyserde automatically coerce the int value 10 into "10".
# {"s": "10"} will be printed.
print(to_json(foo))
```

### Custom coercion rules

By default, `coerce` converts a primitive value by calling its declared type, as in `int(value)`.
To validate values or use a different conversion, pass a coercer function to
`coerce(coercer=...)`. The function receives:

- `owner`: the decorated class name, such as `"Config"`, or `None` when unavailable
- `field`: the field name, such as `"count"`
- `target`: the declared primitive type
- `value`: the value to convert

The function must return the converted value. If it raises an exception, pyserde wraps that
exception in `SerdeError`.

The following function accepts only integer values for `int` fields. It includes the field location
in the error message and converts all other primitive types normally:

```python
from typing import Any
from serde import coerce, from_dict, serde


def integer_only(
    owner: str | None, field: str, target: type[Any], value: Any
) -> Any:
    if target is int:
        if isinstance(value, bool) or not isinstance(value, int):
            location = f"{owner}.{field}" if owner else field
            raise TypeError(f"{location} must be an integer")
    return target(value)


@serde(type_check=coerce(coercer=integer_only))
class Config:
    count: int


from_dict(Config, {"count": 1})       # Config(count=1)
from_dict(Config, {"count": 1.5})     # raises SerdeError mentioning Config.count
```

pyserde calls the function for primitive fields during both serialization and deserialization,
including primitive values inside containers and `Optional` fields. Enums and `Literal` values are
not passed to the function, nor is the function used to select a `Union` branch. Field serializers
and deserializers handle their corresponding direction without invoking it. The `field` argument is
`"v"` for list items and mapping values, and `"k"` for mapping keys.

The function is configured per class. Fields in a nested dataclass are therefore handled according
to that dataclass's own `type_check` setting.

## `disabled`

This is the default behavior until pyserde v0.8.3 and v0.9.x. No type coercion or checks are run. Even if a user puts a wrong value, pyserde doesn't complain anything.

```python
@serde
class Foo:
    s: str

foo = Foo(10)
# pyserde doesn't complain anything. {"s": 10} will be printed.
print(to_json(foo))
```
