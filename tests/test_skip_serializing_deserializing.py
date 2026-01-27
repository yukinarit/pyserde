import dataclasses

import pytest

import serde


def test_skip_serializing_only() -> None:
    @serde.serde
    class Foo:
        a: int
        secret: str = serde.field(skip_serializing=True)

    f = Foo(1, "top")
    assert serde.to_dict(f) == {"a": 1}

    restored = serde.from_dict(Foo, {"a": 1, "secret": "reveal"})
    assert restored.a == 1
    assert restored.secret == "reveal"


def test_skip_deserializing_only_defaults_used() -> None:
    @serde.serde
    class Foo:
        a: int
        cached: int = serde.field(default=10, skip_deserializing=True)

    restored = serde.from_dict(Foo, {"a": 1, "cached": 99})
    assert dataclasses.asdict(restored) == {"a": 1, "cached": 10}
    assert serde.to_dict(restored) == {"a": 1, "cached": 10}


def test_skip_both_behaves_like_skip() -> None:
    @serde.serde
    class Foo:
        a: int
        temp: int = serde.field(default=5, skip_serializing=True, skip_deserializing=True)

    f = Foo(1, 7)
    assert serde.to_dict(f) == {"a": 1}

    restored = serde.from_dict(Foo, {"a": 1, "temp": 999})
    assert restored.temp == 5


def test_deny_unknown_fields_allows_skip_deserializing() -> None:
    @serde.serde(deny_unknown_fields=True)
    class Foo:
        a: int
        shadow: int = serde.field(default=0, skip_deserializing=True)

    restored = serde.from_dict(Foo, {"a": 10, "shadow": 123})
    assert restored.a == 10
    assert restored.shadow == 0


def test_tuple_serialization_and_deserialization() -> None:
    @serde.serde
    class Foo:
        a: int
        b: int = serde.field(default=2, skip_serializing=True)

    assert serde.to_tuple(Foo(1, 3)) == (1,)

    @serde.serde
    class Bar:
        a: int
        b: int = serde.field(default=5, skip_deserializing=True)

    assert serde.to_tuple(Bar(1, 7)) == (1, 7)
    assert serde.from_tuple(Bar, (1,)) == Bar(1, 5)


def test_skip_deserializing_requires_default() -> None:
    with pytest.raises(serde.SerdeError):

        @serde.serde
        class Foo:
            a: int = serde.field(skip_deserializing=True)
