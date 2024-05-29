# Union Representation

`pyserde`>=0.7 offers attributes to control how Union is (de)serialized. This concept is the very same as the one in [serde-rs](https://serde.rs/enum-representations.html). Note these representations only apply to the dataclass, non dataclass objects are (de)serialized with `Untagged` always.

## `Untagged`

This is the default Union representation for pyserde<0.7. Given these dataclasses,

```python
@serde
class Bar:
    b: int

@serde
class Baz:
    b: int

@serde(tagging=Untagged)
class Foo:
    a: Union[Bar, Baz]
```

Note that `Bar` and `Baz` have the same field name and type. If you serialize `Foo(Baz(10))` into dict, you get `{"a": {"b": 10}}`. But if you deserialize `{"a": {"b": 10}}`, you get `Foo(Bar(10))` instead of `Foo(Baz(10))`. This means pyserde **can't correctly (de)serialize dataclasses of Union with `Untagged`**. This is why pyserde offers other kinds of union representation options.

## `ExternalTagging`

This is the default Union representation since 0.7. A class declaration with `ExternalTagging` looks like below. If you serialize `Foo(Baz(10))` into dict, you get `{"a": {"Baz": {"b": 10}}}` and you can deserialize it back to `Foo(Baz(10))`. 

```python
@serde(tagging=ExternalTagging)
class Foo:
    a: Union[Bar, Baz]
```

> **NOTE:** Non dataclass objects are alreays (de)serialized with `Untagged` regardless of `tagging` attribute because there is no information which can be used for tag. The drawback of `Untagged` is pyserde can't correctly deserialize certain types. For example, `Foo({1, 2, 3})` of below class is serialized into `{"a": [1, 2, 3]}`, but you get `Foo([1, 2, 3])` by deserializing.
>
> ```python
> @serde(tagging=ExternalTagging)
> class Foo:
>    a: Union[list[int], set[int]]
> ```

## `InternalTagging`

A class declaration with `InternalTagging` looks like below. If you serialize `Foo(Baz(10))` into dict, you will get `{"a": {"type": "Baz", "b": 10}}` and you can deserialize it back to `Foo(Baz(10))`. `type` tag is encoded inside the `Baz`'s dictionary.

```python
@serde(tagging=InternalTagging("type"))
class Foo:
    a: Union[Bar, Baz]
```

## `AdjacentTagging`

A class declaration with `AdjacentTagging` looks like below. If you serialize `Foo(Baz(10))` into dict, you will get `{"a": {"type": "Baz", "content": {"b": 10}}}` and you can deserialize it back to `Foo(Baz(10))`. `type` tag is encoded inside `Baz`'s dictionary and `Baz`s fields are encoded inside `content`.

```python
@serde(tagging=AdjacentTagging("type", "content"))
class Foo:
    a: Union[Bar, Baz]
```

## (de)serializing Union types directly

New in v0.12.0.

Passing Union types directly in (de)serialize APIs (e.g. to_json, from_json) was partially supported prior to v0.12, but the union type was always treated as untagged. Users had no way to change the union tagging. The following example code wasn't able to correctly deserialize into `Bar` due to untagged.

```python
@serde
class Foo:
    a: int

@serde
class Bar:
    a: int

bar = Bar(10)
s = to_json(bar)
print(s)
# prints {"a": 10}
print(from_json(Union[Foo, Bar], s))
# prints Foo(10)
```

Since v0.12.0, pyserde can handle union that's passed in (de)serialize APIs a bit nicely. The union type is treated as externally tagged as that is the default tagging in pyserde. So the above example can correctly (de)serialize as `Bar`.

```python
@serde
class Foo:
    a: int

@serde
class Bar:
    a: int

bar = Bar(10)
s = to_json(bar, cls=Union[Foo, Bar])
print(s)
# prints {"Bar" {"a": 10}}
print(from_json(Union[Foo, Bar], s))
# prints Bar(10)
```

Also you can change the tagging using `serde.InternalTagging`, `serde.AdjacentTagging` and `serde.Untagged`.

Now try to change the tagging for the above example. You need to pass a new argument `cls` in `to_json`. Also union class must be wrapped in either `InternalTagging`, `AdjacentTaging` or `Untagged` with required parameters.

* InternalTagging
    ```python
    from serde import InternalTagging

    s = to_json(bar, cls=InternalTagging("type", Union[Foo, Bar]))
    print(s)
    # prints {"type": "Bar", "a": 10}
    print(from_json(InternalTagging("type", Union[Foo, Bar]), s))
    # prints Bar(10)
    ```
* AdjacentTagging
    ```python
    from serde import AdjacentTagging

    s = to_json(bar, cls=AdjacentTagging("type", "content", Union[Foo, Bar]))
    print(s)
    # prints {"type": "Bar", "content": {"a": 10}}
    print(from_json(AdjacentTagging("type", "content", Union[Foo, Bar]), s))
    # prints Bar(10)
    ```
* Untagged
    ```python
    from serde import Untagged

    s = to_json(bar, cls=Untagged(Union[Foo, Bar]))
    print(s)
    # prints {"a": 10}
    print(from_json(Untagged(Union[Foo, Bar]), s))
    # prints Foo(10)
    ```
