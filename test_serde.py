import enum
import json
import logging
import msgpack
import pytest
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, fields

from serde import deserialize, serialize, iter_types, astuple, asdict, from_obj
from serde.de import from_value
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('serde')

@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Pri:
    """
    Primitives.
    """
    i: int
    s: str
    f: float
    b: bool


@deserialize
@serialize
@dataclass
class PriList:
    """
    List containing primitives.
    """
    i: List[int]
    s: List[str]
    f: List[float]
    b: List[bool]


@deserialize
@serialize
@dataclass
class PriDict:
    """
    Dict containing primitives.
    """
    i: Dict[int, int]
    s: Dict[str, str]
    f: Dict[float, float]
    b: Dict[bool, bool]


@deserialize
@serialize
@dataclass
class PriTuple:
    """
    Tuple containing primitives.
    """
    i: Tuple[int, int, int]
    s: Tuple[str, str, str, str]
    f: Tuple[float, float, float, float, float]
    b: Tuple[bool, bool, bool, bool, bool, bool]


def test_non_dataclass():
    with pytest.raises(TypeError):
        @deserialize
        @serialize
        class Hoge:
            i: int


def test_from_value():
    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: int
        s: str
        f: float
        b: bool
        pri: Pri
        lst: List[int]
        lst2: List[Pri]
        dct: Dict[str, int]
        dct2: Dict[str, Pri]
        dct3: Dict[Pri, Pri]
        tpl: Tuple[int, str, float]
        tpl2: Tuple[str, Pri]

    assert 'data' == from_value(fields(Hoge)[0].type, 'data')
    assert 'data' == from_value(fields(Hoge)[1].type, 'data')
    assert 'data' == from_value(fields(Hoge)[2].type, 'data')
    assert 'data' == from_value(fields(Hoge)[3].type, 'data')
    assert 'from_any(Pri, data)' == from_value(fields(Hoge)[4].type, 'data')
    assert '[d for d in data]' == from_value(fields(Hoge)[5].type, 'data')
    assert '[from_any(Pri, d) for d in data]' == from_value(fields(Hoge)[6].type, 'data')
    assert '{ k: v for k, v in data.items() }' == from_value(fields(Hoge)[7].type, 'data')
    assert '{ k: from_any(Pri, v) for k, v in data.items() }' == from_value(fields(Hoge)[8].type, 'data')
    assert '{ from_any(Pri, k): from_any(Pri, v) for k, v in data.items() }' == \
        from_value(fields(Hoge)[9].type, 'data')
    assert '(data[0], data[1], data[2], )' == from_value(fields(Hoge)[10].type, 'data')
    assert '(data[0], from_any(Pri, data[1]), )' == from_value(fields(Hoge)[11].type, 'data')


def test_iter_types():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        i: int

    @deserialize
    @serialize
    @dataclass
    class Opt:
        i: Optional[int]

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: int
        foo: Foo
        lst: List[int]
        lst2: List[Foo]

    assert [Pri, int, str, float] == list(iter_types(Pri))
    assert [Foo, int] == list(iter_types(Foo))
    assert [Foo, int] == list(iter_types(List[Foo]))
    assert [str, Foo, int] == list(iter_types(Dict[str, Foo]))
    assert [str, Foo, int, float] == list(iter_types(Tuple[str, Foo, float]))
    assert [Opt, int] == list(iter_types(Opt))
    assert [Foo, int, str, Foo, int] == list(iter_types(Tuple[List[Foo], Dict[str, Foo]]))
    assert [str, str, int, bool, float] == list(iter_types(Tuple[Tuple[str, str], Tuple[int, bool, float]]))
    assert [Hoge, int, Foo, int, int, Foo, int] == list(iter_types(Hoge))


def test_primitive():
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
    assert h == from_json(Hoge, s)


def test_enum():
    class IEnum(enum.IntEnum):
        V0 = enum.auto()
        V1 = enum.auto()
        V2 = enum.auto()

    class SEnum(enum.Enum):
        V0 = 'v0'
        V1 = 'v1'
        V2 = 'v2'

    # Only IntEnum is supported now.
    try:
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
    except TypeError:
        pass

    # h = Hoge(ie0=IEnum.V0, ie1=IEnum.V1, ie2=IEnum.V2, se0=SEnum.V0, se1=SEnum.V1, se2=SEnum.V2)
    # s = '{"ie0": 1, "ie1": 2, "ie2": 3}'
    # assert s == to_json(h)
    # assert h == from_json(Hoge, s)


def test_optional():
    @deserialize
    @serialize
    @dataclass
    class Foo:
        i: int

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: Optional[int]
        f: Foo

    f = Foo(i=20)
    h = Hoge(i=10, f=f)
    s = '{"i": 10, "f": {"i": 20}}'
    assert s == to_json(h)
    assert f == from_json(Foo, '{"i": 20}')
    assert h == from_json(Hoge, s)


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


def test_from_obj():
    @deserialize
    @serialize
    @dataclass(unsafe_hash=True)
    class Bar:
        i: int

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
    assert Bar(100) == from_obj(Bar, (100,))
    assert Bar(100) == from_obj(Bar, {'i': 100})
    assert f == from_obj(Foo, (10, 's', 20.0, False))
    assert f == from_obj(Optional[Foo], [10, 's', 20.0, False])
    assert from_obj(Optional[Foo], None) is None
    assert f == from_obj(Foo, dict(i=10, s='s', f=20.0, b=False))
    v = (f,)
    assert v == from_obj(Tuple[Foo], ((10, 's', 20.0, False),))
    v = [f]
    assert v == from_obj(List[Foo], [(10, 's', 20.0, False)])
    d = {'foo': f}
    assert d == from_obj(Dict[str, Foo], {'foo': (10, 's', 20.0, False)})
    d = {'foo': [f, f]}
    assert d == from_obj(Optional[Dict[str, List[Foo]]], {'foo': [(10, 's', 20.0, False), (10, 's', 20.0, False)]})


def test_from_obj_complex():
    @deserialize
    @serialize
    @dataclass(unsafe_hash=True)
    class Foo:
        i: int

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        d: Dict[Foo, List[Foo]]
        lst: List[Foo]

    f = Foo(i=100)
    f2 = Foo(i=100)
    lst = [f, f2]
    h = Hoge(d={f: lst}, lst=lst)
    assert h == from_obj(Hoge, {'d': {(100,): lst}, 'lst': lst})
    hh = from_obj(Hoge, ({(100,): lst}, lst))
    assert h.d == hh.d
    assert h.lst == hh.lst


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


def test_msgpack():
    @deserialize
    @serialize
    @dataclass(unsafe_hash=True)
    class Foo:
        i: int

    @deserialize
    @serialize
    @dataclass
    class Hoge:
        i: int
        s: str
        f: float
        b: bool
        d: Dict[Foo, int]

    f = Foo(i=100)
    # h = Hoge(i=10, s='hoge', f=100.0, b=True, d={f: [f, f]})
    # p = msgpack.packb((10, 'hoge', 100.0, True, {(100,): [(100,), (100,)]}))
    h = Hoge(i=10, s='hoge', f=100.0, b=True, d={f: 100})
    p = msgpack.packb((10, 'hoge', 100.0, True, {(100,): 100}))
    assert p == to_msgpack(h)
    hh = from_msgpack(Hoge, p, use_list=False)
    assert h.i == hh.i
    assert h.s == hh.s
    assert h.f == hh.f
    assert h.b == hh.b
    assert h.d == hh.d
