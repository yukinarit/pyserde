import enum
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List

import pytest

from serde import asdict, astuple, deserialize, from_dict
from serde import init as serde_init
from serde import logger, serialize
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml

from .data import Bool, Float, Int, NestedPri, NestedPriOpt, NestedPriTuple, Pri, PriOpt, PriTuple, Str

logging.basicConfig(level=logging.WARNING)

logger.setLevel(logging.DEBUG)

serde_init(True)


all_formats = [
    (asdict, from_dict),
    (to_json, from_json),
    (to_msgpack, from_msgpack),
    (to_yaml, from_yaml),
    (to_toml, from_toml),
]


@pytest.mark.parametrize('se,de', all_formats)
def test_primitive(se, de):
    p = Pri(10, 'foo', 100.0, True)
    assert p == de(Pri, se(p))


@pytest.mark.parametrize('se,de', all_formats)
def test_nested_primitive(se, de):
    p = NestedPri(Int(10), Str('foo'), Float(100.0), Bool(True))
    assert p == from_dict(NestedPri, asdict(p))


def test_non_dataclass():
    with pytest.raises(TypeError):

        @deserialize
        @serialize
        class Hoge:
            i: int


def test_forward_declaration():
    @serialize
    @deserialize
    @dataclass
    class Foo:
        bar: 'Bar'

    @serialize
    @deserialize
    @dataclass
    class Bar:
        i: int

    h = Foo(bar=Bar(i=10))
    assert h.bar.i == 10


def test_enum():
    class IEnum(enum.IntEnum):
        V0 = enum.auto()
        V1 = enum.auto()
        V2 = enum.auto()

    class SEnum(enum.Enum):
        V0 = 'v0'
        V1 = 'v1'
        V2 = 'v2'

    # NOTE: Only IntEnum is supported now.
    @deserialize
    @serialize
    @dataclass
    class Hoge:
        ie0: IEnum
        ie1: IEnum
        ie2: IEnum
        se0: SEnum
        se1: SEnum
        se2: SEnum


@pytest.mark.parametrize('se,de', all_formats)
def test_tuple(se, de):
    p = PriTuple(
        (10, 20, 30), ('a', 'b', 'c', 'd'), (10.0, 20.0, 30.0, 40.0, 50.0), (True, False, True, False, True, False)
    )
    tpl: PriTuple = de(PriTuple, se(p))
    assert tpl.i == (10, 20, 30)
    assert tpl.s == ('a', 'b', 'c', 'd')
    assert tpl.f == (10.0, 20.0, 30.0, 40.0, 50.0)
    assert tpl.b == (True, False, True, False, True, False)

    # List can also be used.
    p = PriTuple(
        [10, 20, 30], ['a', 'b', 'c', 'd'], [10.0, 20.0, 30.0, 40.0, 50.0], [True, False, True, False, True, False]
    )
    tpl: PriTuple = de(PriTuple, se(p))
    assert tpl.i == (10, 20, 30)
    assert tpl.s == ('a', 'b', 'c', 'd')
    assert tpl.f == (10.0, 20.0, 30.0, 40.0, 50.0)
    assert tpl.b == (True, False, True, False, True, False)


@pytest.mark.parametrize('se,de', all_formats)
def test_dataclass_in_tuple(se, de):
    src = NestedPriTuple(
        (Int(10), Int(10), Int(10)),
        (Str("10"), Str("10"), Str("10"), Str("10")),
        (Float(10.0), Float(10.0), Float(10.0), Float(10.0), Float(10.0)),
        (Bool(False), Bool(False), Bool(False), Bool(False), Bool(False), Bool(False)),
    )
    assert src == from_json(NestedPriTuple, to_json(src))

    with pytest.raises(IndexError):
        j = json.dumps(
            {
                'i': (10, 20),
                's': ('a', 'b', 'c', 'd'),
                'f': (10.0, 20.0, 30.0, 40.0, 50.0),
                'b': (True, False, True, False, True, False),
            }
        )
        _: PriTuple = from_json(PriTuple, j)


@pytest.mark.parametrize('se,de', all_formats)
def test_optional(se, de):
    p = PriOpt(20, None, 100.0, True)
    assert p == de(PriOpt, se(p))


def test_optional_dataclass():
    pass
    # p = NestedPriOpt(Int(20), Str(None), Float(100.0), Bool(True))
    # s = '{"i": 20, "s": null, "f": 100.0, "b": true}'
    # TODO
    # assert s == asdict(p)
    # assert p == from_json(PriOpt, s)


def test_complex():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        v: List[int] = field(default_factory=list)
        d: Dict[str, int] = field(default_factory=dict)

    @deserialize
    @serialize
    @dataclass
    class Bar:
        i: int

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: int
        s: str
        f: float
        b: bool
        foo: Foo
        lst: List[Bar] = field(default_factory=list)
        lst2: List[Dict[str, Bar]] = field(default_factory=list)
        dct: Dict[str, List[List[Bar]]] = field(default_factory=dict)

    f = Foo(v=[1, 2, 3, 4, 5], d={'hoge': 10, 'fuga': 20})
    lst = [Bar(10), Bar(20)]
    lst2 = [{'bar1': Bar(10)}, {'bar2': Bar(10), 'bar3': Bar(20)}]
    dct = {'hoge': [[Bar(10), Bar(20)], [Bar(20), Bar(30)]]}
    h = Hoge(i=10, s='hoge', f=100.0, b=True, foo=f, lst=lst, lst2=lst2, dct=dct)
    s = """
               {"i": 10,
                "s": "hoge",
                "f": 100.0,
                "b": true,
                "foo" : {
                    "v": [1, 2, 3, 4, 5],
                    "d": {"hoge": 10, "fuga": 20}
                },
                "lst": [{"i": 10}, {"i": 20}],
                "lst2": [{"bar1": {"i": 10}}, {"bar2": {"i": 10}, "bar3": {"i": 20}}],
                "dct": {"hoge": [[{"i": 10}, {"i": 20}], [{"i": 20}, {"i": 30}]]}
                }
                """
    assert json.loads(s) == json.loads(to_json(h))
    hh = from_json(Hoge, s)
    assert h.foo == hh.foo
    assert h.lst == hh.lst
    assert h.dct == hh.dct


def test_json():
    p = Pri(10, 'foo', 100.0, True)
    s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
    assert s == to_json(p)

    assert '10' == to_json(10)
    assert '[10, 20, 30]' == to_json([10, 20, 30])
    assert '{"hoge": 10, "fuga": 10}' == to_json({'hoge': 10, 'fuga': 10})


def test_msgpack():
    p = Pri(10, 'foo', 100.0, True)
    d = b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3'
    assert d == to_msgpack(p)
    assert p == from_msgpack(Pri, d)
