import enum
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

import msgpack
import pytest

from serde import asdict, astuple, deserialize, from_obj, init as serde_init, logger, serialize, typecheck
from serde.compat import is_dict, is_list, is_opt, is_tuple, is_union, type_args, union_args, iter_types
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack

logging.basicConfig(level=logging.WARNING)
logger.setLevel(logging.DEBUG)

serde_init(True)


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Int:
    """
    Integer.
    """

    i: int


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Str:
    """
    String.
    """

    s: str


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Float:
    """
    Float.
    """

    f: float


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Boolean:
    """
    Boolean.
    """

    b: bool


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


@deserialize
@serialize
@dataclass
class PriOpt:
    """
    Optional Primitives.
    """

    i: Optional[int]
    s: Optional[str]
    f: Optional[float]
    b: Optional[bool]


def test_non_dataclass():
    with pytest.raises(TypeError):

        @deserialize
        @serialize
        class Hoge:
            i: int


def test_types():
    assert is_list(List[int])
    assert is_tuple(Tuple[int, int, int])
    assert is_dict(Dict[str, int])
    assert is_opt(Optional[int])
    assert is_union(Union[int, str])
    assert is_union(Union[Optional[int], Optional[str]])

    assert is_opt(Optional[int])
    assert not is_union(Optional[int])

    assert not is_opt(Union[Optional[int], Optional[str]])
    assert is_union(Union[Optional[int], Optional[str]])


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

    # assert 'data' == de_value(fields(Hoge)[0].type, 'data')
    # assert 'data' == de_value(fields(Hoge)[1].type, 'data')
    # assert 'data' == de_value(fields(Hoge)[2].type, 'data')
    # assert 'data' == de_value(fields(Hoge)[3].type, 'data')
    # assert 'from_dict_or_iter(Pri, data)' == de_value(fields(Hoge)[4].type, 'data')
    # assert '[d for d in data]' == de_value(fields(Hoge)[5].type, 'data')
    # assert '[from_dict_or_iter(Pri, d) for d in data]' == de_value(fields(Hoge)[6].type, 'data')
    # assert '{ k: v for k, v in data.items() }' == de_value(fields(Hoge)[7].type, 'data')
    # assert '{ k: from_dict_or_iter(Pri, v) for k, v in data.items() }' == de_value(fields(Hoge)[8].type, 'data')
    # assert '{ from_dict_or_iter(Pri, k): from_dict_or_iter(Pri, v) for k, v in data.items() }' == \
    #     de_value(fields(Hoge)[9].type, 'data')
    # assert '(data[0], data[1], data[2], )' == de_value(fields(Hoge)[10].type, 'data')
    # assert '(data[0], from_dict_or_iter(Pri, data[1]), )' == de_value(fields(Hoge)[11].type, 'data')


def test_iter_types():
    assert [Pri, int, str, float, bool] == list(iter_types(Pri))
    assert [str, Pri, int, str, float, bool] == list(iter_types(Dict[str, Pri]))
    assert [str] == list(iter_types(List[str]))
    assert [int, str, bool, float] == list(iter_types(Tuple[int, str, bool, float]))
    assert [PriOpt, int, str, float, bool] == list(iter_types(PriOpt))
    assert [Pri, int, str, float, bool, Pri, int, str, float, bool, Pri, int, str, float, bool] == list(
        iter_types(Tuple[List[Pri], Tuple[Pri, Pri]])
    )


def test_primitive():
    p = Pri(i=10, s='hoge', f=100.0, b=True)
    s = '{"i": 10, "s": "hoge", "f": 100.0, "b": true}'
    assert s == to_json(p)
    assert p == from_json(Pri, s)


def test_forward_declaration():
    print(locals())

    @serialize
    @deserialize
    @dataclass
    class Hoge:
        fuga: 'Fuga'

    @serialize
    @deserialize
    @dataclass
    class Fuga:
        i: int

    h = Hoge(fuga=Fuga(i=10))
    assert h.fuga.i == 10


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


def test_type_args():
    assert (int,) == type_args(List[int])
    assert (int, str) == type_args(Dict[int, str])
    assert (int, type(None)) == type_args(Optional[int])
    assert (Optional[int],) == type_args(List[Optional[int]])
    assert (List[int], type(None)) == type_args(Optional[List[int]])
    assert (List[int], Dict[str, int]) == type_args(Union[List[int], Dict[str, int]])
    assert (int, type(None), str) == type_args(Union[Optional[int], str])


def test_union_args():
    assert (int, str) == union_args(Union[int, str])
    assert (List[int], Dict[int, str]) == union_args(Union[List[int], Dict[int, str]])
    assert (Optional[int], str) == union_args(Union[Optional[int], str])


def test_optional():
    p = PriOpt(i=20, f=100.0, s=None, b=True)
    s = '{"i": 20, "s": null, "f": 100.0, "b": true}'
    assert s == to_json(p)
    assert p == from_json(PriOpt, s)


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

    # Primitrive types
    assert 10 == from_obj(int, 10)
    assert 0.1 == from_obj(float, 0.1)
    assert 'hoge' == from_obj(str, 'hoge')
    assert not from_obj(bool, False)

    f = Foo(i=10, s='s', f=20.0, b=False)
    assert Bar(100) == from_obj(Bar, (100,))
    assert Bar(100) == from_obj(Bar, {'i': 100})
    assert f == from_obj(Foo, (10, 's', 20.0, False))
    assert f == from_obj(Optional[Foo], [10, 's', 20.0, False])
    assert from_obj(Optional[Foo], None) is None
    assert f == from_obj(Foo, dict(i=10, s='s', f=20.0, b=False))
    assert (f,) == from_obj(Tuple[Foo], ((10, 's', 20.0, False),))
    assert [f] == from_obj(List[Foo], [(10, 's', 20.0, False)])
    assert {'foo': f} == from_obj(Dict[str, Foo], {'foo': (10, 's', 20.0, False)})
    assert {'foo': [f, f]} == from_obj(
        Optional[Dict[str, List[Foo]]], {'foo': [(10, 's', 20.0, False), (10, 's', 20.0, False)]}
    )


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
        lst2: List[int]
        opt: Optional[Foo]

    f = Foo(i=100)
    f2 = Foo(i=100)
    lst = [f, f2]
    lst2 = [1, 2, 3]
    h = Hoge(d={f: lst}, lst=lst, lst2=lst2, opt=f)
    hh = from_obj(Hoge, ({(100,): lst}, lst, lst2, f))
    assert h.d == hh.d
    assert h.lst == hh.lst
    assert h.lst2 == hh.lst2
    assert h.opt == hh.opt

    hh == from_obj(Hoge, {'d': {(100,): lst}, 'lst': lst, 'lst2': lst2, 'opt': None})
    assert h.d == hh.d
    assert h.lst == hh.lst
    assert h.lst2 == hh.lst2
    assert h.opt == hh.opt


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
        lst: List[Foo]

    f = Foo(i=100)
    lst = [f, f, f]
    h = Hoge(i=10, s='hoge', f=100.0, b=True, d={f: 100}, lst=lst)
    p = msgpack.packb((10, 'hoge', 100.0, True, {(100,): 100}, [(100,), (100,), (100,)]))
    hh = from_msgpack(Hoge, p, use_list=False)
    assert p == to_msgpack(h)
    assert h.i == hh.i
    assert h.s == hh.s
    assert h.f == hh.f
    assert h.b == hh.b
    assert h.d == hh.d
    assert lst == hh.lst


def test_typecheck():
    # Primitive
    typecheck(int, 10)
    with pytest.raises(ValueError):
        typecheck(int, 10.0)

    # Dataclass
    p = Pri(i=10, s='hoge', f=100.0, b=True)
    typecheck(Pri, p)

    with pytest.raises(ValueError):
        p.i = 10.0
        typecheck(Pri, p)

    # Dataclass (Nested)
    @dataclass
    class Hoge:
        p: Pri

    h = Hoge(Pri(i=10, s='hoge', f=100.0, b=True))
    typecheck(Hoge, h)

    with pytest.raises(ValueError):
        h.p.i = 10.0
        typecheck(Hoge, h)

    # List
    typecheck(List[int], [10])
    with pytest.raises(ValueError):
        typecheck(List[int], [10.0])

    # List of dataclasses
    typecheck(List[Int], [Int(n) for n in range(1, 10)])
    with pytest.raises(ValueError):
        typecheck(List[Pri], [Pri(i=10.0, s='hoge', f=100.0, b=True)])

    # Tuple
    typecheck(Tuple[int, str, float, bool], (10, 'hoge', 100.0, True))
    with pytest.raises(ValueError):
        typecheck(Tuple[int, str, float, bool], (10.0, 'hoge', 100.0, True))

    # Tuple of dataclasses
    typecheck(Tuple[Int, Str, Float, Boolean], (Int(10), Str('hoge'), Float(100.0), Boolean(True)))
    with pytest.raises(ValueError):
        typecheck(Tuple[Int, Str, Float, Boolean], (Int(10.0), Str('hoge'), Float(100.0), Boolean(True)))

    # Dict
    typecheck(Dict[str, int], dict(hoge=10, foo=20))
    with pytest.raises(ValueError):
        typecheck(Dict[str, int], dict(hoge=10.0, foo=20))

    # Dict of dataclasses
    typecheck(Dict[Str, Int], {Str('hoge'): Int(10), Str('foo'): Int(20)})
    with pytest.raises(ValueError):
        typecheck(Dict[Str, Int], {Str('hoge'): Int(10.0), Str('foo'): Int(20)})

    # Optional
    typecheck(Optional[int], 10)
    typecheck(Optional[int], None)
    with pytest.raises(ValueError):
        typecheck(Optional[int], 10.0)

    # Optional of dataclass
    typecheck(Optional[Int], Int(10))
    typecheck(Optional[Int], None)
    with pytest.raises(ValueError):
        typecheck(Optional[Int], 10.0)
        typecheck(Optional[Int], Int(10.0))
