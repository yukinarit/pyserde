"""
Tests for custom serializer/deserializer.
"""
from datetime import datetime
from typing import Optional, Union

import pytest

from serde import SerdeError, SerdeSkip, default_deserializer, default_serializer, field, from_tuple, serde, to_tuple
from serde.json import from_json, to_json


def test_custom_field_serializer():
    @serde
    class Foo:
        a: datetime
        b: datetime = field(
            serializer=lambda x: x.strftime('%d/%m/%y'), deserializer=lambda x: datetime.strptime(x, '%d/%m/%y')
        )
        c: Optional[datetime] = field(
            serializer=lambda x: x.strftime('%d/%m/%y') if x else None,
            deserializer=lambda x: datetime.strptime(x, '%d/%m/%y') if x else None,
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt, None)

    assert to_json(f) == '{"a": "2021-01-01T00:00:00", "b": "01/01/21", "c": null}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (datetime(2021, 1, 1, 0, 0), '01/01/21', None)
    assert f == from_tuple(Foo, to_tuple(f))


def test_raise_error():
    def raise_exception(_):
        raise Exception()

    @serde
    class Foo:
        i: int = field(serializer=raise_exception, deserializer=raise_exception)

    f = Foo(10)
    with pytest.raises(Exception):
        to_json(f)

    with pytest.raises(Exception):
        from_json(Foo, '{"i": 10}')


def test_wrong_signature():
    @serde
    class Foo:
        i: int = field(serializer=lambda: '10', deserializer=lambda: 10)

    f = Foo(10)
    with pytest.raises(SerdeError):
        to_json(f)

    with pytest.raises(SerdeError):
        from_json(Foo, '{"i": 10}')


def test_custom_class_serializer():
    def serializer(cls, o):
        if cls is datetime:
            return o.strftime('%d/%m/%y')
        else:
            raise SerdeSkip()

    def deserializer(cls, o):
        if cls is datetime:
            return datetime.strptime(o, '%d/%m/%y')
        else:
            raise SerdeSkip()

    @serde(serializer=serializer, deserializer=deserializer)
    class Foo:
        a: int
        b: datetime
        c: datetime
        d: Optional[str] = None
        e: Union[str, int] = 10

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"a": 10, "b": "01/01/21", "c": "01/01/21", "d": null, "e": 10}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, '01/01/21', '01/01/21', None, 10)
    assert f == from_tuple(Foo, to_tuple(f))

    def fallback(_, __):
        raise SerdeSkip()

    @serde(serializer=fallback, deserializer=fallback)
    class Foo:
        a: Optional[str]
        b: str

    f = Foo("foo", "bar")
    assert to_json(f) == '{"a": "foo", "b": "bar"}'
    assert f == from_json(Foo, '{"a": "foo", "b": "bar"}')
    assert Foo(None, "bar") == from_json(Foo, '{"b": "bar"}')
    with pytest.raises(Exception):
        assert Foo(None, "bar") == from_json(Foo, '{}')
    with pytest.raises(Exception):
        assert Foo("foo", "bar") == from_json(Foo, '{"a": "foo"}')


def test_field_serialize_override_class_serializer():
    def serializer(cls, o):
        if cls is datetime:
            return o.strftime('%d/%m/%y')
        else:
            raise SerdeSkip()

    def deserializer(cls, o):
        if cls is datetime:
            return datetime.strptime(o, '%d/%m/%y')
        else:
            raise SerdeSkip()

    @serde(serializer=serializer, deserializer=deserializer)
    class Foo:
        a: int
        b: datetime
        c: datetime = field(
            serializer=lambda x: x.strftime('%y.%m.%d'), deserializer=lambda x: datetime.strptime(x, '%y.%m.%d')
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"a": 10, "b": "01/01/21", "c": "21.01.01"}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, '01/01/21', '21.01.01')
    assert f == from_tuple(Foo, to_tuple(f))


def test_override_by_default_serializer():
    def serializer(cls, o):
        if cls is datetime:
            return o.strftime('%d/%m/%y')
        else:
            raise SerdeSkip()

    def deserializer(cls, o):
        if cls is datetime:
            return datetime.strptime(o, '%d/%m/%y')
        else:
            raise SerdeSkip()

    @serde(serializer=serializer, deserializer=deserializer)
    class Foo:
        a: int
        b: datetime
        c: datetime = field(serializer=default_serializer, deserializer=default_deserializer)

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"a": 10, "b": "01/01/21", "c": "2021-01-01T00:00:00"}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, '01/01/21', datetime(2021, 1, 1, 0, 0))
    assert f == from_tuple(Foo, to_tuple(f))
