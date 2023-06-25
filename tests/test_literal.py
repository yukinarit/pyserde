import logging
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

if sys.version_info[:2] == (3, 7):
    from typing_extensions import Literal
else:
    from typing import Literal

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

    i: Dict[Literal[1, 2], Literal[1, 2]]
    s: Dict[Literal["foo", "bar"], Literal["foo", "bar"]]
    b: Dict[Literal[True], Literal[True]]
    m: Dict[
        Literal[1, 2, "foo", "bar", False, True],
        Literal[1, 2, "foo", "bar", False, True],
    ]


@serde.serde
@dataclass(unsafe_hash=True)
class LitStrDict:
    """
    Dict containing primitives.
    """

    i: Dict[Literal["1", "2"], Literal[1, 2]]
    s: Dict[Literal["foo", "bar"], Literal["foo", "bar"]]
    b: Dict[Literal["True"], Literal[True]]
    m: Dict[
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
class LitNestedPriTuple:
    """
    Tuple containing nested primitives.
    """

    i: Tuple[LitInt, LitInt]
    s: Tuple[LitStr, LitStr]
    b: Tuple[LitBool, LitBool, LitBool]
    m: Tuple[LitMixed, LitMixed]


ListLiterals = List[Literals]
PRI = Literals(1, "foo", True, 2)
DictLiterals = Dict[str, Literals]


"""
Tests
"""


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_dict(se, de, opt):
    if se in (serde.json.to_json, serde.msgpack.to_msgpack, serde.toml.to_toml):
        # JSON, Msgpack, Toml don't allow non string key.
        p = LitStrDict({"1": 2}, {"foo": "bar"}, {"True": True}, {"foo": True})
        assert p == de(LitStrDict, se(p))
    else:
        p = LitDict({1: 2}, {"foo": "bar"}, {True: True}, {2: False})
        assert p == de(LitDict, se(p))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_tuple(se, de, opt):
    if se is not serde.toml.to_toml:
        p = LitNestedPriTuple(
            (LitInt(1), LitInt(2)),
            (LitStr("foo"), LitStr("bar")),
            (LitBool(True), LitBool(True), LitBool(True)),
            (LitMixed(False), LitMixed("foo")),
        )
        assert p == de(LitNestedPriTuple, se(p))


@pytest.mark.parametrize(
    "se,de", (format_dict + format_tuple + format_json + format_msgpack + format_yaml)
)
def test_list_literals(se, de):
    p = [PRI, PRI]
    assert p == de(ListLiterals, se(p))

    p = []
    assert p == de(ListLiterals, se(p))


@pytest.mark.parametrize(
    "se,de", (format_dict + format_tuple + format_json + format_msgpack + format_yaml)
)
def test_dict_literals(se, de):
    p = {"1": PRI, "2": PRI}
    assert p == de(DictLiterals, se(p))

    p = {}
    assert p == de(DictLiterals, se(p))


def test_json():
    p = Literals(1, "foo", True, "bar")
    s = '{"i":1,"s":"foo","b":true,"m":"bar"}'
    assert s == serde.json.to_json(p)


def test_msgpack():
    p = Literals(1, "foo", True, "bar")
    d = b"\x84\xa1i\x01\xa1s\xa3foo\xa1b\xc3\xa1m\xa3bar"
    assert d == serde.msgpack.to_msgpack(p)
    assert p == serde.msgpack.from_msgpack(Literals, d)


def test_msgpack_unnamed():
    p = Literals(1, "foo", True, "bar")
    d = b"\x94\x01\xa3foo\xc3\xa3bar"
    assert d == serde.msgpack.to_msgpack(p, named=False)
    assert p == serde.msgpack.from_msgpack(Literals, d, named=False)
