"""
Tests for flatten attribute.
"""

from typing import Dict, List

import pytest

import serde
from serde import field
from serde.json import from_json, to_json
from serde.orjson import from_json as from_orjson
from serde.orjson import to_json as to_orjson

from .common import all_formats


def test_flatten_simple_json():
    @serde.serde
    class Bar:
        c: float
        d: bool

    @serde.serde
    class Foo:
        a: int
        b: str
        bar: Bar = field(flatten=True)

    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True))
    s = '{"a": 10, "b": "foo", "c": 100.0, "d": true}'
    assert to_json(f) == s
    assert from_json(Foo, s) == f


def test_flatten_simple_orjson():
    @serde.serde
    class Bar:
        c: float
        d: bool

    @serde.serde
    class Foo:
        a: int
        b: str
        bar: Bar = field(flatten=True)

    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True))
    s = b'{"a":10,"b":"foo","c":100.0,"d":true}'
    assert to_orjson(f, direct=False) == s
    assert from_orjson(Foo, s) == f


@pytest.mark.parametrize('se,de', all_formats)
def test_flatten(se, de):
    @serde.serde
    class Baz:
        e: List[int]
        f: Dict[str, str]

    @serde.serde
    class Bar:
        c: float
        d: bool
        baz: Baz = field(flatten=True)

    @serde.serde
    class Foo:
        a: int
        b: str
        bar: Bar = field(flatten=True)

    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True, baz=Baz([1, 2], {"a": 10})))

    se_f = se(f, direct=False) if se == serde.orjson.to_json else se(f)
    assert de(Foo, se_f) == f
