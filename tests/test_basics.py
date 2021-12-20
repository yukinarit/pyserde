import dataclasses
import enum
import logging
import uuid
from typing import Dict, List, Optional, Tuple

import pytest

import serde

from . import data
from .common import (
    all_formats,
    format_dict,
    format_json,
    format_msgpack,
    format_toml,
    format_tuple,
    format_yaml,
    opt_case,
    opt_case_ids,
    type_ids,
    types,
)

log = logging.getLogger('test')

serde.init(True)


@pytest.mark.parametrize('t,T', types, ids=type_ids())
@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_simple(se, de, opt, t, T):
    log.info(f'Running test with se={se.__name__} de={de.__name__} opts={opt}')

    @serde.serde(**opt)
    class C:
        i: int
        t: T

    c = C(10, t)
    assert c == de(C, se(c))

    @serde.serde(**opt)
    class Nested:
        t: T

    @serde.serde(**opt)
    class C:
        n: Nested

    c = C(Nested(t))
    assert c == de(C, se(c))

    if se is not serde.toml.to_toml:
        assert t == de(T, se(t))


@pytest.mark.parametrize('t,T', types, ids=type_ids())
@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', (format_dict + format_tuple))
def test_simple_with_reuse_instances(se, de, opt, t, T):
    log.info(f'Running test with se={se.__name__} de={de.__name__} opts={opt} while reusing instances')

    @serde.serde(**opt)
    class C:
        i: int
        t: T

    c = C(10, t)
    assert c == de(C, se(c, reuse_instances=True), reuse_instances=True)

    @serde.serde(**opt)
    class Nested:
        t: T

    @serde.serde(**opt)
    class C:
        n: Nested

    c = C(Nested(t))
    assert c == de(C, se(c, reuse_instances=True), reuse_instances=True)


def test_non_dataclass():
    @serde.serde
    class Foo:
        i: int

    @serde.serialize
    class Bar:
        i: int

    @serde.deserialize
    class Baz:
        i: int


# test_string_forward_reference_works currently only works with global visible classes
# and can not be mixed with PEP 563 "from __future__ import annotations"
@dataclasses.dataclass
class ForwardReferenceFoo:
    bar: 'ForwardReferenceBar'


@serde.serde
class ForwardReferenceBar:
    i: int


# assert type is str
assert 'ForwardReferenceBar' == dataclasses.fields(ForwardReferenceFoo)[0].type

# setup pyserde for Foo after Bar becomes visible to global scope
serde.serde(ForwardReferenceFoo)

# now the type really is of type Bar
assert ForwardReferenceBar == dataclasses.fields(ForwardReferenceFoo)[0].type
assert ForwardReferenceBar == next(serde.compat.dataclass_fields(ForwardReferenceFoo)).type


# verify usage works
def test_string_forward_reference_works():
    h = ForwardReferenceFoo(bar=ForwardReferenceBar(i=10))
    h_dict = {"bar": {"i": 10}}

    assert serde.to_dict(h) == h_dict
    assert serde.from_dict(ForwardReferenceFoo, h_dict) == h


# trying to use string forward reference normally will throw
def test_unresolved_forward_reference_throws():
    with pytest.raises(serde.SerdeError) as e:

        @serde.serde
        class UnresolvedForwardFoo:
            bar: 'UnresolvedForwardBar'

        @serde.serde
        class UnresolvedForwardBar:
            i: int

    assert "Failed to resolve type hints for UnresolvedForwardFoo" in str(e)


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_list(se, de, opt):
    @serde.serde(**opt)
    class Variant:
        d: List

    # List can contain different types (except Toml).
    if se is not serde.toml.to_toml:
        p = Variant([10, 'foo', 10.0, True])
        assert p == de(Variant, se(p))


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_dict(se, de, opt):
    from .data import PriDict

    if se in (serde.json.to_json, serde.msgpack.to_msgpack, serde.toml.to_toml):
        # JSON, Msgpack, Toml don't allow non string key.
        p = PriDict({'10': 10}, {'foo': 'bar'}, {'100.0': 100.0}, {'True': False})
        assert p == de(PriDict, se(p))
    else:
        p = PriDict({10: 10}, {'foo': 'bar'}, {100.0: 100.0}, {True: False})
        assert p == de(PriDict, se(p))

    @serde.serde(**opt)
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

    @serde.serde(**opt)
    class Foo:
        a: E
        b: IE
        c: NestedEnum
        d: E = E.S
        e: IE = IE.V1
        f: NestedEnum = NestedEnum.V

    f = Foo(E.S, IE.V0, NestedEnum.V)
    ff = de(Foo, se(f))
    assert f == ff
    assert is_enum(ff.a) and isinstance(ff.a, E)
    assert is_enum(ff.b) and isinstance(ff.b, IE)
    assert is_enum(ff.c) and isinstance(ff.c, NestedEnum)
    assert is_enum(ff.d) and isinstance(ff.d, E)
    assert is_enum(ff.e) and isinstance(ff.e, IE)
    assert is_enum(ff.f) and isinstance(ff.f, NestedEnum)

    # pyserde automatically convert enum compatible value.
    f = Foo('foo', 2, Inner.V0, True, 10, Inner.V0)
    ff = de(Foo, se(f))
    assert is_enum(ff.a) and isinstance(ff.a, E) and ff.a == E.S
    assert is_enum(ff.b) and isinstance(ff.b, IE) and ff.b == IE.V1
    assert is_enum(ff.c) and isinstance(ff.c, NestedEnum) and ff.c == NestedEnum.V
    assert is_enum(ff.d) and isinstance(ff.d, E) and ff.d == E.B
    assert is_enum(ff.e) and isinstance(ff.e, IE) and ff.e == IE.V2
    assert is_enum(ff.f) and isinstance(ff.f, NestedEnum) and ff.f == NestedEnum.V


@pytest.mark.parametrize('se,de', all_formats)
def test_enum_imported(se, de):
    from .data import EnumInClass

    c = EnumInClass()
    cc = de(EnumInClass, se(c))
    assert c == cc


@pytest.mark.parametrize('opt', opt_case, ids=opt_case_ids())
@pytest.mark.parametrize('se,de', all_formats)
def test_tuple(se, de, opt):
    @serde.serde(**opt)
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

    @serde.serde(**opt)
    class Variant:
        t: Tuple[int, str, float, bool]

    # Toml doesn't support variant type of array.
    if se is not serde.toml.to_toml:
        p = Variant((10, 'a', 10.0, True))
        assert p == de(Variant, se(p))

    @serde.serde(**opt)
    class BareTuple:
        t: Tuple

    p = BareTuple((10, 20))
    assert p == de(BareTuple, se(p))

    @serde.serde(**opt)
    class Nested:
        i: Tuple[data.Int, data.Int]
        s: Tuple[data.Str, data.Str]
        f: Tuple[data.Float, data.Float]
        b: Tuple[data.Bool, data.Bool]

    # hmmm.. Nested tuple doesn't work ..
    if se is not serde.toml.to_toml:
        p = Nested(
            (data.Int(10), data.Int(20)),
            (data.Str("a"), data.Str("b")),
            (data.Float(10.0), data.Float(20.0)),
            (data.Bool(True), data.Bool(False)),
        )
        assert p == de(Nested, se(p))


@pytest.mark.parametrize('se,de', all_formats)
def test_single_element_tuples(se, de):
    @serde.serde
    class Foo:
        a: Tuple[int]
        b: Tuple[uuid.UUID]

    foo = Foo(a=(1,), b=(uuid.UUID("855f07da-c3cd-46f2-9557-b8dbeb99ff42"),))
    assert serde.to_dict(foo) == {"a": foo.a, "b": foo.b}

    assert foo == de(Foo, se(foo))


@pytest.mark.parametrize('se,de', all_formats)
def test_dataclass_default_factory(se, de):
    @serde.serde
    class Foo:
        foo: str
        items: Dict[str, int] = serde.field(default_factory=dict)

    f = Foo('bar')
    assert f == de(Foo, se(f))

    assert {'foo': 'bar', 'items': {}} == serde.to_dict(f)
    assert f == serde.from_dict(Foo, {'foo': 'bar'})


@pytest.mark.parametrize('se,de', all_formats)
def test_default(se, de):
    from serde import from_dict, from_tuple

    from .data import OptDefault, PriDefault

    p = PriDefault()
    assert p == de(PriDefault, se(p))

    p = PriDefault()
    assert p == from_dict(PriDefault, {})
    assert p == from_dict(PriDefault, {'i': 10})
    assert p == from_dict(PriDefault, {'i': 10, 's': 'foo'})
    assert p == from_dict(PriDefault, {'i': 10, 's': 'foo', 'f': 100.0})
    assert p == from_dict(PriDefault, {'i': 10, 's': 'foo', 'f': 100.0, 'b': True})
    assert p == from_tuple(PriDefault, (10, 'foo', 100.0, True))

    o = OptDefault()
    assert o == de(OptDefault, se(o))

    o = OptDefault()
    assert o == from_dict(OptDefault, {})
    assert o == from_dict(OptDefault, {"n": None})
    assert o == from_dict(OptDefault, {"n": None, "i": 10})
    assert o == from_tuple(OptDefault, (None, 10))

    o = OptDefault(n=None, i=None)
    assert o == from_dict(OptDefault, {"n": None, "i": None})
    assert o == from_tuple(OptDefault, (None, None))

    assert 10 == dataclasses.fields(PriDefault)[0].default
    assert 'foo' == dataclasses.fields(PriDefault)[1].default
    assert 100.0 == dataclasses.fields(PriDefault)[2].default
    assert True is dataclasses.fields(PriDefault)[3].default


@pytest.mark.parametrize('se,de', (format_dict + format_tuple + format_json + format_msgpack + format_yaml))
def test_list_pri(se, de):
    p = [data.PRI, data.PRI]
    assert p == de(data.ListPri, se(p))

    p = []
    assert p == de(data.ListPri, se(p))


@pytest.mark.parametrize('se,de', (format_dict + format_tuple + format_json + format_msgpack + format_yaml))
def test_dict_pri(se, de):
    p = {'1': data.PRI, '2': data.PRI}
    assert p == de(data.DictPri, se(p))

    p = {}
    assert p == de(data.DictPri, se(p))


def test_json():
    p = data.Pri(10, 'foo', 100.0, True)
    s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
    assert s == serde.json.to_json(p)

    assert '10' == serde.json.to_json(10)
    assert '[10, 20, 30]' == serde.json.to_json([10, 20, 30])
    assert '{"foo": 10, "fuga": 10}' == serde.json.to_json({'foo': 10, 'fuga': 10})


def test_msgpack():
    p = data.Pri(10, 'foo', 100.0, True)
    d = b'\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3'
    assert d == serde.msgpack.to_msgpack(p)
    assert p == serde.msgpack.from_msgpack(data.Pri, d)


def test_msgpack_unnamed():
    p = data.Pri(10, 'foo', 100.0, True)
    d = b'\x94\n\xa3foo\xcb@Y\x00\x00\x00\x00\x00\x00\xc3'
    assert d == serde.msgpack.to_msgpack(p, named=False)
    assert p == serde.msgpack.from_msgpack(data.Pri, d, named=False)


@pytest.mark.parametrize('se,de', all_formats)
def test_rename(se, de):
    @serde.serde
    class Foo:
        class_name: str = serde.field(rename='class')

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f))


@pytest.mark.parametrize('se,de', format_msgpack)
def test_rename_msgpack(se, de):
    @serde.serde(rename_all='camelcase')
    class Foo:
        class_name: str

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f, named=True), named=True)
    assert f == de(Foo, se(f, named=False), named=False)


@pytest.mark.parametrize('se,de', (format_dict + format_json + format_yaml + format_toml))
def test_rename_formats(se, de):
    @serde.serde(rename_all='camelcase')
    class Foo:
        class_name: str

    f = Foo(class_name='foo')
    assert f == de(Foo, se(f))


@pytest.mark.parametrize('se,de', (format_dict + format_json + format_msgpack + format_yaml + format_toml))
def test_skip_if(se, de):
    @serde.serde
    class Foo:
        comments: Optional[List[str]] = serde.field(default_factory=list, skip_if=lambda v: len(v) == 0)
        attrs: Optional[Dict[str, str]] = serde.field(default_factory=dict, skip_if=lambda v: v is None or len(v) == 0)

    f = Foo(['foo'], {"bar": "baz"})
    assert f == de(Foo, se(f))

    f = Foo([])
    ff = de(Foo, se(f))
    assert ff.comments == []
    assert ff.attrs == {}


@pytest.mark.parametrize('se,de', all_formats)
def test_skip_if_false(se, de):
    @serde.serde
    class Foo:
        comments: Optional[List[str]] = serde.field(default_factory=list, skip_if_false=True)

    f = Foo(['foo'])
    assert f == de(Foo, se(f))


@pytest.mark.parametrize('se,de', (format_dict + format_json + format_msgpack + format_yaml + format_toml))
def test_skip_if_overrides_skip_if_false(se, de):
    @serde.serde
    class Foo:
        comments: Optional[List[str]] = serde.field(
            default_factory=list, skip_if_false=True, skip_if=lambda v: len(v) == 1
        )

    f = Foo(['foo'])
    ff = de(Foo, se(f))
    assert ff.comments == []


@pytest.mark.parametrize('se,de', all_formats)
def test_skip_if_default(se, de):
    @serde.serde
    class Foo:
        a: str = serde.field(default='foo', skip_if_default=True)

    f = Foo()
    assert f == de(Foo, se(f))

    assert serde.to_dict(Foo()) == {}
    assert serde.to_dict(Foo('bar')) == {'a': 'bar'}
    assert serde.from_dict(Foo, {}) == Foo()
    assert serde.from_dict(Foo, {'a': 'bar'}) == Foo('bar')


@pytest.mark.parametrize('se,de', format_msgpack)
def test_inheritance(se, de):
    @serde.serde
    class Base:
        a: int
        b: str

    @serde.serde
    class Derived(Base):
        c: float

    base = Base(10, "foo")
    assert base == de(Base, se(base))

    derived = Derived(10, "foo", 100.0)
    assert derived == de(Derived, se(derived))


@pytest.mark.parametrize('se,de', format_msgpack)
def test_ext(se, de):
    @serde.serde
    class Base:
        i: int
        s: str

    @serde.serde
    class DerivedA(Base):
        j: int

    @serde.serde
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

    with pytest.raises(serde.SerdeError) as se_ex:
        se(a, ext_dict={})
    assert str(se_ex.value) == "Could not find type code for DerivedA in ext_dict"

    with pytest.raises(serde.SerdeError) as de_ex:
        de(None, se(a, ext_dict=EXT_TYPE_DICT_REVERSED), ext_dict={})
    assert str(de_ex.value) == "Could not find type for code 0 in ext_dict"


def test_exception_on_not_supported_types():
    class UnsupportedClass:
        def __init__(self):
            pass

    @serde.serde
    class Foo:
        b: UnsupportedClass

    with pytest.raises(serde.SerdeError) as se_ex:
        serde.to_dict(Foo(UnsupportedClass()))
    assert str(se_ex.value).startswith("Unsupported type: UnsupportedClass")

    with pytest.raises(serde.SerdeError) as de_ex:
        serde.from_dict(Foo, {"b": UnsupportedClass()})
    assert str(de_ex.value).startswith("Unsupported type: UnsupportedClass")


def test_dataclass_inheritance():
    @serde.serde
    class Base:
        i: int
        s: str

    @serde.serde
    class DerivedA(Base):
        j: int

    @serde.serde
    class DerivedB(Base):
        k: float

    # each class should have own scope
    # ensure the generated code of DerivedB does not overwrite the earlier generated code from DerivedA
    assert getattr(Base, serde.core.SERDE_SCOPE) is not getattr(DerivedA, serde.core.SERDE_SCOPE)
    assert getattr(DerivedA, serde.core.SERDE_SCOPE) is not getattr(DerivedB, serde.core.SERDE_SCOPE)

    base = Base(i=0, s="foo")
    assert base == serde.from_dict(Base, serde.to_dict(base))

    a = DerivedA(i=0, s="foo", j=42)
    assert a == serde.from_dict(DerivedA, serde.to_dict(a))

    b = DerivedB(i=0, s="foo", k=42.0)
    assert b == serde.from_dict(DerivedB, serde.to_dict(b))
