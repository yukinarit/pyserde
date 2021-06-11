"""
Tests for custom serializer/deserializer.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pytest

from serde import SerdeSkip, default_deserializer, default_serializer, deserialize, from_tuple, serialize, to_tuple
from serde.json import from_json, to_json


def test_custom_field_serializer():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        dt1: datetime
        dt2: datetime = field(
            metadata={
                'serde_serializer': lambda x: x.strftime('%d/%m/%y'),
                'serde_deserializer': lambda x: datetime.strptime(x, '%d/%m/%y'),
            }
        )
        dt3: Optional[datetime] = field(
            metadata={
                'serde_serializer': lambda x: x.strftime('%d/%m/%y') if x else None,
                'serde_deserializer': lambda x: datetime.strptime(x, '%d/%m/%y') if x else None,
            }
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt, None)

    assert to_json(f) == '{"dt1": "2021-01-01T00:00:00", "dt2": "01/01/21", "dt3": null}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (datetime(2021, 1, 1, 0, 0), '01/01/21', None)
    assert f == from_tuple(Foo, to_tuple(f))


def test_raise_error():
    def raise_exception(_):
        raise Exception()

    @deserialize
    @serialize
    @dataclass
    class Foo:
        i: int = field(metadata={'serde_serializer': raise_exception, 'serde_deserializer': raise_exception})

    f = Foo(10)
    with pytest.raises(Exception):
        to_json(f)

    with pytest.raises(Exception):
        from_json(Foo, '{"i": 10}')


def test_wrong_signature():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        i: int = field(metadata={'serde_serializer': lambda: '10', 'serde_deserializer': lambda: 10})

    f = Foo(10)
    with pytest.raises(TypeError):
        to_json(f)

    with pytest.raises(TypeError):
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

    @deserialize(deserializer=deserializer)
    @serialize(serializer=serializer)
    @dataclass
    class Foo:
        i: int
        dt1: datetime
        dt2: datetime

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"i": 10, "dt1": "01/01/21", "dt2": "01/01/21"}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, '01/01/21', '01/01/21')
    assert f == from_tuple(Foo, to_tuple(f))


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

    @deserialize(deserializer=deserializer)
    @serialize(serializer=serializer)
    @dataclass
    class Foo:
        i: int
        dt1: datetime
        dt2: datetime = field(
            metadata={
                'serde_serializer': lambda x: x.strftime('%y.%m.%d'),
                'serde_deserializer': lambda x: datetime.strptime(x, '%y.%m.%d'),
            }
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"i": 10, "dt1": "01/01/21", "dt2": "21.01.01"}'
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

    @deserialize(deserializer=deserializer)
    @serialize(serializer=serializer)
    @dataclass
    class Foo:
        i: int
        dt1: datetime
        dt2: datetime = field(
            metadata={'serde_serializer': default_serializer, 'serde_deserializer': default_deserializer}
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    assert to_json(f) == '{"i": 10, "dt1": "01/01/21", "dt2": "2021-01-01T00:00:00"}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, '01/01/21', datetime(2021, 1, 1, 0, 0))
    assert f == from_tuple(Foo, to_tuple(f))
