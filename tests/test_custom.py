"""
Tests for custom serializer/deserializer.
"""

from datetime import datetime
from typing import Optional, Any, Union
from plum import dispatch

import pytest

from serde import (
    SerdeError,
    add_deserializer,
    add_serializer,
    field,
    from_dict,
    from_tuple,
    serde,
    to_dict,
    to_tuple,
    ClassSerializer,
    ClassDeserializer,
)
from serde.core import GLOBAL_CLASS_DESERIALIZER, GLOBAL_CLASS_SERIALIZER
from serde.json import from_json, to_json


def test_custom_field_serializer() -> None:
    @serde
    class Foo:
        a: datetime
        b: datetime = field(
            serializer=lambda x: x.strftime("%d/%m/%y"),
            deserializer=lambda x: datetime.strptime(x, "%d/%m/%y"),
        )
        c: Optional[datetime] = field(
            serializer=lambda x: x.strftime("%d/%m/%y") if x else None,
            deserializer=lambda x: datetime.strptime(x, "%d/%m/%y") if x else None,
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt, None)

    assert to_json(f) == '{"a":"2021-01-01T00:00:00","b":"01/01/21","c":null}'
    assert f == from_json(Foo, to_json(f))

    assert to_tuple(f) == (datetime(2021, 1, 1, 0, 0), "01/01/21", None)
    assert f == from_tuple(Foo, to_tuple(f))


def test_raise_error() -> None:
    def raise_exception(_: Any) -> None:
        raise Exception()

    @serde
    class Foo:
        i: int = field(serializer=raise_exception, deserializer=raise_exception)

    f = Foo(10)
    with pytest.raises(SerdeError):
        to_json(f)

    with pytest.raises(SerdeError):
        from_json(Foo, '{"i": 10}')


def test_wrong_signature() -> None:
    @serde
    class Foo:
        i: int = field(serializer=lambda: "10", deserializer=lambda: 10)

    f = Foo(10)
    with pytest.raises(SerdeError):
        to_json(f)

    with pytest.raises(SerdeError):
        from_json(Foo, '{"i": 10}')


def test_custom_class_serializer() -> None:
    class MySerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: datetime) -> str:
            return value.strftime("%d/%m/%y")

    class MyDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[datetime], value: Any) -> datetime:
            return datetime.strptime(value, "%d/%m/%y")

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Bar:
        e: datetime
        f: list[datetime]

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Foo:
        a: datetime
        b: list[datetime]
        c: dict[str, datetime]
        d: Bar

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, [dt], {"k": dt}, Bar(dt, [dt]))

    s = (
        '{"a":"01/01/21","b":["01/01/21"],"c":{"k":"01/01/21"},'
        '"d":{"e":"01/01/21","f":["01/01/21"]}}'
    )
    assert s == to_json(f)
    assert f == from_json(Foo, s)

    t = ("01/01/21", ["01/01/21"], {"k": "01/01/21"}, ("01/01/21", ["01/01/21"]))
    assert t == to_tuple(f)
    assert f == from_tuple(Foo, t)


def test_custom_class_serializer_dataclass() -> None:
    @serde
    class Bar:
        v: int

    class MySerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: Bar) -> str:
            return str(value.v)

    class MyDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[Bar], value: Any) -> Bar:
            return Bar(int(value))

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Foo:
        bar: Bar

    f = Foo(Bar(10))

    s = '{"bar":"10"}'
    assert s == to_json(f)
    assert f == from_json(Foo, s)


def test_global_class_serializer_top_level() -> None:
    # A serializer/deserializer registered globally via add_serializer/add_deserializer
    # must also apply when the custom type is passed directly to to_dict/from_dict, not
    # only when nested inside a dataclass. https://github.com/yukinarit/pyserde/issues/514
    class Point:
        def __init__(self, x: int, y: int) -> None:
            self.x = x
            self.y = y

        def __eq__(self, other: object) -> bool:
            return isinstance(other, Point) and self.x == other.x and self.y == other.y

    class PointSerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: Point) -> dict[str, Any]:
            return {"x": value.x, "y": value.y}

    class PointDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[Point], value: dict[str, Any]) -> Point:
            return Point(value["x"], value["y"])

    ser_snapshot = list(GLOBAL_CLASS_SERIALIZER)
    de_snapshot = list(GLOBAL_CLASS_DESERIALIZER)
    add_serializer(PointSerializer())
    add_deserializer(PointDeserializer())
    try:

        @serde
        class Wrapper:
            p: Point

        # Nested has always worked; keep it as the reference behaviour.
        assert to_dict(Wrapper(Point(1, 2))) == {"p": {"x": 1, "y": 2}}

        # Top-level used to skip the global serializer and return the raw object.
        assert to_dict(Point(1, 2)) == {"x": 1, "y": 2}
        assert to_tuple(Point(1, 2)) == {"x": 1, "y": 2}

        # Deserialization is symmetric and must round-trip from the top level.
        assert from_dict(Point, {"x": 1, "y": 2}) == Point(1, 2)
    finally:
        GLOBAL_CLASS_SERIALIZER[:] = ser_snapshot
        GLOBAL_CLASS_DESERIALIZER[:] = de_snapshot


def test_global_class_serializer_top_level_no_match() -> None:
    # When a global serializer is registered but does not handle the top-level
    # type, the lookup must fall through to the normal dataclass path rather
    # than hijacking it. https://github.com/yukinarit/pyserde/issues/514
    class Point:
        def __init__(self, x: int, y: int) -> None:
            self.x = x
            self.y = y

    class PointSerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: Point) -> dict[str, Any]:
            return {"x": value.x, "y": value.y}

    class PointDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[Point], value: dict[str, Any]) -> Point:
            return Point(value["x"], value["y"])

    ser_snapshot = list(GLOBAL_CLASS_SERIALIZER)
    de_snapshot = list(GLOBAL_CLASS_DESERIALIZER)
    add_serializer(PointSerializer())
    add_deserializer(PointDeserializer())
    try:

        @serde
        class Other:
            a: int

        # The registry is non-empty, but no entry matches ``Other``; the value
        # must be handled by the regular dataclass (de)serialization.
        assert to_dict(Other(1)) == {"a": 1}
        assert from_dict(Other, {"a": 1}) == Other(1)
    finally:
        GLOBAL_CLASS_SERIALIZER[:] = ser_snapshot
        GLOBAL_CLASS_DESERIALIZER[:] = de_snapshot


def test_custom_serializer_with_field_attributes() -> None:
    class MySerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: datetime) -> str:
            return value.strftime("%d/%m/%y")

    class MyDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[datetime], value: Any) -> datetime:
            return datetime.strptime(value, "%d/%m/%y")

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Foo:
        # TODO This does not work as expected
        # a: Optional[datetime] = field(
        #    serializer=lambda x: x.strftime("%d/%m/%y"),
        #    deserializer=lambda x: datetime.strptime(x, "%d/%m/%y"),
        #    skip=True,
        # )
        b: Optional[datetime] = field(skip_if_false=True)
        c: Optional[datetime] = field(skip_if_false=True)

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, None)
    s = '{"b":"01/01/21"}'
    assert s == to_json(f)
    assert f == from_json(Foo, s)


def test_custom_serializer_with_class_attributes() -> None:
    class MySerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: datetime) -> str:
            return value.strftime("%d/%m/%y")

    class MyDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[datetime], value: Any) -> datetime:
            return datetime.strptime(value, "%d/%m/%y")

    @serde(
        class_serializer=MySerializer(),
        class_deserializer=MyDeserializer(),
        rename_all="capitalcase",
    )
    class Foo:
        a: datetime
        b: datetime = field(
            serializer=lambda x: x.strftime("%d/%m/%y"),
            deserializer=lambda x: datetime.strptime(x, "%d/%m/%y"),
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt)
    s = '{"A":"01/01/21","B":"01/01/21"}'
    assert s == to_json(f)
    assert f == from_json(Foo, s)


def test_field_serialize_override_class_serializer() -> None:
    class MySerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: datetime) -> str:
            return value.strftime("%d/%m/%y")

    class MyDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[datetime], value: Any) -> datetime:
            return datetime.strptime(value, "%d/%m/%y")

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Foo:
        a: int
        b: datetime
        c: datetime = field(
            serializer=lambda x: x.strftime("%y.%m.%d"),
            deserializer=lambda x: datetime.strptime(x, "%y.%m.%d"),
        )

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt)

    s = '{"a":10,"b":"01/01/21","c":"21.01.01"}'
    assert s == to_json(f)
    assert f == from_json(Foo, s)

    t = (10, "01/01/21", "21.01.01")
    assert t == to_tuple(f)
    assert f == from_tuple(Foo, t)


def test_custom_serializer_union() -> None:
    class MySerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: datetime) -> str:
            return value.strftime("%d/%m/%y")

    class MyDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[datetime], value: Any) -> datetime:
            return datetime.strptime(value, "%d/%m/%y")

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Bar:
        v: datetime

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Baz:
        v: datetime

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Foo:
        v: Union[Bar, Baz]

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(Baz(dt))
    s = '{"v":{"Baz":{"v":"01/01/21"}}}'
    assert s == to_json(f)
    assert f == from_json(Foo, s)


def test_custom_class_serializer_optional() -> None:
    class MySerializer(ClassSerializer):
        @dispatch
        def serialize(self, value: datetime) -> str:
            return value.strftime("%d/%m/%y")

    class MyDeserializer(ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[datetime], value: Any) -> datetime:
            return datetime.strptime(value, "%d/%m/%y")

    @serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
    class Foo:
        a: datetime
        b: Optional[datetime]
        c: Optional[datetime]

    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt, None)

    s = '{"a":"01/01/21","b":"01/01/21","c":null}'
    assert s == to_json(f)
    assert f == from_json(Foo, s)
