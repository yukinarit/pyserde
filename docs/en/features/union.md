# Union Representation

`pyserde`>=0.7 offers attributes to control how Union is (de)serialized. This concept is the very same as the one in [serde-rs](https://serde.rs/enum-representations.html). Note these representations only apply to the dataclass, non dataclass objects are (de)serialized with `Untagged` always.

## `Untagged`

This is the default Union representation for pyserde<0.7. Given these dataclasses,

```python
@serde
@dataclass
class Bar:
    b: int

@serde
@dataclass
class Baz:
    b: int

@serde(tagging=Untagged)
@dataclass
class Foo:
    a: Union[Bar, Baz]
```

Note that `Bar` and `Baz` have the same field name and type. If you serialize `Foo(Baz(10))` into dict, you get `{"a": {"b": 10}}`. But if you deserialize `{"a": {"b": 10}}`, you get `Foo(Bar(10))` instead of `Foo(Baz(10))`. This means pyserde **can't correctly (de)serialize dataclasses of Union with `Untagged`**. This is why pyserde offers other kinds of union representation options.

## `ExternalTagging`

This is the default Union representation since 0.7. A class declaration with `ExternalTagging` looks like below. If you serialize `Foo(Baz(10))` into dict, you get `{"a": {"Baz": {"b": 10}}}` and you can deserialize it back to `Foo(Baz(10))`. 

```
@serde(tagging=ExternalTagging)
@dataclass
class Foo:
    a: Union[Bar, Baz]
```

> **NOTE:** Non dataclass objects are alreays (de)serialized with `Ungagged` regardless of `tagging` attribute because there is no information which can be used for tag. The drawback of `Untagged` is pyserde can't correctly deserialize certain types. For example, `Foo({1, 2, 3})` of below class is serialized into `{"a": [1, 2, 3]}`, but you get `Foo([1, 2, 3])` by deserializing.
>
> ```python
> @serde(tagging=ExternalTagging)
> @dataclass
> class Foo:
>    a: Union[List[int], Set[int]]
> ```

## `InternalTagging`

A class declaration with `InternalTagging` looks like below. If you serialize `Foo(Baz(10))` into dict, you will get `{"a": {"type": "Baz", "b": 10}}` and you can deserialize it back to `Foo(Baz(10))`. `type` tag is encoded inside the `Baz`'s dictionary.

```python
@serde(tagging=InternalTagging("type"))
@dataclass
class Foo:
    a: Union[Bar, Baz]
```

## `AdjacentTagging`

A class declaration with `AdjacentTagging` looks like below. If you serialize `Foo(Baz(10))` into dict, you will get `{"a": {"type": "Baz", "content": {"b": 10}}}` and you can deserialize it back to `Foo(Baz(10))`. `type` tag is encoded inside `Baz`'s dictionary and `Baz`s fields are encoded inside `content`.

```python
@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class Foo:
    a: Union[Bar, Baz]
```