import datetime
import pathlib
from beartype.roar import BeartypeCallHintViolation
from typing import (
    Union,
    Any,
)
from beartype.typing import (
    Dict,
    List,
    Set,
    Tuple,
)

import pytest

import serde

from . import data

test_cases: List[Tuple[Any, Any, bool]] = [
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
    (List[int], [1], False),
    (List[int], [1.0], True),
    (List[float], [1.0], False),
    (List[float], [1], True),
    (List[float], ["foo"], True),
    (List[str], ["foo"], False),
    (List[str], [True], True),
    (List[bool], [True], False),
    (List[bool], [10], True),
    (List[data.Int], [data.Int(1)], False),
    (List[data.Int], [data.Int.uncheck_new(1.0)], True),  # Runtime incompatible object
    (List[data.Int], [], False),
    (Dict[str, int], {"foo": 10}, False),
    (Dict[str, int], {"foo": 10.0}, False),
    (Dict[str, data.Int], {"foo": data.Int(1)}, False),
    (Dict[str, data.Int], {"foo": data.Int.uncheck_new(1.0)}, True),  # Runtime incompatible object
    (Set[int], {10}, False),
    (Set[int], {10.0}, False),
    (Set[int], [10], True),
    (Tuple[int], (10,), False),
    (Tuple[int], (10.0,), True),
    (Tuple[int, str], (10, "foo"), False),
    (Tuple[int, str], (10, 10.0), True),
    (Tuple[data.Int, data.Str], (data.Int(1), data.Str("2")), False),
    (Tuple[data.Int, data.Str], (data.Int(1), data.Int(2)), True),
    (Tuple, (10, 10.0), False),
    (Tuple[int, ...], (1, 2), False),
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
default_unstable_test_cases: List[Tuple[Any, Any, bool]] = [
    (List[int], [1, 1.0], True),
    (List[data.Int], [data.Int(1), data.Float(10.0)], True),
    (Dict[str, int], {"foo": 10, 100: "bar"}, False),
    (Tuple[int, ...], (1, 2.0), True),
]


@pytest.mark.parametrize("T,data,exc", test_cases)
def test_type_check_strict(T: Any, data: Any, exc: bool) -> None:
    @serde.serde
    class C:
        a: T

    if exc:
        with pytest.raises((serde.SerdeError, BeartypeCallHintViolation)):
            d = serde.to_dict(C(data))
            serde.from_dict(C, d)
    else:
        d = serde.to_dict(C(data))
        serde.from_dict(C, d)


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
    d2: Dict[str, Dict[str, Any]] = serde.to_dict(p2)
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
