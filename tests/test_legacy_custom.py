"""
Tests for custom serializer/deserializer.
"""
from datetime import datetime
from typing import Optional, Union
from beartype.typing import List, Set

import pytest

from serde import (
    SerdeSkip,
    default_deserializer,
    default_serializer,
    field,
    from_tuple,
    serde,
    to_tuple,
)
from serde.json import from_json, to_json


def test_legacy_custom_class_serializer():
    def serializer(cls, o):
        if cls is datetime:
            return o.strftime("%d/%m/%y")
        else:
            raise SerdeSkip()

    def deserializer(cls, o):
        if cls is datetime:
            return datetime.strptime(o, "%d/%m/%y")
        else:
            raise SerdeSkip()

    @serde(serializer=serializer, deserializer=deserializer)
    class Foo:
        a: int
        b: datetime
        c: datetime
        d: Optional[str] = None
        e: Union[str, int] = 10
        f: List[int] = field(default_factory=list)
        g: Set[int] = field(default_factory=set)

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt, f=[1, 2, 3], g={4, 5, 6})

    assert (
        to_json(f)
        == '{"a":10,"b":"01/01/21","c":"01/01/21","d":null,"e":10,"f":[1,2,3],"g":[4,5,6]}'
    )
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, "01/01/21", "01/01/21", None, 10, [1, 2, 3], {4, 5, 6})
    assert f == from_tuple(Foo, to_tuple(f))

    def fallback(_, __):
        raise SerdeSkip()

    @serde(serializer=fallback, deserializer=fallback)
    class Foo:
        a: Optional[str]
        b: str

    f = Foo("foo", "bar")
    assert to_json(f) == '{"a":"foo","b":"bar"}'
    assert f == from_json(Foo, '{"a":"foo","b":"bar"}')
    assert Foo(None, "bar") == from_json(Foo, '{"b":"bar"}')
    with pytest.raises(Exception):
        assert Foo(None, "bar") == from_json(Foo, "{}")
    with pytest.raises(Exception):
        assert Foo("foo", "bar") == from_json(Foo, '{"a": "foo"}')


def test_field_serialize_override_legacy_class_serializer():
    def serializer(cls, o):
        if cls is datetime:
            return o.strftime("%d/%m/%y")
        else:
            raise SerdeSkip()

    def deserializer(cls, o):
        if cls is datetime:
            return datetime.strptime(o, "%d/%m/%y")
        else:
            raise SerdeSkip()

    @serde(serializer=serializer, deserializer=deserializer)
    class Foo:
        a: int
        b: datetime
        c: datetime = field(
            serializer=lambda x: x.strftime("%y.%m.%d"),
            deserializer=lambda x: datetime.strptime(x, "%y.%m.%d"),
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"a":10,"b":"01/01/21","c":"21.01.01"}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, "01/01/21", "21.01.01")
    assert f == from_tuple(Foo, to_tuple(f))


def test_override_by_default_serializer():
    def serializer(cls, o):
        if cls is datetime:
            return o.strftime("%d/%m/%y")
        else:
            raise SerdeSkip()

    def deserializer(cls, o):
        if cls is datetime:
            return datetime.strptime(o, "%d/%m/%y")
        else:
            raise SerdeSkip()

    @serde(serializer=serializer, deserializer=deserializer)
    class Foo:
        a: int
        b: datetime
        c: datetime = field(serializer=default_serializer, deserializer=default_deserializer)

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"a":10,"b":"01/01/21","c":"2021-01-01T00:00:00"}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, "01/01/21", datetime(2021, 1, 1, 0, 0))
    assert f == from_tuple(Foo, to_tuple(f))
