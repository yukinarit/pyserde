"""
Tests for flatten attribute.
"""

from typing import Dict, List

import pytest

from serde import field, serde
from serde.json import from_json, to_json

from .common import all_formats


def test_flatten_simple():
    @serde
    class Bar:
        c: float
        d: bool

    @serde
    class Foo:
        a: int
        b: str
        bar: Bar = field(flatten=True)

    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True))
    s = '{"a": 10, "b": "foo", "c": 100.0, "d": true}'
    assert to_json(f) == s
    assert from_json(Foo, s) == f


@pytest.mark.parametrize('se,de', all_formats)
def test_flatten(se, de):
    @serde
    class Baz:
        e: List[int]
        f: Dict[str, str]

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

    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True, baz=Baz([1, 2], {"a": 10})))
    assert de(Foo, se(f)) == f
