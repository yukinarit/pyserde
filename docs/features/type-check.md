# Type Checking

This is one of the most awaited features. `pyserde` v0.9 adds the experimental type checkers. As this feature is still experimental, the type checking is not perfect. Also, [@tbsexton](https://github.com/tbsexton) is looking into more beautiful solution, the entire backend of type checker may be replaced by [beartype](https://github.com/beartype/beartype) in the future.

### `NoCheck`

This is the default behavior until pyserde v0.8.3 and v0.9.x. No type coercion or checks are run. Even if a user puts a wrong value, pyserde doesn't complain anything.

```python
@serde
@dataclass
class Foo
    s: str

foo = Foo(10)
# pyserde doesn't complain anything. {"s": 10} will be printed.
print(to_json(foo))
```

### `Coerce`

Type coercing automatically converts a value into the declared type during (de)serialization. If the value is incompatible e.g. value is "foo" and type is int, pyserde raises an `SerdeError`.

```python
@serde(type_check=Coerce)
@dataclass
class Foo
    s: str

foo = Foo(10)
# pyserde automatically coerce the int value 10 into "10".
# {"s": "10"} will be printed.
print(to_json(foo))
```

### `Strict`

Strict type checking is to check every value against the declared type during (de)serialization. We plan to make `Strict` a default type checker in the future release.

```python
@serde(type_check=Strict)
@dataclass
class Foo
    s: str

foo = Foo(10)
# pyserde checks the value 10 is instance of `str`.
# SerdeError will be raised in this case because of the type mismatch.
print(to_json(foo))
```
