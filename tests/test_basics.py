import dataclasses
import decimal
import enum
import ipaddress
import itertools
import logging
import os
import pathlib
import sys
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Set, Tuple

import more_itertools
import pytest

import serde.compat
from serde import SerdeError, deserialize, from_dict, from_tuple, serialize, to_dict, to_tuple
from serde.core import SERDE_SCOPE
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml

from . import data
from .data import Bool, Float, Int, ListPri, Pri, PriDefault, Str

log = logging.getLogger('test')

serde.init(True)

format_dict: List = [(to_dict, from_dict)]

format_tuple: List = [(to_tuple, from_tuple)]

format_json: List = [(to_json, from_json)]

format_msgpack: List = [(to_msgpack, from_msgpack)]

format_yaml: List = [(to_yaml, from_yaml)]

format_toml: List = [(to_toml, from_toml)]

all_formats: List = format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_toml

opt_case: List = [
    {'reuse_instances_default': False},
    {'reuse_instances_default': False, 'rename_all': 'camelcase'},
    {'reuse_instances_default': False, 'rename_all': 'snakecase'},
]

types: List = [
    (10, int),  # Primitive
    ('foo', str),
    (100.0, float),
    (True, bool),
    (10, Optional[int]),  # Optional
    (None, Optional[int]),
    ([1, 2], List[int]),  # Container
    ([1, 2], List),
    ([1, 2], list),
    ([], List[int]),
    ({1, 2}, Set[int]),
    ({1, 2}, Set),
    ({1, 2}, set),
    (set(), Set[int]),
    ((1, 1), Tuple[int, int]),
    ((1, 1), Tuple),
    ({'a': 1}, Dict[str, int]),
    ({'a': 1}, Dict),
    ({'a': 1}, dict),
    ({}, Dict[str, int]),
    (Pri(10, 'foo', 100.0, True), Pri),  # dataclass
    (Pri(10, 'foo', 100.0, True), Optional[Pri]),
    (None, Optional[Pri]),
    (pathlib.Path('/tmp/foo'), pathlib.Path),  # Extended types
    (pathlib.Path('/tmp/foo'), Optional[pathlib.Path]),
    (None, Optional[pathlib.Path]),
    (pathlib.PurePath('/tmp/foo'), pathlib.PurePath),
    (pathlib.PurePosixPath('/tmp/foo'), pathlib.PurePosixPath),
    (pathlib.PureWindowsPath('C:\\tmp'), pathlib.PureWindowsPath),
    (uuid.UUID("8f85b32c-a0be-466c-87eb-b7bbf7a01683"), uuid.UUID),
    (ipaddress.IPv4Address("127.0.0.1"), ipaddress.IPv4Address),
    (ipaddress.IPv6Address("::1"), ipaddress.IPv6Address),
    (ipaddress.IPv4Network("127.0.0.0/8"), ipaddress.IPv4Network),
    (ipaddress.IPv6Network("::/128"), ipaddress.IPv6Network),
    (ipaddress.IPv4Interface("192.168.1.1/24"), ipaddress.IPv4Interface),
    (ipaddress.IPv6Interface("::1/128"), ipaddress.IPv6Interface),
    (decimal.Decimal(10), decimal.Decimal),
    (datetime.now(), datetime),
    (date.today(), date),
]

# these types can only be instantiated on their corresponding system
if os.name == "posix":
    types.append((pathlib.PosixPath('/tmp/foo'), pathlib.PosixPath))
if os.name == "nt":
    types.append((pathlib.WindowsPath('C:\\tmp'), pathlib.WindowsPath))

if sys.version_info[:3] >= (3, 9, 0):
    types.extend([([1, 2], list[int]), ({'a': 1}, dict[str, int]), ((1, 1), tuple[int, int])])

types_combinations: List = list(map(lambda c: list(more_itertools.flatten(c)), itertools.combinations(types, 2)))


def make_id_from_dict(d: Dict) -> str:
    if not d:
        return 'none'
    else:
        key = list(d)[0]
        return f'{key}-{d[key]}'


def opt_case_ids():
    return list(map(make_id_from_dict, opt_case))


def type_ids():
    from serde.compat import typename

    def make_id(pair: Tuple):
        t, T = pair
        return f'{typename(T)}({t})'

    return list(map(make_id, types))


def type_combinations_ids():
    from serde.compat import typename

    def make_id(quad: Tuple):
        t, T, u, U = quad
        return f'{typename(T)}({t})-{typename(U)}({u})'

    return list(map(make_id, types_combinations))


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

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class Nested:
        t: T

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class C:
        n: Nested

    c = C(Nested(t))
    assert c == de(C, se(c))


@pytest.mark.parametrize('t,T', types, ids=type_ids())
@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', (format_dict + format_tuple))
def test_simple_with_reuse_instances(se, de, opt, t, T):
    log.info(f'Running test with se={se.__name__} de={de.__name__} opts={opt} while reusing instances')

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class C:
        i: int
        t: T

    c = C(10, t)
    assert c == de(C, se(c, reuse_instances=True), reuse_instances=True)

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class Nested:
        t: T

    @deserialize(**opt)
    @serialize(**opt)
    @dataclass
    class C:
        n: Nested

    c = C(Nested(t))
    assert c == de(C, se(c, reuse_instances=True), reuse_instances=True)


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
    class Variant:
        d: List

    # List can contain different types (except Toml).
    if se is not to_toml:
        p = Variant([10, 'foo', 10.0, True])
        assert p == de(Variant, se(p))


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_dict(se, de, opt):
    from .data import PriDict

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
    class Variant:
        d: Dict[int, str]

    p = Variant({'10': 10, 'foo': 'bar', '100.0': 100.0, 'True': False})
    assert p == de(Variant, se(p))


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_enum(se, de, opt):
    from serde.compat import is_enum

    from .data import IE, E

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

    assert {'foo': 'bar', 'items': {}} == to_dict(f)
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


def test_msgpack_unnamed():
    p = Pri(10, 'foo', 100.0, True)
    d = b'\x94\n\xa3foo\xcb@Y\x00\x00\x00\x00\x00\x00\xc3'
    assert d == to_msgpack(p, named=False)
    assert p == from_msgpack(Pri, d, named=False)


@pytest.mark.parametrize('se,de', all_formats)
def test_rename(se, de):
    @deserialize
    @serialize
    @dataclass
    class Foo:
        class_name: str = field(metadata={'serde_rename': 'class'})

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f))


@pytest.mark.parametrize('se,de', format_msgpack)
def test_rename_msgpack(se, de):
    @deserialize(rename_all='camelcase')
    @serialize(rename_all='camelcase')
    @dataclass
    class Foo:
        class_name: str

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f, named=True), named=True)
    assert f == de(Foo, se(f, named=False), named=False)


@pytest.mark.parametrize('se,de', (format_dict + format_json + format_yaml + format_toml))
def test_rename_formats(se, de):
    @deserialize(rename_all='camelcase')
    @serialize(rename_all='camelcase')
    @dataclass
    class Foo:
        class_name: str

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f))


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


@pytest.mark.parametrize('se,de', (format_msgpack))
def test_ext(se, de):
    @deserialize
    @serialize
    @dataclass
    class Base:
        i: int
        s: str

    @deserialize
    @serialize
    @dataclass
    class DerivedA(Base):
        j: int

    @deserialize
    @serialize
    @dataclass
    class DerivedB(Base):
        k: float

    a = DerivedA(i=7, s="A", j=13)
    aa = de(Base, se(a))
    assert aa != a

    EXT_TYPE_DICT = {0: DerivedA, 1: DerivedB}
    # reverse the external type dict for faster serialization
    EXT_TYPE_DICT_REVERSED = {v: k for k, v in EXT_TYPE_DICT.items()}

    a = DerivedA(i=7, s="A", j=13)
    aa = de(None, se(a, ext_dict=EXT_TYPE_DICT_REVERSED), ext_dict=EXT_TYPE_DICT)
    assert aa == a

    b = DerivedB(i=3, s="B", k=11.0)
    bb = de(None, se(b, ext_dict=EXT_TYPE_DICT_REVERSED), ext_dict=EXT_TYPE_DICT)
    assert b == bb

    with pytest.raises(SerdeError) as se_ex:
        se(a, ext_dict={})
    assert str(se_ex.value) == "Could not find type code for DerivedA in ext_dict"

    with pytest.raises(SerdeError) as de_ex:
        de(None, se(a, ext_dict=EXT_TYPE_DICT_REVERSED), ext_dict={})
    assert str(de_ex.value) == "Could not find type for code 0 in ext_dict"


def test_exception_on_not_supported_types():
    class UnsupportedClass:
        def __init__(self):
            pass

    @deserialize
    @serialize
    @dataclass
    class Foo:
        b: UnsupportedClass

    with pytest.raises(SerdeError) as se_ex:
        to_dict(Foo(UnsupportedClass()))
    assert str(se_ex.value).startswith("Unsupported type: UnsupportedClass")

    with pytest.raises(SerdeError) as de_ex:
        from_dict(Foo, {"b": UnsupportedClass()})
    assert str(de_ex.value).startswith("Unsupported type: UnsupportedClass")


def test_dataclass_inheritance():
    @deserialize
    @serialize
    @dataclass
    class Base:
        i: int
        s: str

    @deserialize
    @serialize
    @dataclass
    class DerivedA(Base):
        j: int

    @deserialize
    @serialize
    @dataclass
    class DerivedB(Base):
        k: float

    # each class should have own scope
    # ensure the generated code of DerivedB does not overwrite the earlier generated code from DerivedA
    assert getattr(Base, SERDE_SCOPE) is not getattr(DerivedA, SERDE_SCOPE)
    assert getattr(DerivedA, SERDE_SCOPE) is not getattr(DerivedB, SERDE_SCOPE)

    base = Base(i=0, s="foo")
    assert base == from_dict(Base, to_dict(base))

    a = DerivedA(i=0, s="foo", j=42)
    assert a == from_dict(DerivedA, to_dict(a))

    b = DerivedB(i=0, s="foo", k=42.0)
    assert b == from_dict(DerivedB, to_dict(b))
