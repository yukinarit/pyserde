"""
Tests for flatten attribute.
"""

from typing import Any, Optional

import pytest

from serde import field, serde, SerdeError
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
