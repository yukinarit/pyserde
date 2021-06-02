"""
Tests for custom serializer/deserializer.
"""
from dataclasses import dataclass, field
from datetime import datetime

import pytest

from serde import deserialize, serialize
from serde.json import from_json, to_json


def test_custom_field_serializer():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        dt1: datetime
        dt2: datetime = field(
            metadata={
                'serde_serialize': lambda x: x.strftime('%d/%m/%y'),
                'serde_deserialize': lambda x: datetime.strptime(x, '%d/%m/%y'),
            }
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt)

    assert to_json(f) == '{"dt1": "2021-01-01T00:00:00", "dt2": "01/01/21"}'
    assert f == from_json(Foo, to_json(f))


def test_raise_error():
    def raise_exception(_):
        raise Exception()

    @deserialize
    @serialize
    @dataclass
    class Foo:
        i: int = field(metadata={'serde_serialize': raise_exception, 'serde_deserialize': raise_exception})

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
        i: int = field(metadata={'serde_serialize': lambda: '10', 'serde_deserialize': lambda: 10})

    f = Foo(10)
    with pytest.raises(TypeError):
        to_json(f)

    with pytest.raises(TypeError):
        from_json(Foo, '{"i": 10}')
