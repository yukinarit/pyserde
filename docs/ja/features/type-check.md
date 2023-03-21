# Type Checking

This is one of the most awaited features. `pyserde` v0.9 adds the experimental type checkers. As this feature is still experimental, the type checking is not perfect. Also, [@tbsexton](https://github.com/tbsexton) is looking into [more beautiful solution](https://github.com/yukinarit/pyserde/issues/237#issuecomment-1191714102), the entire backend of type checker may be replaced by [beartype](https://github.com/beartype/beartype) in the future.

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

> **NOTE:** Since pyserde is a serialization framework, it provides type checks or coercing only during (de)serialization. For example, pyserde doesn't complain even if incompatible value is assigned in the object below.
>
> ```python
> @serde(type_check=Strict)
> @dataclass
> class Foo
>     s: str
>
> f = Foo(100) # pyserde doesn't raise an error
> ```
>
> If you want to detect runtime type errors, I recommend to use [beartype](https://github.com/beartype/beartype).
> ```python
> @beartype
> @serde(type_check=Strict)
> @dataclass
> class Foo
>     s: str
>
> f = Foo(100) # beartype raises an error
> ```
