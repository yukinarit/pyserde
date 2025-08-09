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
