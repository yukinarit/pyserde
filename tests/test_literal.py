import logging
from dataclasses import dataclass
from typing import Any, Literal

import pytest

import serde

from .common import (
    all_formats,
    format_dict,
    format_json,
    format_msgpack,
    format_tuple,
    format_yaml,
    opt_case,
    opt_case_ids,
)

log = logging.getLogger("test")

serde.init(True)


@serde.serde
@dataclass(unsafe_hash=True)
class LitInt:
    """
    Integer.
    """

    i: Literal[1, 2]


@serde.serde
@dataclass(unsafe_hash=True)
class LitStr:
    """
    String.
    """

    s: Literal["foo", "bar"]


@serde.serde
@dataclass(unsafe_hash=True)
class LitBool:
    """
    Boolean.
    """

    b: Literal[True]


@serde.serde
@dataclass(unsafe_hash=True)
class LitMixed:
    """
    Mixed Literal
    """

    m: Literal[1, 2, "foo", "bar", False, True]


@serde.serde
@dataclass(unsafe_hash=True)
class LitDict:
    """
    Dict containing primitives.
    """

    i: dict[Literal[1, 2], Literal[1, 2]]
    s: dict[Literal["foo", "bar"], Literal["foo", "bar"]]
    b: dict[Literal[True], Literal[True]]
    m: dict[
        Literal[1, 2, "foo", "bar", False, True],
        Literal[1, 2, "foo", "bar", False, True],
    ]


@serde.serde
@dataclass(unsafe_hash=True)
class LitStrDict:
    """
    Dict containing primitives.
    """

    i: dict[Literal["1", "2"], Literal[1, 2]]
    s: dict[Literal["foo", "bar"], Literal["foo", "bar"]]
    b: dict[Literal["True"], Literal[True]]
    m: dict[
        Literal["1", "2", "foo", "bar", "False", "True"],
        Literal[1, 2, "foo", "bar", False, True],
    ]


@serde.serde
@dataclass(unsafe_hash=True)
class Literals:
    """
    Primitives.
    """

    i: Literal[1, 2]
    s: Literal["foo", "bar"]
    b: Literal[True]
    m: Literal[1, 2, "foo", "bar", False, True]


@serde.serde
class LitNestedPrituple:
    """
    tuple containing nested primitives.
    """

    i: tuple[LitInt, LitInt]
    s: tuple[LitStr, LitStr]
    b: tuple[LitBool, LitBool, LitBool]
    m: tuple[LitMixed, LitMixed]


listLiterals = list[Literals]
PRI = Literals(1, "foo", True, 2)
DictLiterals = dict[str, Literals]


"""
Tests
"""


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_dict(se: Any, de: Any, opt: Any) -> None:
    if se in (serde.json.to_json, serde.msgpack.to_msgpack, serde.toml.to_toml):
        # JSON, Msgpack, Toml don't allow non string key.
        p = LitStrDict({"1": 2}, {"foo": "bar"}, {"True": True}, {"foo": True})
        assert p == de(LitStrDict, se(p))
    else:
        p = LitDict({1: 2}, {"foo": "bar"}, {True: True}, {2: False})  # type: ignore[assignment]
        assert p == de(LitDict, se(p))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_tuple(se: Any, de: Any, opt: Any) -> None:
    if se is not serde.toml.to_toml:
        p = LitNestedPrituple(
            (LitInt(1), LitInt(2)),
            (LitStr("foo"), LitStr("bar")),
            (LitBool(True), LitBool(True), LitBool(True)),
            (LitMixed(False), LitMixed("foo")),
        )
        assert p == de(LitNestedPrituple, se(p))


@pytest.mark.parametrize(
    "se,de", (format_dict + format_tuple + format_json + format_msgpack + format_yaml)
)
def test_list_literals(se: Any, de: Any) -> None:
    p = [PRI, PRI]
    assert p == de(listLiterals, se(p))

    p = []
    assert p == de(listLiterals, se(p))


@pytest.mark.parametrize(
    "se,de", (format_dict + format_tuple + format_json + format_msgpack + format_yaml)
)
def test_dict_literals(se: Any, de: Any) -> None:
    p = {"1": PRI, "2": PRI}
    assert p == de(DictLiterals, se(p))

    p = {}
    assert p == de(DictLiterals, se(p))


def test_json() -> None:
    p = Literals(1, "foo", True, "bar")
    s = '{"i":1,"s":"foo","b":true,"m":"bar"}'
    assert s == serde.json.to_json(p)


def test_msgpack() -> None:
    p = Literals(1, "foo", True, "bar")
    d = b"\x84\xa1i\x01\xa1s\xa3foo\xa1b\xc3\xa1m\xa3bar"
    assert d == serde.msgpack.to_msgpack(p)
    assert p == serde.msgpack.from_msgpack(Literals, d)


def test_msgpack_unnamed() -> None:
    p = Literals(1, "foo", True, "bar")
    d = b"\x94\x01\xa3foo\xc3\xa3bar"
    assert d == serde.msgpack.to_msgpack(p, named=False)
    assert p == serde.msgpack.from_msgpack(Literals, d, named=False)
