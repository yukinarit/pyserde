"""
Tests for flatten attribute.
"""

from dataclasses import dataclass, field
from typing import Dict, List

import pytest

from serde import deserialize, serialize
from serde.json import from_json, to_json

from .common import all_formats


def test_flatten_simple():
    @deserialize
    @serialize
    @dataclass
    class Bar:
        c: float
        d: bool

    @deserialize
    @serialize
    @dataclass
    class Foo:
        a: int
        b: str
        bar: Bar = field(metadata={'serde_flatten': True})

    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True))
    s = '{"a": 10, "b": "foo", "c": 100.0, "d": true}'
    assert to_json(f) == s
    assert from_json(Foo, s) == f


@pytest.mark.parametrize('se,de', all_formats)
def test_flatten(se, de):
    @deserialize
    @serialize
    @dataclass
    class Baz:
        e: List[int]
        f: Dict[str, str]

    @deserialize
    @serialize
    @dataclass
    class Bar:
        c: float
        d: bool
        baz: Baz = field(metadata={'serde_flatten': True})

    @deserialize
    @serialize
    @dataclass
    class Foo:
        a: int
        b: str
        bar: Bar = field(metadata={'serde_flatten': True})

    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True, baz=Baz([1, 2], {"a": 10})))
    assert de(Foo, se(f)) == f
