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

from .data import Bool, Float, Int, NestedPri, NestedPriOpt, NestedPriTuple, Pri, PriOpt, PriTuple, Str

logging.basicConfig(level=logging.WARNING)

logger.setLevel(logging.DEBUG)

serde_init(True)


def test_primitive():
    p = Pri(10, 'foo', 100.0, True)
    d = {"i": 10, "s": "foo", "f": 100.0, "b": True}
    assert d == asdict(p)
    assert p == from_dict(Pri, d)


def test_nested_primitive():
    p = NestedPri(Int(10), Str('foo'), Float(100.0), Bool(True))
    d = {"i": {"i": 10}, "s": {"s": "foo"}, "f": {"f": 100.0}, "b": {"b": True}}
    assert d == asdict(p)
    assert p == from_dict(NestedPri, d)


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


def test_tuple():
    j = json.dumps(
        {
            'i': (10, 20, 30),
            's': ('a', 'b', 'c', 'd'),
            'f': (10.0, 20.0, 30.0, 40.0, 50.0),
            'b': (True, False, True, False, True, False),
        }
    )
    tpl: PriTuple = from_json(PriTuple, j)
    assert tpl.i == (10, 20, 30)
    assert tpl.s == ('a', 'b', 'c', 'd')
    assert tpl.f == (10.0, 20.0, 30.0, 40.0, 50.0)
    assert tpl.b == (True, False, True, False, True, False)

    # List can also be used.
    j = json.dumps(
        {
            'i': [10, 20, 30],
            's': ['a', 'b', 'c', 'd'],
            'f': [10.0, 20.0, 30.0, 40.0, 50.0],
            'b': [True, False, True, False, True, False],
        }
    )
    tpl: PriTuple = from_json(PriTuple, j)
    assert tpl.i == (10, 20, 30)
    assert tpl.s == ('a', 'b', 'c', 'd')
    assert tpl.f == (10.0, 20.0, 30.0, 40.0, 50.0)
    assert tpl.b == (True, False, True, False, True, False)


def test_dataclass_in_tuple():
    src = NestedPriTuple(
        (Int(10), Int(10), Int(10)),
        (Str("10"), Str("10"), Str("10"), Str("10")),
        (Float(10.0), Float(10.0), Float(10.0), Float(10.0), Float(10.0)),
        (Bool(False), Bool(False), Bool(False), Bool(False), Bool(False), Bool(False)),
    )
    j = to_json(src)
    dst: PriTuple = from_json(NestedPriTuple, j)
    assert src == dst

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


def test_optional():
    p = PriOpt(20, None, 100.0, True)
    s = '{"i": 20, "s": null, "f": 100.0, "b": true}'
    assert s == to_json(p)
    assert p == from_json(PriOpt, s)


def test_optional_dataclass():
    pass
    # p = NestedPriOpt(Int(20), Str(None), Float(100.0), Bool(True))
    # s = '{"i": 20, "s": null, "f": 100.0, "b": true}'
    # TODO
    # assert s == asdict(p)
    # assert p == from_json(PriOpt, s)


def test_container():
    @deserialize
    @serialize
    @dataclass(unsafe_hash=True)
    class Foo:
        i: int

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        v: List[int] = field(default_factory=list)
        d: Dict[str, int] = field(default_factory=dict)
        d2: Dict[Foo, int] = field(default_factory=dict)

    f = Foo(i=100)
    h = Hoge(v=[1, 2, 3, 4, 5], d={'hoge': 10, 'fuga': 20}, d2={f: 100})
    with pytest.raises(TypeError):
        # dict (Foo in this case) cannot be a dict key.
        asdict(h)

    # tuple is ok
    assert astuple(h) == ([1, 2, 3, 4, 5], {'hoge': 10, 'fuga': 20}, {(100,): 100})

    with pytest.raises(TypeError):
        to_json(h)


def test_nested():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        i: int
        s: str
        f: float
        b: bool

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: int
        s: str
        f: float
        b: bool
        foo: Foo

    f = Foo(i=20, s='foo', f=200.0, b=False)
    h = Hoge(i=10, s='hoge', f=100.0, b=True, foo=f)
    s = """
               {"i": 10,
                "s": "hoge",
                "f": 100.0,
                "b": true,
                "foo" : {
                    "i": 20,
                    "s": "foo",
                    "f": 200.0,
                    "b": false}}
               """
    assert json.loads(s) == json.loads(to_json(h))
    assert h == from_json(Hoge, s)


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


def test_asdict():
    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: int

    assert {'i': 10} == asdict(Hoge(i=10))
    # assert {'i': 10} == asdict(10)


def test_astuple():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        i: int
        s: str
        f: float
        b: bool

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        f: Foo
        f2: Foo

    f = Foo(i=10, s='s', f=20.0, b=False)
    f2 = Foo(i=10, s='s', f=20.0, b=True)
    assert (10, 's', 20.0, False) == astuple(f)
    assert ((10, 's', 20.0, False), (10, 's', 20.0, True)) == astuple(Hoge(f=f, f2=f2))
    assert (10, 20, 30) == astuple([10, 20, 30])
    assert (10, 20, 30) == astuple((10, 20, 30))
    assert 10 == astuple(10)


# def test_from_obj():
#     @deserialize
#     @serialize
#     @dataclass(unsafe_hash=True)
#     class Bar:
#         i: int
#
#     @deserialize
#     @serialize
#     @dataclass
#     class Foo:
#         i: int
#         s: str
#         f: float
#         b: bool
#
#     @deserialize
#     @serialize
#     @dataclass
#     class Hoge:
#         f: Foo
#         f2: Foo
#
#     # Primitrive types
#     assert 10 == from_obj(int, 10)
#     assert 0.1 == from_obj(float, 0.1)
#     assert 'hoge' == from_obj(str, 'hoge')
#     assert not from_obj(bool, False)
#
#     f = Foo(i=10, s='s', f=20.0, b=False)
#     assert Bar(100) == from_obj(Bar, (100,))
#     assert Bar(100) == from_obj(Bar, {'i': 100})
#     assert f == from_obj(Foo, (10, 's', 20.0, False))
#     assert f == from_obj(Optional[Foo], [10, 's', 20.0, False])
#     assert from_obj(Optional[Foo], None) is None
#     assert f == from_obj(Foo, dict(i=10, s='s', f=20.0, b=False))
#     assert (f,) == from_obj(Tuple[Foo], ((10, 's', 20.0, False),))
#     assert [f] == from_obj(List[Foo], [(10, 's', 20.0, False)])
#     assert {'foo': f} == from_obj(Dict[str, Foo], {'foo': (10, 's', 20.0, False)})
#     assert {'foo': [f, f]} == from_obj(
#         Optional[Dict[str, List[Foo]]], {'foo': [(10, 's', 20.0, False), (10, 's', 20.0, False)]}
#     )


# def test_from_obj_complex():
#     @deserialize
#     @serialize
#     @dataclass(unsafe_hash=True)
#     class Foo:
#         i: int
#
#     @deserialize
#     @serialize
#     @dataclass
#     class Hoge:
#         d: Dict[Foo, List[Foo]]
#         lst: List[Foo]
#         lst2: List[int]
#         opt: Optional[Foo]
#
#     f = Foo(i=100)
#     f2 = Foo(i=100)
#     lst = [f, f2]
#     lst2 = [1, 2, 3]
#     h = Hoge(d={f: lst}, lst=lst, lst2=lst2, opt=f)
#     hh = from_obj(Hoge, ({(100,): lst}, lst, lst2, f))
#     assert h.d == hh.d
#     assert h.lst == hh.lst
#     assert h.lst2 == hh.lst2
#     assert h.opt == hh.opt
#
#     hh == from_obj(Hoge, {'d': {(100,): lst}, 'lst': lst, 'lst2': lst2, 'opt': None})
#     assert h.d == hh.d
#     assert h.lst == hh.lst
#     assert h.lst2 == hh.lst2
#     assert h.opt == hh.opt


def test_json():
    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: int
        s: str
        f: float
        b: bool

    h = Hoge(i=10, s='hoge', f=100.0, b=True)
    s = '{"i": 10, "s": "hoge", "f": 100.0, "b": true}'
    assert s == to_json(h)

    assert '10' == to_json(10)
    assert '[10, 20, 30]' == to_json([10, 20, 30])
    assert '{"hoge": 10, "fuga": 10}' == to_json({'hoge': 10, 'fuga': 10})


# def test_msgpack():
#     @deserialize
#     @serialize
#     @dataclass(unsafe_hash=True)
#     class Foo:
#         i: int
#
#     @deserialize
#     @serialize
#     @dataclass
#     class Hoge:
#         i: int
#         s: str
#         f: float
#         b: bool
#         d: Dict[Foo, int]
#         lst: List[Foo]
#
#     f = Foo(i=100)
#     lst = [f, f, f]
#     h = Hoge(i=10, s='hoge', f=100.0, b=True, d={f: 100}, lst=lst)
#     p = msgpack.packb((10, 'hoge', 100.0, True, {(100,): 100}, [(100,), (100,), (100,)]))
#     hh = from_msgpack(Hoge, p, use_list=False)
#     assert p == to_msgpack(h)
#     assert h.i == hh.i
#     assert h.s == hh.s
#     assert h.f == hh.f
#     assert h.b == hh.b
#     assert h.d == hh.d
#     assert lst == hh.lst
