# Introduction

`pyserde` is a simple yet powerful serialization library on top of [dataclasses](https://docs.python.org/3/library/dataclasses.html). Simply adding pyserde's `@serde` decorator makes your class (de)serializable from/to many data formats.

```python
@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool
```

You can serialize `Foo` object into JSON.

```python
>>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
'{"i":10,"s":"foo","f":100.0,"b":true}'
```

You can deserialize JSON into `Foo` object.
```python
>>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
Foo(i=10, s='foo', f=100.0, b=True)
```
