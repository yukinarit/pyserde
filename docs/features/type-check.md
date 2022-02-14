# Type Checking

`pyserde` provides 3 kinds of type checks.

### `NoCheck`

This is the default behavior until pyserde v0.8.3. No type coercion or checks are applied. If a user puts a wrong value, pyserde doesn't complain anything.

```python
@serde
@dataclass
class Foo
    s: str

foo = Foo(10)
# pyserde doesn't complain anything. {"s": 10} will be printed.
print(to_json(foo, type_check=NoCheck))

```

### `Coerce`

Type coercion is not yet implemented but this will be the default behavior in pyserde v0.9.0 onward.

```python
foo = Foo(10)
# pyserde automatically coerce the int value 10 into "10".
# {"s": "10"} will be printed.
print(to_json(foo, type_check=Coerce))
```

Not yet implemented.

### `Strict`

Strict type checking is to check every value against the declared type.

```python
foo = Foo(10)
# pyserde checks the value 10 is instance of `str`.
# SerdeError will be raised in this case because of the type mismatch.
print(to_json(foo, type_check=Strict))
```
