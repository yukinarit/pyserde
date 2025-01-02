# Type Checking

pyserde offers runtime type checking since v0.9. It was completely reworked at v0.14 using [beartype](https://github.com/beartype/beartype) and it became more sophisticated and reliable. It is highly recommended to enable type checking always as it helps writing type-safe and robust programs.

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

> **NOTE:** beartype exception instead of SerdeError is raised from constructor because beartype does not provide post validation hook as of Feb. 2024.

similarly, if you call (de)serialize APIs with wrong type of object,

```python
print(to_json(foo))
```

again you get an error

```python
serde.compat.SerdeError: Method __main__.Foo.__init__() parameter s=10 violates type hint <class 'str'>, as int 10 not instance of str.
```

> **NOTE:** There are several caveats regarding type checks by beartype.
>
> 1. beartype can not validate on mutated properties
>
> The following code mutates the property "s" at the bottom. beartype can not detect this case.
> ```python
> @serde
> class Foo
>     s: str
>
> f = Foo("foo")
> f.s = 100
> ```
>
> 2. beartype can not validate every one of elements in containers. This is not a bug. This is desgin principle of beartype. See [Does beartype actually do anything?](https://beartype.readthedocs.io/en/latest/faq/#faq-o1].
> ```

## `coerce`

Type coercing automatically converts a value into the declared type during (de)serialization. If the value is incompatible e.g. value is "foo" and type is int, pyserde raises an `SerdeError`.

```python
@serde(type_check=coerce)
class Foo
    s: str

foo = Foo(10)
# pyserde automatically coerce the int value 10 into "10".
# {"s": "10"} will be printed.
print(to_json(foo))
```

## `disabled`

This is the default behavior until pyserde v0.8.3 and v0.9.x. No type coercion or checks are run. Even if a user puts a wrong value, pyserde doesn't complain anything.

```python
@serde
class Foo
    s: str

foo = Foo(10)
# pyserde doesn't complain anything. {"s": 10} will be printed.
print(to_json(foo))
```
