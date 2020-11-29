import dataclasses
import decimal
import enum
import itertools
import logging
import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import pytest

import more_itertools
import serde
import serde.compat
from serde import asdict, astuple, deserialize, from_dict, from_tuple, serialize
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml

from . import data
from .data import Bool, Float, Int, ListPri, NestedPri, NestedPriOpt, Pri, PriDefault, PriOpt, Str

log = logging.getLogger('test')

serde.init(True)

format_dict: List = [(asdict, from_dict)]

format_tuple: List = [(astuple, from_tuple)]

format_json: List = [(to_json, from_json)]

format_msgpack: List = [(to_msgpack, from_msgpack)]

format_yaml: List = [(to_yaml, from_yaml)]

format_toml: List = [(to_toml, from_toml)]

all_formats: List = format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_toml

opt_case: List = [{}, {'rename_all': 'camelcase'}, {'rename_all': 'snakecase'}]

types: List = [
    (10, int),  # Primitive
    ('foo', str),
    (100.0, float),
    (True, bool),
    (10, Optional[int]),  # Optional
    ('foo', Optional[str]),
    (100.0, Optional[float]),
    (True, Optional[bool]),
    (None, Optional[int]),
    (None, Optional[str]),
    (None, Optional[float]),
    (None, Optional[bool]),
    (Pri(10, 'foo', 100.0, True), Pri),  # dataclass
    (Pri(10, 'foo', 100.0, True), Optional[Pri]),
    (None, Optional[Pri]),
    (pathlib.Path('/tmp/foo'), pathlib.Path),  # Extended types
    (pathlib.Path('/tmp/foo'), Optional[pathlib.Path]),
    (None, Optional[pathlib.Path]),
    (decimal.Decimal(10), decimal.Decimal),
]

types_combinations: List = list(map(lambda c: list(more_itertools.flatten(c)), itertools.combinations(types, 2)))


def make_id_from_dict(d: Dict) -> str:
    if not d:
        return 'none'
    else:
        key = list(d)[0]
        return f'{key}-{d[key]}'


def opt_case_ids():
    return map(make_id_from_dict, opt_case)


def type_ids():
    from serde.compat import typename

    def make_id(pair: Tuple):
        t, T = pair
        return f'{typename(T)}({t})'

    return map(make_id, types)


def type_combinations_ids():
    from serde.compat import typename

    def make_id(quad: Tuple):
        t, T, u, U = quad
        return f'{typename(T)}({t})-{typename(U)}({u})'

    return map(make_id, types_combinations)


@pytest.mark.parametrize('t,T', types, ids=type_ids())
@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_simple(se, de, opt, t, T):
    log.info(f'Running test with se={se.__name__} de={de.__name__} opts={opt}')

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class C:
        i: int
        t: T

    c = C(10, t)
    assert c == de(C, se(c))


def test_non_dataclass():
    with pytest.raises(TypeError):

        @deserialize
        @serialize
        class Foo:
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

    assert 'Bar' == dataclasses.fields(Foo)[0].type


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_list(se, de, opt):
    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class PriList:
        i: List[int]
        s: List[str]
        f: List[float]
        b: List[bool]

    p = PriList([10, 10], ['foo', 'bar'], [10.0, 10.0], [True, False])
    assert p == de(PriList, se(p))

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class BareList:
        i: List

    p = BareList([10])
    assert p == de(BareList, se(p))

    # List can contain different types (except Toml).
    if se is not to_toml:
        p = BareList([10, 'foo', 10.0, True])
        assert p == de(BareList, se(p))


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_dict(se, de, opt):
    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class PriDict:
        i: Dict[int, int]
        s: Dict[str, str]
        f: Dict[float, float]
        b: Dict[bool, bool]

    if se in (to_json, to_msgpack, to_toml):
        # JSON, Msgpack, Toml don't allow non string key.
        p = PriDict({'10': 10}, {'foo': 'bar'}, {'100.0': 100.0}, {'True': False})
        assert p == de(PriDict, se(p))
    else:
        p = PriDict({10: 10}, {'foo': 'bar'}, {100.0: 100.0}, {True: False})
        assert p == de(PriDict, se(p))

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class BareDict:
        d: Dict

    p = BareDict({'10': 10})
    assert p == de(BareDict, se(p))

    p = BareDict({'10': 10, 'foo': 'bar', '100.0': 100.0, 'True': False})
    assert p == de(BareDict, se(p))


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_enum(se, de, opt):
    from .data import E, IE
    from serde.compat import is_enum

    class Inner(enum.IntEnum):
        V0 = enum.auto()
        V1 = enum.auto()
        V2 = enum.auto()

    class NestedEnum(enum.Enum):
        V = Inner.V0

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class Foo:
        e: E
        ie: IE
        ne: NestedEnum
        e2: E = E.S
        ie2: IE = IE.V1
        ne2: NestedEnum = NestedEnum.V

    f = Foo(E.I, IE.V0, NestedEnum.V)
    ff = de(Foo, se(f))
    assert f == ff
    assert is_enum(ff.e) and isinstance(ff.e, E)
    assert is_enum(ff.ie) and isinstance(ff.ie, IE)
    assert is_enum(ff.ne) and isinstance(ff.ne, NestedEnum)
    assert is_enum(ff.e2) and isinstance(ff.e2, E)
    assert is_enum(ff.ie2) and isinstance(ff.ie2, IE)
    assert is_enum(ff.ne2) and isinstance(ff.ne2, NestedEnum)

    # pyserde automatically convert enum compatible value.
    f = Foo('foo', 2, Inner.V0, True, 10, Inner.V0)
    ff = de(Foo, se(f))
    assert is_enum(ff.e) and isinstance(ff.e, E) and ff.e == E.S
    assert is_enum(ff.ie) and isinstance(ff.ie, IE) and ff.ie == IE.V1
    assert is_enum(ff.ne) and isinstance(ff.ne, NestedEnum) and ff.ne == NestedEnum.V
    assert is_enum(ff.e2) and isinstance(ff.e2, E) and ff.e2 == E.B
    assert is_enum(ff.ie2) and isinstance(ff.ie2, IE) and ff.ie2 == IE.V2
    assert is_enum(ff.ne2) and isinstance(ff.ne2, NestedEnum) and ff.ne2 == NestedEnum.V


@pytest.mark.parametrize('se,de', all_formats)
def test_enum_imported(se, de):
    from .data import EnumInClass

    c = EnumInClass()
    cc = de(EnumInClass, se(c))
    assert c == cc


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_tuple(se, de, opt):
    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class Homogeneous:
        i: Tuple[int, int]
        s: Tuple[str, str]
        f: Tuple[float, float]
        b: Tuple[bool, bool]

    p = Homogeneous((10, 20), ('a', 'b'), (10.0, 20.0), (True, False))
    assert p == de(Homogeneous, se(p))

    # List can also be used.
    p = Homogeneous([10, 20], ['a', 'b'], [10.0, 20.0], [True, False])
    assert p != de(Homogeneous, se(p))

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class Variant:
        t: Tuple[int, str, float, bool]

    # Toml doesn't support variant type of array.
    if se is not to_toml:
        p = Variant((10, 'a', 10.0, True))
        assert p == de(Variant, se(p))

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class BareTuple:
        t: Tuple

    p = BareTuple((10, 20))
    assert p == de(BareTuple, se(p))

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class Nested:
        i: Tuple[Int, Int]
        s: Tuple[Str, Str]
        f: Tuple[Float, Float]
        b: Tuple[Bool, Bool]

    # hmmm.. Nested tuple doesn't work ..
    if se is not to_toml:
        p = Nested((Int(10), Int(20)), (Str("a"), Str("b")), (Float(10.0), Float(20.0)), (Bool(True), Bool(False)))
        assert p == de(Nested, se(p))


@pytest.mark.parametrize('se,de', all_formats)
def test_dataclass_default_factory(se, de):
    @deserialize
    @serialize
    @dataclass
    class Foo:
        foo: str
        items: Dict[str, int] = field(default_factory=dict)

    f = Foo('bar')
    assert f == de(Foo, se(f))

    assert {'foo': 'bar', 'items': {}} == asdict(f)
    assert f == from_dict(Foo, {'foo': 'bar'})


@pytest.mark.parametrize('se,de', all_formats)
def test_default(se, de):
    p = PriDefault()
    assert p == de(PriDefault, se(p))

    p = PriDefault()
    assert p == from_dict(PriDefault, {})
    assert p == from_dict(PriDefault, {'i': 10})
    assert p == from_dict(PriDefault, {'i': 10, 's': 'foo'})
    assert p == from_dict(PriDefault, {'i': 10, 's': 'foo', 'f': 100.0})
    assert p == from_dict(PriDefault, {'i': 10, 's': 'foo', 'f': 100.0, 'b': True})

    assert 10 == dataclasses.fields(PriDefault)[0].default
    assert 'foo' == dataclasses.fields(PriDefault)[1].default
    assert 100.0 == dataclasses.fields(PriDefault)[2].default
    assert True is dataclasses.fields(PriDefault)[3].default


@pytest.mark.parametrize('se,de', (format_dict + format_tuple + format_json + format_msgpack + format_yaml))
def test_list_pri(se, de):
    p = [data.PRI, data.PRI]
    assert p == de(ListPri, se(p))

    p = []
    assert p == de(ListPri, se(p))


@pytest.mark.parametrize('se,de', (format_dict + format_tuple + format_json + format_msgpack + format_yaml))
def test_dict_pri(se, de):
    p = {'1': data.PRI, '2': data.PRI}
    assert p == de(data.DictPri, se(p))

    p = {}
    assert p == de(data.DictPri, se(p))


def test_json():
    p = Pri(10, 'foo', 100.0, True)
    s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
    assert s == to_json(p)

    assert '10' == to_json(10)
    assert '[10, 20, 30]' == to_json([10, 20, 30])
    assert '{"foo": 10, "fuga": 10}' == to_json({'foo': 10, 'fuga': 10})


def test_msgpack():
    p = Pri(10, 'foo', 100.0, True)
    d = b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3'
    assert d == to_msgpack(p)
    assert p == from_msgpack(Pri, d)


def test_msgpack_named():
    p = Pri(10, 'foo', 100.0, True)
    d = b'\x94\n\xa3foo\xcb@Y\x00\x00\x00\x00\x00\x00\xc3'
    assert d == to_msgpack(p, named=False)
    assert p == from_msgpack(Pri, d, named=False)


def test_from_dict():
    p = Pri(10, 'foo', 100.0, True)
    d = {'i': 10, 's': 'foo', 'f': 100.0, 'b': True}
    assert d == asdict(p)
    assert p == from_dict(Pri, d)

    p = {'p': Pri(10, 'foo', 100.0, True)}
    d = {'p': {'i': 10, 's': 'foo', 'f': 100.0, 'b': True}}
    assert d == asdict(p)
    assert p == from_dict(Dict[str, Pri], d)

    p = [Pri(10, 'foo', 100.0, True)]
    d = ({'i': 10, 's': 'foo', 'f': 100.0, 'b': True},)
    assert d == asdict(p)
    assert p == from_dict(List[Pri], d)

    p = (Pri(10, 'foo', 100.0, True),)
    d = ({'i': 10, 's': 'foo', 'f': 100.0, 'b': True},)
    assert d == asdict(p)
    assert p == from_dict(Tuple[Pri], d)


def test_from_tuple():
    p = Pri(10, 'foo', 100.0, True)
    d = (10, 'foo', 100.0, True)
    assert d == astuple(p)
    assert p == from_tuple(Pri, d)

    p = {'p': Pri(10, 'foo', 100.0, True)}
    d = {'p': (10, 'foo', 100.0, True)}
    assert d == astuple(p)
    assert p == from_tuple(Dict[str, Pri], d)

    p = [Pri(10, 'foo', 100.0, True)]
    d = ((10, 'foo', 100.0, True),)
    assert d == astuple(p)
    assert p == from_tuple(List[Pri], d)

    p = (Pri(10, 'foo', 100.0, True),)
    d = ((10, 'foo', 100.0, True),)
    assert d == astuple(p)
    assert p == from_tuple(Tuple[Pri], d)


@pytest.mark.parametrize('se,de', all_formats)
def test_rename(se, de):
    @deserialize
    @serialize
    @dataclass
    class Foo:
        class_name: str = field(metadata={'serde_rename': 'class'})

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f))


@pytest.mark.parametrize('se,de', format_json + format_yaml + format_toml + format_msgpack)
def test_rename_all(se, de):
    @deserialize(rename_all='camelcase')
    @serialize(rename_all='camelcase')
    @dataclass
    class Foo:
        class_name: str

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f, named=True), named=True)


@pytest.mark.parametrize('se,de', (format_dict + format_json + format_msgpack + format_yaml + format_toml))
def test_skip_if(se, de):
    @deserialize
    @serialize
    @dataclass
    class Foo:
        comments: Optional[List[str]] = field(default_factory=list, metadata={'serde_skip_if': lambda v: len(v) == 0})
        attrs: Optional[Dict[str, str]] = field(
            default_factory=dict, metadata={'serde_skip_if': lambda v: v is None or len(v) == 0}
        )

    f = Foo(['foo'], {"bar": "baz"})
    assert f == de(Foo, se(f))

    f = Foo([])
    ff = de(Foo, se(f))
    assert ff.comments == []
    assert ff.attrs == {}


@pytest.mark.parametrize('se,de', all_formats)
def test_skip_if_false(se, de):
    @deserialize
    @serialize
    @dataclass
    class Foo:
        comments: Optional[List[str]] = field(default_factory=list, metadata={'serde_skip_if_false': True})

    f = Foo(['foo'])
    assert f == de(Foo, se(f))


@pytest.mark.parametrize('se,de', (format_dict + format_json + format_msgpack + format_yaml + format_toml))
def test_skip_if_overrides_skip_if_false(se, de):
    @deserialize
    @serialize
    @dataclass
    class Foo:
        comments: Optional[List[str]] = field(
            default_factory=list, metadata={'serde_skip_if_false': True, 'serde_skip_if': lambda v: len(v) == 1}
        )

    f = Foo(['foo'])
    ff = de(Foo, se(f))
    assert ff.comments == []
