"""
Tests for custom serializer/deserializer.
"""

from datetime import datetime
from typing import Any, Optional, Union

import pytest

from serde import (
    SerdeSkip,
    default_deserializer,
    default_serializer,
    field,
    from_tuple,
    serde,
    to_tuple,
    SerdeError,
)
from serde.json import from_json, to_json


def test_legacy_custom_class_serializer() -> None:
    def serializer(cls: Any, o: Any) -> Any:
        if cls is datetime:
            return o.strftime("%d/%m/%y")
        else:
            raise SerdeSkip()

    def deserializer(cls: Any, o: Any) -> Any:
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
        f: list[int] = field(default_factory=list)
        g: set[int] = field(default_factory=set)

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt, f=[1, 2, 3], g={4, 5, 6})

    assert (
        to_json(f)
        == '{"a":10,"b":"01/01/21","c":"01/01/21","d":null,"e":10,"f":[1,2,3],"g":[4,5,6]}'
    )
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (10, "01/01/21", "01/01/21", None, 10, [1, 2, 3], {4, 5, 6})
    assert f == from_tuple(Foo, to_tuple(f))

    def fallback(_: Any, __: Any) -> Any:
        raise SerdeSkip()

    @serde(serializer=fallback, deserializer=fallback)
    class Foo2:
        a: Optional[str]
        b: str

    f2 = Foo2("foo", "bar")
    assert to_json(f2) == '{"a":"foo","b":"bar"}'
    assert f2 == from_json(Foo2, '{"a":"foo","b":"bar"}')
    assert Foo2(None, "bar") == from_json(Foo2, '{"b":"bar"}')
    with pytest.raises(SerdeError):
        assert Foo2(None, "bar") == from_json(Foo2, "{}")
    with pytest.raises(SerdeError):
        assert Foo2("foo", "bar") == from_json(Foo2, '{"a": "foo"}')


def test_field_serialize_override_legacy_class_serializer() -> None:
    def serializer(cls: Any, o: Any) -> Any:
        if cls is datetime:
            return o.strftime("%d/%m/%y")
        else:
            raise SerdeSkip()

    def deserializer(cls: Any, o: Any) -> Any:
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


def test_override_by_default_serializer() -> None:
    def serializer(cls: Any, o: Any) -> Any:
        if cls is datetime:
            return o.strftime("%d/%m/%y")
        else:
            raise SerdeSkip()

    def deserializer(cls: Any, o: Any) -> Any:
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
