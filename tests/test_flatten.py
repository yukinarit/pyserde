"""
Tests for flatten attribute.
"""

from typing import Any, Optional

import pytest

from serde import field, from_dict, serde, SerdeError
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
