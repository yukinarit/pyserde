"""
Tests for flatten attribute.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, Optional, TypeVar, Union

import pytest

from serde import field, from_dict, serde, SerdeError, to_dict
from serde.json import from_json, to_json

from .common import all_formats


def test_flatten_simple() -> None:
    @serde
    class Bar:
        c: float
        d: bool

    @serde
    class Foo:
        a: int
        b: str
        bar: Bar = field(flatten=True)

    f = Foo(a=10, b="foo", bar=Bar(c=100.0, d=True))
    s = '{"a":10,"b":"foo","c":100.0,"d":true}'
    assert to_json(f) == s
    assert from_json(Foo, s) == f


def test_flatten_custom_field_serializer() -> None:
    # A custom field serializer on a flattened dataclass's field must be in
    # scope of the enclosing class's generated serializer (#453).
    @serde
    class Child:
        value: int = field(serializer=str)

    @serde
    class Parent:
        child: Child = field(flatten=True)

    assert to_json(Parent(child=Child(value=3))) == '{"value":"3"}'

    # also works through a nested flatten
    @serde
    class GrandParent:
        parent: Parent = field(flatten=True)

    assert to_json(GrandParent(parent=Parent(child=Child(value=7)))) == '{"value":"7"}'


@pytest.mark.parametrize("se,de", all_formats)
def test_flatten(se: Any, de: Any) -> None:
    @serde
    class Baz:
        e: list[int]
        f: dict[str, str]

    @serde
    class Bar:
        c: float
        d: bool
        baz: Baz = field(flatten=True)

    @serde
    class Foo:
        a: int
        b: str
        bar: Bar = field(flatten=True)

    f = Foo(a=10, b="foo", bar=Bar(c=100.0, d=True, baz=Baz([1, 2], {"a": "10"})))
    assert de(Foo, se(f)) == f


@pytest.mark.parametrize("se,de", all_formats)
def test_flatten_optional(se: Any, de: Any) -> None:
    @serde
    class Bar:
        c: float
        d: bool

    @serde
    class Foo:
        a: int
        b: str
        bar: Optional[Bar] = field(flatten=True)

    f = Foo(a=10, b="foo", bar=Bar(c=100.0, d=True))
    assert de(Foo, se(f)) == f


@pytest.mark.parametrize("se,de", all_formats)
def test_flatten_optional_with_default(se: Any, de: Any) -> None:
    @serde
    class Bar:
        c: float
        d: bool

    @serde
    class Foo:
        a: int
        b: str
        bar: Optional[Bar] = field(default=None, flatten=True)

    f = Foo(a=10, b="foo", bar=Bar(c=100.0, d=True))
    assert de(Foo, se(f)) == f

    assert from_dict(Foo, {"a": 10, "b": "foo"}) == Foo(a=10, b="foo", bar=None)


@pytest.mark.parametrize("se,de", all_formats)
def test_flatten_not_supported(se: Any, de: Any) -> None:
    @serde
    class Bar:
        pass

    with pytest.raises(SerdeError):

        @serde
        class Foo:
            bar: list[Bar] = field(flatten=True)


def test_flatten_default() -> None:
    @serde
    class Bar:
        c: float = field(default=0.0)
        d: bool = field(default=False)

    @serde
    class Foo:
        a: int
        b: str = field(default="foo")
        bar: Bar = field(flatten=True, default_factory=Bar)

    f = Foo(a=10, b="b", bar=Bar(c=100.0, d=True))
    assert from_json(Foo, to_json(f)) == f

    assert from_json(Foo, '{"a": 20}') == Foo(20, "foo", Bar())


def test_flatten_default_with_empty_input() -> None:
    @serde
    class Bar:
        c: float = field(default=0.0)
        d: bool = field(default=False)

    @serde
    class Foo:
        bar: Bar = field(flatten=True, default_factory=Bar)

    assert from_dict(Foo, {}) == Foo(bar=Bar())


def test_flatten_default_alias() -> None:
    @serde
    class Bar:
        a: float = field(default=0.0, alias=["aa"])  # type: ignore
        b: bool = field(default=False, alias=["bb"])  # type: ignore

    @serde
    class Foo:
        bar: Bar = field(flatten=True, default_factory=Bar)

    f = Foo(bar=Bar(100.0, True))
    assert from_json(Foo, to_json(f)) == f

    assert from_json(Foo, '{"aa": 20.0, "bb": false}') == Foo(Bar(20.0, False))


def test_flatten_dict_simple() -> None:
    """Test basic flattened dict captures extra fields."""

    @serde
    class Foo:
        a: int
        b: str
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    # Deserialization - extra fields captured
    s = '{"a": 10, "b": "foo", "c": 100.0, "d": true}'
    f = from_json(Foo, s)
    assert f.a == 10
    assert f.b == "foo"
    assert f.extra == {"c": 100.0, "d": True}

    # Serialization - extra fields merged back
    f2 = Foo(a=20, b="bar", extra={"x": 1, "y": "z"})
    s2 = to_json(f2)
    assert '"a":20' in s2
    assert '"b":"bar"' in s2
    assert '"x":1' in s2
    assert '"y":"z"' in s2


def test_flatten_dict_empty() -> None:
    """Test flattened dict when no extra fields."""

    @serde
    class Foo:
        a: int
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    s = '{"a": 10}'
    f = from_json(Foo, s)
    assert f.a == 10
    assert f.extra == {}

    # Round-trip
    assert from_json(Foo, to_json(f)) == f


def test_flatten_dict_roundtrip() -> None:
    """Test serialization/deserialization roundtrip."""

    @serde
    class Foo:
        a: int
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    original = Foo(a=10, extra={"x": 1, "y": [1, 2, 3], "z": {"nested": True}})
    s = to_json(original)
    restored = from_json(Foo, s)
    assert restored == original


def test_flatten_dict_with_dataclass() -> None:
    """Test flattened dict alongside flattened dataclass."""

    @serde
    class Inner:
        c: float
        d: bool

    @serde
    class Outer:
        a: int
        inner: Inner = field(flatten=True)
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    s = '{"a": 10, "c": 1.5, "d": true, "unknown": "value"}'
    f = from_json(Outer, s)
    assert f.a == 10
    assert f.inner.c == 1.5
    assert f.inner.d is True
    assert f.extra == {"unknown": "value"}

    # Round-trip
    assert from_json(Outer, to_json(f)) == f


def test_flatten_dict_conflict_declared_wins() -> None:
    """Test that declared fields take precedence over flattened dict during serialization."""
    import json

    @serde
    class Foo:
        a: int
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    # If extra contains 'a', the declared field 'a' should win
    f = Foo(a=10, extra={"a": 999, "b": 20})
    s = to_json(f)
    d = json.loads(s)
    assert d["a"] == 10  # Declared field wins
    assert d["b"] == 20


def test_flatten_dict_invalid_type_rejected() -> None:
    """Test that non dict[str, Any] is rejected."""
    # dict[int, str] should be rejected (key must be str)
    with pytest.raises(SerdeError):

        @serde
        class Foo1:
            extra: dict[int, str] = field(flatten=True)

    # dict[str, int] should be rejected (value must be Any)
    with pytest.raises(SerdeError):

        @serde
        class Foo2:
            extra: dict[str, int] = field(flatten=True)

    # list[str] should be rejected
    with pytest.raises(SerdeError):

        @serde
        class Foo3:
            extra: list[str] = field(flatten=True)


@pytest.mark.parametrize("se,de", all_formats)
def test_flatten_dict_all_formats(se: Any, de: Any) -> None:
    """Test flattened dict with all serialization formats."""

    @serde
    class Foo:
        a: int
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    f = Foo(a=10, extra={"b": 20, "c": "hello"})
    assert de(Foo, se(f)) == f


def test_flatten_bare_dict() -> None:
    """Test that bare dict (without type parameters) also works for flatten."""

    @serde
    class Foo:
        a: int
        extra: dict = field(flatten=True, default_factory=dict)

    # Deserialization - extra fields captured
    s = '{"a": 10, "b": "foo", "c": 100.0, "d": true}'
    f = from_json(Foo, s)
    assert f.a == 10
    assert f.extra == {"b": "foo", "c": 100.0, "d": True}

    # Serialization - extra fields merged back
    f2 = Foo(a=20, extra={"x": 1, "y": "z"})
    s2 = to_json(f2)
    assert '"a":20' in s2
    assert '"x":1' in s2
    assert '"y":"z"' in s2


def test_flatten_deny_unknown_fields_excludes_parent_fields() -> None:
    @serde(deny_unknown_fields=True)
    class Inner:
        a: int

    @serde
    class Outer:
        b: int
        inner: Inner = field(flatten=True)

    assert from_dict(Outer, {"a": 1, "b": 2}) == Outer(b=2, inner=Inner(a=1))

    with pytest.raises(SerdeError):
        from_dict(Outer, {"a": 1, "b": 2, "unknown": 3})


def test_flatten_deny_unknown_child_with_parent_extra() -> None:
    @serde(deny_unknown_fields=True)
    class Inner:
        a: int

    @serde
    class Outer:
        b: int
        inner: Inner = field(flatten=True)
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    assert from_dict(Outer, {"a": 1, "b": 2, "unknown": 3}) == Outer(
        b=2, inner=Inner(a=1), extra={"unknown": 3}
    )


def test_flatten_parent_and_child_extra_both_capture_unknowns() -> None:
    @serde
    class Inner:
        a: int
        child_extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    @serde
    class Outer:
        b: int
        inner: Inner = field(flatten=True)
        parent_extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    assert from_dict(Outer, {"a": 1, "b": 2, "unknown": 3}) == Outer(
        b=2,
        inner=Inner(a=1, child_extra={"unknown": 3}),
        parent_extra={"unknown": 3},
    )


def test_flatten_parent_and_grandchild_extra_both_capture_unknowns() -> None:
    @serde
    class Grand:
        a: int
        grand_extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    @serde
    class Inner:
        grand: Grand = field(flatten=True)

    @serde
    class Outer:
        inner: Inner = field(flatten=True)
        parent_extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    assert from_dict(Outer, {"a": 1, "unknown": 2}) == Outer(
        inner=Inner(grand=Grand(a=1, grand_extra={"unknown": 2})),
        parent_extra={"unknown": 2},
    )


def test_flatten_sibling_fields_do_not_leak_between_children() -> None:
    @serde(deny_unknown_fields=True)
    class Left:
        a: int

    @serde(deny_unknown_fields=True)
    class Right:
        b: int

    @serde
    class Outer:
        left: Left = field(flatten=True)
        right: Right = field(flatten=True)

    assert from_dict(Outer, {"a": 1, "b": 2}) == Outer(left=Left(a=1), right=Right(b=2))


@pytest.mark.parametrize("se,de", all_formats)
def test_flatten_generic(se: Any, de: Any) -> None:
    T = TypeVar("T")

    @serde
    @dataclass
    class Foo(Generic[T]):
        v: T

    @serde
    @dataclass
    class Bar(Generic[T]):
        foo: Foo[T] = field(flatten=True)

    bar = Bar[int](Foo[int](10))
    assert de(Bar[int], se(bar)) == bar


def test_flatten_generic_dict_and_type_resolution() -> None:
    T = TypeVar("T")
    U = TypeVar("U")
    V = TypeVar("V")

    @serde
    @dataclass
    class Item:
        x: int

    @serde
    @dataclass
    class Foo(Generic[T]):
        v: T

    @serde
    @dataclass
    class Bar(Generic[T]):
        foo: Foo[T] = field(flatten=True)

    bar_int = Bar[int](Foo[int](10))
    d_int = to_dict(bar_int)
    assert d_int == {"v": 10}
    assert from_dict(Bar[int], d_int) == bar_int

    bar_item = Bar[Item](Foo[Item](Item(x=42)))
    d_item = to_dict(bar_item)
    assert d_item == {"v": {"x": 42}}
    assert from_dict(Bar[Item], d_item) == bar_item

    @serde
    @dataclass
    class Inner(Generic[T, U]):
        first: T
        second: U

    @serde
    @dataclass
    class Outer(Generic[U, V]):
        tag: U
        inner: Inner[V, U] = field(flatten=True)

    outer = Outer[str, Item](tag="ok", inner=Inner[Item, str](first=Item(x=7), second="s"))
    d_outer = to_dict(outer)
    assert d_outer == {"tag": "ok", "first": {"x": 7}, "second": "s"}
    assert from_dict(Outer[str, Item], d_outer) == outer


def test_flatten_generic_nested_and_inner_types() -> None:
    T = TypeVar("T")

    class Color(Enum):
        RED = "red"

    @dataclass
    class Leaf(Generic[T]):
        v: T
        color: Color
        choice: Union[int, str]
        formatted: int = field(serializer=str)

    @serde
    @dataclass
    class Mid(Generic[T]):
        leaf: Leaf[T] = field(flatten=True)

    @serde
    @dataclass
    class Root(Generic[T]):
        name: str
        mid: Mid[T] = field(flatten=True)

    root = Root[int](
        name="r",
        mid=Mid[int](leaf=Leaf[int](v=5, color=Color.RED, choice="a", formatted=3)),
    )
    assert to_dict(root) == {
        "name": "r",
        "v": 5,
        "color": "red",
        "choice": "a",
        "formatted": "3",
    }
    assert (
        from_dict(
            Root[int],
            {"name": "r", "v": 5, "color": "red", "choice": "a", "formatted": 3},
        )
        == root
    )


def test_flatten_generic_optional_and_default() -> None:
    T = TypeVar("T")

    @serde
    @dataclass
    class Item:
        x: int

    @serde
    @dataclass
    class Foo(Generic[T]):
        v: T

    @serde
    @dataclass
    class OptBar(Generic[T]):
        a: int
        foo: Optional[Foo[T]] = field(default=None, flatten=True)

    present = OptBar[Item](a=1, foo=Foo[Item](Item(x=9)))
    assert to_dict(present) == {"a": 1, "v": {"x": 9}}
    assert from_dict(OptBar[Item], {"a": 1, "v": {"x": 9}}) == present
    assert from_dict(OptBar[Item], {"a": 1}) == OptBar[Item](a=1, foo=None)

    @serde
    @dataclass
    class DefaultFoo(Generic[T]):
        v: Optional[T] = None

    @serde
    @dataclass
    class DefaultBar(Generic[T]):
        a: int
        foo: DefaultFoo[T] = field(flatten=True, default_factory=DefaultFoo)

    assert from_dict(DefaultBar[int], {"a": 1}) == DefaultBar[int](a=1, foo=DefaultFoo(v=None))
    assert from_dict(DefaultBar[int], {"a": 1, "v": 2}) == DefaultBar[int](a=1, foo=DefaultFoo(v=2))


def test_flatten_generic_deny_unknown_fields_and_extra() -> None:
    T = TypeVar("T")

    @serde(deny_unknown_fields=True)
    @dataclass
    class Inner(Generic[T]):
        v: T

    @serde(deny_unknown_fields=True)
    @dataclass
    class StrictOuter(Generic[T]):
        a: int
        inner: Inner[T] = field(flatten=True)

    assert from_dict(StrictOuter[int], {"a": 1, "v": 2}) == StrictOuter[int](
        a=1, inner=Inner[int](v=2)
    )
    with pytest.raises(SerdeError):
        from_dict(StrictOuter[int], {"a": 1, "v": 2, "unknown": 3})

    @serde
    @dataclass
    class ExtraOuter(Generic[T]):
        a: int
        inner: Inner[T] = field(flatten=True)
        extra: dict[str, Any] = field(flatten=True, default_factory=dict)

    assert from_dict(ExtraOuter[int], {"a": 1, "v": 2, "unknown": 3}) == ExtraOuter[int](
        a=1, inner=Inner[int](v=2), extra={"unknown": 3}
    )


def test_flatten_non_dataclass_generic_rejected() -> None:
    T = TypeVar("T")

    class NotDataclass(Generic[T]):
        pass

    with pytest.raises(SerdeError):

        @serde
        class Bad(Generic[T]):
            x: NotDataclass[T] = field(flatten=True)
