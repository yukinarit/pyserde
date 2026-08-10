from collections import Counter
from dataclasses import dataclass
import datetime
import pathlib
from beartype.roar import BeartypeCallHintViolation
from typing import (
    Union,
    Any,
)

import pytest

import serde
import serde.json

from . import data

test_cases: list[tuple[Any, Any, bool]] = [
    (int, 10, False),
    (int, 10.0, True),
    (int, "10", True),
    (int, True, False),
    (float, 10, True),
    (float, 10.0, False),
    (float, "10", True),
    (float, True, True),
    (str, 10, True),
    (str, 10.0, True),
    (str, "10", False),
    (str, True, True),
    (bool, 10, True),
    (bool, 10.0, True),
    (bool, "10", True),
    (bool, True, False),
    (list[int], [1], False),
    (list[int], [1.0], True),
    (list[float], [1.0], False),
    (list[float], [1], True),
    (list[float], ["foo"], True),
    (list[str], ["foo"], False),
    (list[str], [True], True),
    (list[bool], [True], False),
    (list[bool], [10], True),
    (list[data.Int], [data.Int(1)], False),
    (list[data.Int], [data.Int.uncheck_new(1.0)], True),  # Runtime incompatible object
    (list[data.Int], [], False),
    (dict[str, int], {"foo": 10}, False),
    # (dict[str, int], {"foo": 10.0}, True),
    (dict[str, data.Int], {"foo": data.Int(1)}, False),
    (dict[str, data.Int], {"foo": data.Int.uncheck_new(1.0)}, True),  # Runtime incompatible object
    (set[int], {10}, False),
    (set[int], {10.0}, True),
    (set[int], [10], True),
    (tuple[int], (10,), False),
    (tuple[int], (10.0,), True),
    (tuple[int, str], (10, "foo"), False),
    (tuple[int, str], (10, 10.0), True),
    (tuple[data.Int, data.Str], (data.Int(1), data.Str("2")), False),
    (tuple[data.Int, data.Str], (data.Int(1), data.Int(2)), True),
    (tuple, (10, 10.0), False),
    (tuple[int, ...], (1, 2), False),
    (data.E, data.E.S, False),
    (data.E, data.IE.V0, True),
    (Union[int, str], 10, False),
    (Union[int, str], "foo", False),
    (Union[int, str], 10.0, True),
    (Union[int, data.Int], data.Int(10), False),
    (datetime.date, datetime.date.today(), False),
    (pathlib.Path, pathlib.Path(), False),
    (pathlib.Path, "foo", True),
]


# Those test cases have wrong runtime values against declared types.
# This is not yet testable until beartype implements O(n) type checking
# https://beartype.readthedocs.io/en/latest/api_decor/#beartype.BeartypeStrategy
default_unstable_test_cases: list[tuple[Any, Any, bool]] = [
    (list[int], [1, 1.0], True),
    (list[data.Int], [data.Int(1), data.Float(10.0)], True),
    (dict[str, int], {"foo": 10, 100: "bar"}, False),
    (tuple[int, ...], (1, 2.0), True),
]


@pytest.mark.parametrize("T,data,exc", test_cases)
def test_type_check_strict(T: Any, data: Any, exc: bool) -> None:
    @serde.serde
    class C:
        a: T  # pyright: ignore[reportInvalidTypeForm]

    if exc:
        with pytest.raises((serde.SerdeError, BeartypeCallHintViolation)):
            d = serde.to_dict(C(data))
            serde.from_dict(C, d)
    else:
        d = serde.to_dict(C(data))
        serde.from_dict(C, d)


def test_type_check_disabled_for_dataclass_without_serde() -> None:
    @dataclass
    class Foo:
        value: int

    f = Foo("100")  # type: ignore
    data = serde.json.to_json(f)
    assert f == serde.json.from_json(Foo, data)

    f = Foo("100")  # type: ignore


def test_uncoercible() -> None:
    @serde.serde(type_check=serde.coerce)
    class Foo:
        i: int

    with pytest.raises(serde.SerdeError):
        serde.to_dict(Foo("foo"))  # type: ignore

    with pytest.raises(serde.SerdeError):
        serde.from_dict(Foo, {"i": "foo"})

    with pytest.raises(serde.SerdeError):
        serde.from_dict(Foo, {"i": None})


def test_coerce() -> None:
    @serde.serde(type_check=serde.coerce)
    class Foo:
        i: int
        s: str
        f: float
        b: bool

    d = {"i": "10", "s": 100, "f": 1000, "b": "True"}
    p = serde.from_dict(Foo, d)
    assert p.i == 10
    assert p.s == "100"
    assert p.f == 1000.0
    assert p.b

    p = Foo("10", 100, 1000, "True")  # type: ignore
    d = serde.to_dict(p)
    assert d["i"] == 10
    assert d["s"] == "100"
    assert d["f"] == 1000.0
    assert d["b"]

    # Couldn't coerce
    with pytest.raises(serde.SerdeError):
        d = {"i": "foo", "s": 100, "f": "bar", "b": "True"}
        p = serde.from_dict(Foo, d)

    @serde.serde(type_check=serde.coerce)
    class Int:
        i: int

    @serde.serde(type_check=serde.coerce)
    class Str:
        s: str

    @serde.serde(type_check=serde.coerce)
    class Float:
        f: float

    @serde.serde(type_check=serde.coerce)
    class Bool:
        b: bool

    @serde.serde(type_check=serde.coerce)
    class Nested:
        i: Int
        s: Str
        f: Float
        b: Bool

    # Nested structure
    p2 = Nested(Int("10"), Str(100), Float(1000), Bool("True"))  # type: ignore
    d2: dict[str, dict[str, Any]] = serde.to_dict(p2)
    assert d2["i"]["i"] == 10
    assert d2["s"]["s"] == "100"
    assert d2["f"]["f"] == 1000.0
    assert d2["b"]["b"]

    d3 = {"i": {"i": "10"}, "s": {"s": 100}, "f": {"f": 1000}, "b": {"b": "True"}}
    p3 = serde.from_dict(Nested, d3)
    assert p3.i.i == 10
    assert p3.s.s == "100"
    assert p3.f.f == 1000.0
    assert p3.b.b

    @serde.serde(type_check=serde.coerce)
    class InnerTuple:
        # Note: `foo` needs to be longer than 1 char, to properly test
        # quote escaping
        foo: tuple[float, float]

    f = InnerTuple(foo=(1, 2))
    assert f.foo == (1.0, 2.0)


def _integer_only_coercer(
    _owner: str | None, _field_name: str, target: type[Any], value: Any
) -> Any:
    if target is int and (isinstance(value, bool) or not isinstance(value, int)):
        raise TypeError("expected an integer")
    return target(value)


def test_custom_coercer_configuration_is_isolated() -> None:
    calls: list[tuple[str | None, str, type[Any], Any]] = []

    def record_context(owner: str | None, field_name: str, target: type[Any], value: Any) -> Any:
        calls.append((owner, field_name, target, value))
        return target(value)

    default_coerce = serde.coerce()
    assert default_coerce is serde.coerce

    @serde.serde(type_check=serde.coerce(coercer=record_context))
    class CustomConfig:
        value: int

    @serde.serde(type_check=default_coerce)
    class DefaultConfig:
        value: int

    assert serde.from_dict(CustomConfig, {"value": "1"}) == CustomConfig(1)
    assert calls == [("CustomConfig", "value", int, "1")]

    calls.clear()
    assert serde.from_dict(DefaultConfig, {"value": "2"}) == DefaultConfig(2)
    assert calls == []


def test_custom_coercer_configuration_validation() -> None:
    def coercer(_owner: str | None, _field_name: str, target: type[Any], value: Any) -> Any:
        return target(value)

    with pytest.raises(TypeError, match="only supported"):
        serde.strict(coercer=coercer)
    with pytest.raises(TypeError, match="must be callable"):
        serde.coerce(coercer=42)  # type: ignore[arg-type]


def test_custom_coercer_receives_field_context() -> None:
    calls: list[tuple[str | None, str, type[Any], Any]] = []

    def record_context(owner: str | None, field_name: str, target: type[Any], value: Any) -> Any:
        calls.append((owner, field_name, target, value))
        return target(value)

    @serde.serde(type_check=serde.coerce(coercer=record_context))
    class Config:
        count: int

    assert serde.from_dict(Config, {"count": "1"}) == Config(1)
    assert calls == [("Config", "count", int, "1")]

    calls.clear()
    assert serde.to_dict(Config("2")) == {"count": 2}  # type: ignore[arg-type]
    assert calls == [("Config", "count", int, "2")]


def test_custom_coercer_receives_composite_value_context() -> None:
    calls: list[tuple[str | None, str, type[Any], Any]] = []

    def record_context(owner: str | None, field_name: str, target: type[Any], value: Any) -> Any:
        calls.append((owner, field_name, target, value))
        return target(value)

    @serde.serde(type_check=serde.coerce(coercer=record_context))
    class Payload:
        values: list[float]
        mapping: dict[int, str]

    payload = serde.from_dict(
        Payload,
        {"values": [2, 3.5], "mapping": {"5": 6}},
    )
    assert payload == Payload([2.0, 3.5], {5: "6"})
    assert Counter(calls) == Counter(
        [
            ("Payload", "v", float, 2),
            ("Payload", "v", float, 3.5),
            ("Payload", "k", int, "5"),
            ("Payload", "v", str, 6),
        ]
    )

    calls.clear()
    serialized = serde.to_dict(Payload([2, 3.5], {5: 6}))  # type: ignore[dict-item]
    assert serialized == {"values": [2.0, 3.5], "mapping": {5: "6"}}
    assert Counter(calls) == Counter(
        [
            ("Payload", "v", float, 2),
            ("Payload", "v", float, 3.5),
            ("Payload", "k", int, 5),
            ("Payload", "v", str, 6),
        ]
    )


def test_custom_coercer_applies_to_optional_values() -> None:
    @serde.serde(type_check=serde.coerce(coercer=_integer_only_coercer))
    class Config:
        scale: float | None

    assert serde.from_dict(Config, {"scale": 4}) == Config(4.0)
    assert serde.to_dict(Config(4)) == {"scale": 4.0}
    assert serde.from_dict(Config, {"scale": None}) == Config(None)
    assert serde.to_dict(Config(None)) == {"scale": None}


def test_custom_field_converters_take_precedence_over_custom_coercer() -> None:
    calls: list[tuple[str, Any]] = []

    def record_call(_owner: str | None, field_name: str, target: type[Any], value: Any) -> Any:
        calls.append((field_name, value))
        return target(value)

    @serde.serde(type_check=serde.coerce(coercer=record_call))
    class Config:
        serializer_only: int = serde.field(serializer=lambda value: f"serialized:{value}")
        deserializer_only: int = serde.field(deserializer=lambda _value: 7)
        plain: int

    config = serde.from_dict(
        Config,
        {
            "serializer_only": "1",
            "deserializer_only": "ignored",
            "plain": "3",
        },
    )
    assert config == Config(1, 7, 3)
    assert Counter(calls) == Counter(
        [
            ("serializer_only", "1"),
            ("plain", "3"),
        ]
    )

    calls.clear()
    assert serde.to_dict(Config("4", "5", "6")) == {  # type: ignore[arg-type]
        "serializer_only": "serialized:4",
        "deserializer_only": 5,
        "plain": 6,
    }
    assert Counter(calls) == Counter(
        [
            ("deserializer_only", "5"),
            ("plain", "6"),
        ]
    )


def test_custom_coercer_does_not_handle_unions() -> None:
    def fail_if_called(
        _owner: str | None, _field_name: str, _target: type[Any], _value: Any
    ) -> Any:
        raise AssertionError("custom coercer must not be called")

    @serde.serde(type_check=serde.coerce(coercer=fail_if_called))
    class Choice:
        value: Union[int, str]

    assert serde.from_dict(Choice, {"value": "1"}) == Choice("1")
    assert serde.to_dict(Choice("1")) == {"value": "1"}


def test_nested_dataclass_uses_its_own_custom_coercer() -> None:
    outer_calls: list[tuple[str | None, str, type[Any], Any]] = []
    inner_calls: list[tuple[str | None, str, type[Any], Any]] = []

    def outer_coercer(owner: str | None, field_name: str, target: type[Any], value: Any) -> Any:
        outer_calls.append((owner, field_name, target, value))
        return target(value)

    def inner_coercer(owner: str | None, field_name: str, target: type[Any], value: Any) -> Any:
        inner_calls.append((owner, field_name, target, value))
        return target(value)

    @serde.serde(type_check=serde.coerce(coercer=inner_coercer))
    class Inner:
        value: int

    @serde.serde(type_check=serde.coerce(coercer=outer_coercer))
    class Outer:
        inner: Inner

    assert serde.from_dict(Outer, {"inner": {"value": "1"}}) == Outer(Inner(1))
    assert outer_calls == []
    assert inner_calls == [("Inner", "value", int, "1")]

    inner_calls.clear()
    assert serde.to_dict(Outer(Inner("2"))) == {"inner": {"value": 2}}  # type: ignore[arg-type]
    assert outer_calls == []
    assert inner_calls == [("Inner", "value", int, "2")]


def test_custom_coercer_wraps_deserialization_rejection() -> None:
    @serde.serde(type_check=serde.coerce(coercer=_integer_only_coercer))
    class Config:
        count: int

    with pytest.raises(
        serde.SerdeError,
        match=r"failed to coerce the field Config\.count.*expected an integer",
    ):
        serde.from_dict(Config, {"count": 3.9999})


def test_custom_coercer_wraps_serialization_rejection() -> None:
    @serde.serde(type_check=serde.coerce(coercer=_integer_only_coercer))
    class Config:
        count: int

    with pytest.raises(
        serde.SerdeError,
        match=r"failed to coerce the field Config\.count.*expected an integer",
    ):
        serde.to_dict(Config(3.9999))  # type: ignore[arg-type]
