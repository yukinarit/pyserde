import dataclasses
import datetime
import enum
import logging
import pathlib
import uuid
from typing import (
    ClassVar,
    DefaultDict,
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

import pytest

import serde
from serde.core import Strict

from . import data
from .common import (
    all_formats,
    format_dict,
    format_json,
    format_msgpack,
    format_pickle,
    format_toml,
    format_tuple,
    format_yaml,
    opt_case,
    opt_case_ids,
    type_ids,
    types,
)

log = logging.getLogger("test")

serde.init(True)


@pytest.mark.parametrize("t,T,f", types, ids=type_ids())
@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_simple(se, de, opt, t, T, f):
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    if f(se, de, opt):
        return

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


@pytest.mark.parametrize("t,T,f", types, ids=type_ids())
@pytest.mark.parametrize("named", (True, False))
@pytest.mark.parametrize("reuse", (True, False))
def test_from_to_obj(t, T, f, named, reuse):
    obj = serde.se.to_obj(t, named, reuse, False)
    assert t == serde.de.from_obj(T, obj, named, reuse)


@pytest.mark.parametrize("t,T,filter", types, ids=type_ids())
@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", (format_dict + format_tuple))
def test_simple_with_reuse_instances(se, de, opt, t, T, filter):
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt} while reusing instances")

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
    bar: "ForwardReferenceBar"


@serde.serde
class ForwardReferenceBar:
    i: int


# assert type is str
assert "ForwardReferenceBar" == dataclasses.fields(ForwardReferenceFoo)[0].type

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
            bar: "UnresolvedForwardBar"

        @serde.serde
        class UnresolvedForwardBar:
            i: int

    assert "Failed to resolve type hints for UnresolvedForwardFoo" in str(e)


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_list(se, de, opt):
    @serde.serde(**opt)
    class Variant:
        d: List

    # List can contain different types (except Toml).
    if se is not serde.toml.to_toml:
        p = Variant([10, "foo", 10.0, True])
        assert p == de(Variant, se(p))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_dict_with_non_str_keys(se, de, opt):
    @serde.serde(**opt)
    class Foo:
        i: Dict[int, int]
        s: Dict[str, str]
        f: Dict[float, float]
        b: Dict[bool, bool]

    if se not in (serde.json.to_json, serde.msgpack.to_msgpack, serde.toml.to_toml):
        # JSON, Msgpack, Toml don't allow non string key.
        p = Foo({10: 10}, {"foo": "bar"}, {100.0: 100.0}, {True: False})
        assert p == de(Foo, se(p))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
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
    f = Foo("foo", 2, Inner.V0, True, 10, Inner.V0)
    try:
        data = se(f)
    except Exception:
        pass
    else:
        ff = de(Foo, data)
        assert is_enum(ff.a) and isinstance(ff.a, E) and ff.a == E.S
        assert is_enum(ff.b) and isinstance(ff.b, IE) and ff.b == IE.V1
        assert is_enum(ff.c) and isinstance(ff.c, NestedEnum) and ff.c == NestedEnum.V
        assert is_enum(ff.d) and isinstance(ff.d, E) and ff.d == E.B
        assert is_enum(ff.e) and isinstance(ff.e, IE) and ff.e == IE.V2
        assert is_enum(ff.f) and isinstance(ff.f, NestedEnum) and ff.f == NestedEnum.V


@pytest.mark.parametrize("se,de", all_formats)
def test_enum_imported(se, de):
    from .data import EnumInClass

    c = EnumInClass()
    se(c)
    cc = de(EnumInClass, se(c))
    assert c == cc


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_tuple(se, de, opt):
    @serde.serde(**opt)
    @dataclasses.dataclass
    class Homogeneous:
        i: Tuple[int, int]
        s: Tuple[str, str]
        f: Tuple[float, float]
        b: Tuple[bool, bool]

    a = Homogeneous((10, 20), ("a", "b"), (10.0, 20.0), (True, False))
    assert a == de(Homogeneous, se(a))

    # List will be type mismatch if type_check=True.
    a = Homogeneous([10, 20], ["a", "b"], [10.0, 20.0], [True, False])
    assert a != de(Homogeneous, se(a))

    @serde.serde(**opt)
    @dataclasses.dataclass
    class Variant:
        t: Tuple[int, str, float, bool]

    # Toml doesn't support variant type of array.
    if se is not serde.toml.to_toml:
        b = Variant((10, "a", 10.0, True))
        assert b == de(Variant, se(b))

    @serde.serde(**opt)
    @dataclasses.dataclass
    class BareTuple:
        t: Tuple

    c = BareTuple((10, 20))
    assert c == de(BareTuple, se(c))

    c = BareTuple(())
    assert c == de(BareTuple, se(c))

    @serde.serde(**opt)
    @dataclasses.dataclass
    class Nested:
        i: Tuple[data.Int, data.Int]
        s: Tuple[data.Str, data.Str]
        f: Tuple[data.Float, data.Float]
        b: Tuple[data.Bool, data.Bool]

    # hmmm.. Nested tuple doesn't work ..
    if se is not serde.toml.to_toml:
        d = Nested(
            (data.Int(10), data.Int(20)),
            (data.Str("a"), data.Str("b")),
            (data.Float(10.0), data.Float(20.0)),
            (data.Bool(True), data.Bool(False)),
        )
        assert d == de(Nested, se(d))

    @serde.serde(**opt)
    @dataclasses.dataclass
    class Inner:
        i: int

    @serde.serde(**opt)
    @dataclasses.dataclass
    class VariableTuple:
        t: Tuple[int, ...]
        i: Tuple[Inner, ...]

    e = VariableTuple((1, 2, 3), (Inner(0), Inner(1)))
    assert e == de(VariableTuple, se(e))

    e = VariableTuple((), ())
    assert e == de(VariableTuple, se(e))

    with pytest.raises(Exception):

        @serde.serde(**opt)
        @dataclasses.dataclass
        class EmptyTuple:
            t: Tuple[()]


@pytest.mark.parametrize("se,de", all_formats)
def test_single_element_tuples(se, de):
    @serde.serde
    class Foo:
        a: Tuple[int]
        b: Tuple[uuid.UUID]

    foo = Foo(a=(1,), b=(uuid.UUID("855f07da-c3cd-46f2-9557-b8dbeb99ff42"),))
    assert serde.to_dict(foo) == {"a": foo.a, "b": foo.b}

    assert foo == de(Foo, se(foo))


@pytest.mark.parametrize("se,de", all_formats)
def test_dataclass_default_factory(se, de):
    @serde.serde
    class Foo:
        foo: str
        items: Dict[str, int] = serde.field(default_factory=dict)

    f = Foo("bar")
    assert f == de(Foo, se(f))

    assert {"foo": "bar", "items": {}} == serde.to_dict(f)
    assert f == serde.from_dict(Foo, {"foo": "bar"})


@pytest.mark.parametrize("se,de", all_formats)
def test_default(se, de):
    from serde import from_dict, from_tuple

    from .data import OptDefault, PriDefault

    p = PriDefault()
    assert p == de(PriDefault, se(p))

    p = PriDefault()
    assert p == from_dict(PriDefault, {})
    assert p == from_dict(PriDefault, {"i": 10})
    assert p == from_dict(PriDefault, {"i": 10, "s": "foo"})
    assert p == from_dict(PriDefault, {"i": 10, "s": "foo", "f": 100.0})
    assert p == from_dict(PriDefault, {"i": 10, "s": "foo", "f": 100.0, "b": True})
    assert p == from_tuple(PriDefault, (10, "foo", 100.0, True))

    if se is not serde.toml.to_toml:  # Toml doesn't support None.
        o = OptDefault()
        assert o == de(OptDefault, se(o))
        o = OptDefault()
        assert o == from_dict(OptDefault, {})
        assert o == from_dict(OptDefault, {"n": None})
        assert o == from_dict(OptDefault, {"n": None, "i": 10})
        assert o == from_tuple(OptDefault, (None, 10))

    if se is not serde.toml.to_toml:
        o = OptDefault(n=None, i=None)
        assert o == from_dict(OptDefault, {"n": None, "i": None})
        assert o == from_tuple(OptDefault, (None, None))

    assert 10 == dataclasses.fields(PriDefault)[0].default
    assert "foo" == dataclasses.fields(PriDefault)[1].default
    assert 100.0 == dataclasses.fields(PriDefault)[2].default
    assert True is dataclasses.fields(PriDefault)[3].default


@pytest.mark.parametrize(
    "se,de", (format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_pickle)
)
def test_list_pri(se, de):
    p = [data.PRI, data.PRI]
    assert p == de(data.ListPri, se(p))

    p = []
    assert p == de(data.ListPri, se(p))


@pytest.mark.parametrize(
    "se,de", (format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_pickle)
)
def test_dict_pri(se, de):
    p = {"1": data.PRI, "2": data.PRI}
    assert p == de(data.DictPri, se(p))

    p = {}
    assert p == de(data.DictPri, se(p))


def test_json():
    p = data.Pri(10, "foo", 100.0, True)
    s = '{"i":10,"s":"foo","f":100.0,"b":true}'
    assert s == serde.json.to_json(p)

    assert '"😊"' == serde.json.to_json("😊")
    assert "10" == serde.json.to_json(10)
    assert "[10,20,30]" == serde.json.to_json([10, 20, 30])
    assert '{"foo":10,"fuga":10}' == serde.json.to_json({"foo": 10, "fuga": 10})


def test_msgpack():
    p = data.Pri(10, "foo", 100.0, True)
    d = b"\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3"
    assert d == serde.msgpack.to_msgpack(p)
    assert p == serde.msgpack.from_msgpack(data.Pri, d)


def test_msgpack_unnamed():
    p = data.Pri(10, "foo", 100.0, True)
    d = b"\x94\n\xa3foo\xcb@Y\x00\x00\x00\x00\x00\x00\xc3"
    assert d == serde.msgpack.to_msgpack(p, named=False)
    assert p == serde.msgpack.from_msgpack(data.Pri, d, named=False)


def test_toml():
    @serde.serde
    @dataclasses.dataclass
    class Foo:
        v: Optional[int]

    f = Foo(10)
    assert "v = 10\n" == serde.toml.to_toml(f)
    assert f == serde.toml.from_toml(Foo, "v = 10\n")

    # TODO: Should raise SerdeError
    with pytest.raises(TypeError):
        f = Foo(None)
        serde.toml.to_toml(f)

    @serde.serde
    @dataclasses.dataclass
    class Foo:
        v: Set[int]

    # TODO: Should raise SerdeError
    with pytest.raises(TypeError):
        f = Foo({1, 2, 3})
        serde.toml.to_toml(f)


@pytest.mark.parametrize("se,de", all_formats)
def test_rename(se, de):
    @serde.serde
    class Foo:
        class_name: str = serde.field(rename="class")

    f = Foo(class_name="foo")
    assert f == de(Foo, se(f))


@pytest.mark.parametrize("se,de", format_msgpack)
def test_rename_msgpack(se, de):
    @serde.serde(rename_all="camelcase")
    class Foo:
        class_name: str

    f = Foo(class_name="foo")
    assert f == de(Foo, se(f, named=True), named=True)
    assert f == de(Foo, se(f, named=False), named=False)


@pytest.mark.parametrize("se,de", (format_dict + format_json + format_yaml + format_toml + format_pickle))
def test_rename_formats(se, de):
    @serde.serde(rename_all="camelcase")
    class Foo:
        class_name: str

    f = Foo(class_name="foo")
    assert f == de(Foo, se(f))


@pytest.mark.parametrize("se,de", (format_dict + format_json + format_yaml + format_toml + format_pickle))
def test_alias(se, de):
    @serde.serde
    class Foo:
        a: str = serde.field(alias=["b", "c", "d"])

    f = Foo(a="foo")
    assert f == de(Foo, se(f))


def test_conflicting_alias():
    @serde.serde
    class Foo:
        a: int = serde.field(alias=["b", "c", "d"])
        b: int
        c: int
        d: int

    f = Foo(a=1, b=2, c=3, d=4)
    assert '{"a":1,"b":2,"c":3,"d":4}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"a":1,"b":2,"c":3,"d":4}')
    assert ff.a == 1
    assert ff.b == 2
    assert ff.c == 3
    assert ff.d == 4

    ff = serde.json.from_json(Foo, '{"b":2,"c":3,"d":4}')
    assert ff.a == 2
    assert ff.b == 2
    assert ff.c == 3
    assert ff.d == 4


def test_rename_and_alias():
    @serde.serde
    class Foo:
        a: int = serde.field(rename="z", alias=["b", "c", "d"])

    f = Foo(a=1)
    assert '{"z":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"b":10}')
    assert ff.a == 10


def test_default_and_alias():
    @serde.serde
    class Foo:
        a: int = serde.field(default=2, alias=["b", "c", "d"])

    f = Foo(a=1)
    assert '{"a":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"b":10}')
    assert ff.a == 10
    ff = serde.json.from_json(Foo, '{"e":10}')
    assert ff.a == 2


def test_default_and_rename():
    @serde.serde
    class Foo:
        a: int = serde.field(default=2, rename="z")

    f = Foo(a=1)
    assert '{"z":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"z":10}')
    assert ff.a == 10
    fff = serde.json.from_json(Foo, '{"a":10}')
    assert fff.a == 2


def test_default_rename_and_alias():
    @serde.serde
    class Foo:
        a: int = serde.field(default=2, rename="z", alias=["b", "c", "d"])

    f = Foo(a=1)
    assert '{"z":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"b":10}')
    assert ff.a == 10
    ff = serde.json.from_json(Foo, '{"e":10}')
    assert ff.a == 2


@pytest.mark.parametrize(
    "se,de", (format_dict + format_json + format_msgpack + format_yaml + format_toml + format_pickle)
)
def test_skip_if(se, de):
    @serde.serde
    class Foo:
        comments: Optional[List[str]] = serde.field(default_factory=list, skip_if=lambda v: len(v) == 0)
        attrs: Optional[Dict[str, str]] = serde.field(default_factory=dict, skip_if=lambda v: v is None or len(v) == 0)

    f = Foo(["foo"], {"bar": "baz"})
    assert f == de(Foo, se(f))

    f = Foo([])
    ff = de(Foo, se(f))
    assert ff.comments == []
    assert ff.attrs == {}


@pytest.mark.parametrize("se,de", all_formats)
def test_skip_if_false(se, de):
    @serde.serde
    class Foo:
        comments: Optional[List[str]] = serde.field(default_factory=list, skip_if_false=True)

    f = Foo(["foo"])
    assert f == de(Foo, se(f))


@pytest.mark.parametrize(
    "se,de", (format_dict + format_json + format_msgpack + format_yaml + format_toml + format_pickle)
)
def test_skip_if_overrides_skip_if_false(se, de):
    @serde.serde
    class Foo:
        comments: Optional[List[str]] = serde.field(
            default_factory=list, skip_if_false=True, skip_if=lambda v: len(v) == 1
        )

    f = Foo(["foo"])
    ff = de(Foo, se(f))
    assert ff.comments == []


@pytest.mark.parametrize("se,de", all_formats)
def test_skip_if_default(se, de):
    @serde.serde
    class Foo:
        a: str = serde.field(default="foo", skip_if_default=True)

    f = Foo()
    assert f == de(Foo, se(f))

    assert serde.to_dict(Foo()) == {}
    assert serde.to_dict(Foo("bar")) == {"a": "bar"}
    assert serde.from_dict(Foo, {}) == Foo()
    assert serde.from_dict(Foo, {"a": "bar"}) == Foo("bar")


@pytest.mark.parametrize("se,de", format_msgpack)
def test_inheritance(se, de):
    from dataclasses import dataclass

    @serde.serde
    class Base:
        a: int
        b: str

    @serde.serde
    @dataclass
    class Derived(Base):
        c: float

    base = Base(10, "foo")
    assert base == de(Base, se(base))

    derived = Derived(10, "foo", 100.0)
    assert derived == de(Derived, se(derived))


@pytest.mark.parametrize("se,de", format_msgpack)
def test_duplicate_decorators(se, de):
    from dataclasses import dataclass

    @serde.serde
    @serde.serde
    @dataclass
    @dataclass
    class Foo:
        a: int
        b: str

    foo = Foo(10, "foo")
    assert foo == de(Foo, se(foo))


@pytest.mark.parametrize("se,de", format_msgpack)
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


def make_serde(class_name: str, se: bool, fields, *args, **kwargs):
    if se:
        return serde.de.deserialize(serde.se._make_serialize(class_name, fields, *args, **kwargs), **kwargs)
    else:
        return serde.se.serialize(serde.de._make_deserialize(class_name, fields, *args, **kwargs), **kwargs)


@pytest.mark.parametrize("se", (True, False))
def test_make_serialize_deserialize(se):
    fields = [("i", int, dataclasses.field())]
    Foo = make_serde("Foo", se, fields)

    f = Foo(10)
    assert serde.to_dict(f) == {"i": 10}
    assert str(f) == "Foo(i=10)"
    assert serde.from_dict(Foo, {"i": 10}) == f

    # Test class attribute
    fields = [("int_field", int, dataclasses.field())]
    Foo = make_serde("Foo", se, fields, rename_all="pascalcase")
    f = Foo(10)
    assert serde.to_dict(f) == {"IntField": 10}

    # Test field attribute
    fields = [("i", int, dataclasses.field(metadata={"serde_skip": True})), ("j", float, dataclasses.field())]
    Foo = make_serde("Foo", se, fields)
    f = Foo(10, 100.0)
    assert serde.to_dict(f) == {"j": 100.0}

    # Test class/field attributes at the same time
    fields = [
        ("int_field", int, dataclasses.field(metadata={"serde_rename": "renamed_field"})),
        ("float_field", float, dataclasses.field()),
    ]
    Foo = make_serde("Foo", se, fields, rename_all="pascalcase")
    f = Foo(10, 100.0)
    assert serde.to_dict(f) == {"renamed_field": 10, "FloatField": 100.0}

    # Nested
    fields = [("v", int, dataclasses.field())]
    Bar = make_serde("Bar", se, fields)

    fields = [("bar", Bar, dataclasses.field())]
    Foo = make_serde("Foo", se, fields)
    f = Foo(Bar(10))
    assert serde.to_dict(f) == {"bar": {"v": 10}}
    assert serde.from_dict(Foo, {"bar": {"v": 10}}) == f


def test_exception_to_from_obj():
    @serde.serde
    class Foo:
        a: int

    class Bar:
        pass

    with pytest.raises(serde.SerdeError):
        serde.from_dict(Foo, {})


def test_user_error():
    class MyException(Exception):
        pass

    @serde.serde
    @dataclasses.dataclass
    class Foo:
        v: int

        def __post_init__(self):
            if self.v == 10:
                raise MyException("Invalid value")

    with pytest.raises(MyException):
        serde.from_dict(Foo, {"v": 10})

    with pytest.raises(serde.SerdeError):
        serde.from_dict(Foo, {})


test_cases = [
    (int, 10, False),
    (int, 10.0, True),
    (int, "10", True),
    (int, True, False),  # Unable to type check bool against int correctly,
    # because "bool" is a subclass of "int"
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
    (List[int], [1, 1.0], False),  # Because serde checks only the first element
    (List[float], [1.0], False),
    (List[float], ["foo"], True),
    (List[str], ["foo"], False),
    (List[str], [True], True),
    (List[bool], [True], False),
    (List[bool], [10], True),
    (List[data.Int], [data.Int(1)], False),
    (List[data.Int], [data.Int(1.0)], True),  # type: ignore
    (List[data.Int], [data.Int(1), data.Float(10.0)], True),
    (List[data.Int], [], False),
    (Dict[str, int], {"foo": 10}, False),
    (Dict[str, int], {"foo": 10.0}, True),
    (Dict[str, int], {"foo": 10, 100: "bar"}, False),  # Because serde checks only the first element
    (Dict[str, data.Int], {"foo": data.Int(1)}, False),
    (Dict[str, data.Int], {"foo": data.Int(1.0)}, True),  # type: ignore
    (Set[int], {10}, False),
    (Set[int], {10.0}, True),
    (Set[int], [10], True),
    (Tuple[int], (10,), False),
    (Tuple[int], (10.0,), True),
    (Tuple[int, str], (10, "foo"), False),
    (Tuple[int, str], (10, 10.0), True),
    (Tuple[data.Int, data.Str], (data.Int(1), data.Str("2")), False),
    (Tuple[data.Int, data.Str], (data.Int(1), data.Int(2)), True),
    (Tuple, (10, 10.0), False),
    (Tuple[int, ...], (1, 2), False),
    (Tuple[int, ...], (1, 2.0), True),
    (data.E, data.E.S, False),
    (data.E, data.IE.V0, False),  # TODO enum type check is not yet perfect
    (Union[int, str], 10, False),
    (Union[int, str], "foo", False),
    (Union[int, str], 10.0, True),
    (Union[int, data.Int], data.Int(10), False),
    (datetime.date, datetime.date.today(), False),
    (pathlib.Path, pathlib.Path(), False),
    (pathlib.Path, "foo", True),
]


@pytest.mark.parametrize("T,data,exc", test_cases)
def test_type_check(T, data, exc):
    @serde.serde(type_check=Strict)
    class C:
        a: T

    if exc:
        with pytest.raises(serde.SerdeError):
            d = serde.to_dict(C(data))
            serde.from_dict(C, d)
    else:
        d = serde.to_dict(C(data))
        serde.from_dict(C, d)


def test_uncoercible():
    @serde.serde(type_check=serde.Coerce)
    class Foo:
        i: int

    with pytest.raises(serde.SerdeError):
        serde.to_dict(Foo("foo"))

    with pytest.raises(serde.SerdeError):
        serde.from_dict(Foo, {"i": "foo"})


def test_coerce():
    @serde.serde(type_check=serde.Coerce)
    @dataclasses.dataclass
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

    p = Foo("10", 100, 1000, "True")
    d = serde.to_dict(p)
    assert d["i"] == 10
    assert d["s"] == "100"
    assert d["f"] == 1000.0
    assert d["b"]

    # Couldn't coerce
    with pytest.raises(serde.SerdeError):
        d = {"i": "foo", "s": 100, "f": "bar", "b": "True"}
        p = serde.from_dict(Foo, d)

    @serde.serde(type_check=serde.Coerce)
    @dataclasses.dataclass
    class Int:
        i: int

    @serde.serde(type_check=serde.Coerce)
    @dataclasses.dataclass
    class Str:
        s: str

    @serde.serde(type_check=serde.Coerce)
    @dataclasses.dataclass
    class Float:
        f: float

    @serde.serde(type_check=serde.Coerce)
    @dataclasses.dataclass
    class Bool:
        b: bool

    @serde.serde(type_check=serde.Coerce)
    @serde.dataclass
    class Nested:
        i: data.Int
        s: data.Str
        f: data.Float
        b: data.Bool

    # Nested structure
    p = Nested(Int("10"), Str(100), Float(1000), Bool("True"))
    d = serde.to_dict(p)
    assert d["i"]["i"] == 10
    assert d["s"]["s"] == "100"
    assert d["f"]["f"] == 1000.0
    assert d["b"]["b"]

    d = {"i": {"i": "10"}, "s": {"s": 100}, "f": {"f": 1000}, "b": {"b": "True"}}
    p = serde.from_dict(Nested, d)


def test_frozenset() -> None:
    @serde.serde
    @dataclasses.dataclass
    class Foo:
        d: FrozenSet[int]

    f = Foo(frozenset({1, 1, 2}))
    assert '{"d":[1,2]}' == serde.json.to_json(f)

    ff = serde.json.from_json(Foo, '{"d":[1,2]}')
    assert f == ff
    assert isinstance(f.d, frozenset)
    assert isinstance(ff.d, frozenset)

    fs = serde.json.from_json(FrozenSet[int], "[1,2]")
    assert fs == frozenset([1, 2])


def test_defaultdict() -> None:
    from collections import defaultdict

    @serde.serde
    @dataclasses.dataclass
    class Foo:
        v: DefaultDict[str, List[int]]

    f = Foo(defaultdict(list, {"k": [1, 2]}))
    assert '{"v":{"k":[1,2]}}' == serde.json.to_json(f)

    ff = serde.json.from_json(Foo, '{"v":{"k":[1,2]}}')
    assert f == ff
    assert isinstance(f.v, defaultdict)
    assert isinstance(ff.v, defaultdict)

    dd = serde.json.from_json(DefaultDict[str, List[int]], '{"k":[1,2]}')
    assert isinstance(dd, defaultdict)
    assert dd == defaultdict(list, {"k": [1, 2]})


def test_defaultdict_invalid_value_type() -> None:
    with pytest.raises(Exception):
        serde.json.from_json(DefaultDict[str, ...], '{"k":[1,2]}')

    with pytest.raises(Exception):
        serde.json.from_json(DefaultDict, '{"k":[1,2]}')


def test_class_var() -> None:
    @serde.serde
    @dataclasses.dataclass
    class Disabled:
        v: ClassVar[int] = 10

    a = Disabled()
    assert {} == serde.to_dict(a)
    assert a == serde.from_dict(Disabled, {})

    @serde.serde(serialize_class_var=True)
    @dataclasses.dataclass
    class Enabled:
        v: ClassVar[int] = 10

    b = Enabled()
    assert {"v": 10} == serde.to_dict(b)
    assert b == serde.from_dict(Enabled, {})

    @serde.serde
    @dataclasses.dataclass
    class Foo:
        v: int

    @serde.serde(serialize_class_var=True)
    @dataclasses.dataclass
    class Dataclass:
        v: ClassVar[Foo] = Foo(10)

    c = Dataclass()
    assert {"v": {"v": 10}} == serde.to_dict(c)
    assert c == serde.from_dict(Dataclass, {})

    @serde.serde(serialize_class_var=True)
    @dataclasses.dataclass
    class ClassList:
        v: ClassVar[List[Foo]] = [Foo(10), Foo(20)]

    d = ClassList()
    assert {"v": [{"v": 10}, {"v": 20}]} == serde.to_dict(d)
    assert d == serde.from_dict(ClassList, {})

    # Mutate class variable
    Enabled.v = 100
    e = Enabled()
    assert {"v": 100} == serde.to_dict(e)
    assert e == serde.from_dict(Enabled, {})

    @serde.serde(serialize_class_var=True)
    @dataclasses.dataclass
    class Bar:
        v: ClassVar[int] = 100

    @serde.serde(serialize_class_var=True)
    @dataclasses.dataclass
    class Nested:
        v: ClassVar[Bar] = Bar()

    f = Nested()
    assert {"v": {"v": 100}} == serde.to_dict(f)
    assert f == serde.from_dict(Nested, {})


def test_dataclass_without_serde() -> None:
    @serde.serde(rename_all="kebabcase")
    @dataclasses.dataclass
    class Foo:
        myLongName: int

    @dataclasses.dataclass
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(myLongName=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"my-long-name": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_dataclass_add_serialize() -> None:
    @serde.serde(rename_all="kebabcase")
    @dataclasses.dataclass
    class Foo:
        myLongName: int

    @serde.deserialize
    @dataclasses.dataclass
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(myLongName=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"my-long-name": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_dataclass_add_deserialize() -> None:
    @serde.serde(rename_all="kebabcase")
    @dataclasses.dataclass
    class Foo:
        myLongName: int

    @serde.serialize
    @dataclasses.dataclass
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(myLongName=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"my-long-name": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_nested_dataclass_without_serde() -> None:
    @dataclasses.dataclass
    class Foo:
        v: int

    @serde.serde
    @dataclasses.dataclass
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(v=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"v": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_nested_dataclass_add_deserialize() -> None:
    @serde.serialize
    @dataclasses.dataclass
    class Foo:
        v: int

    @serde.serde
    @dataclasses.dataclass
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(v=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"v": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_nested_dataclass_add_serialize() -> None:
    @serde.deserialize
    @dataclasses.dataclass
    class Foo:
        v: int

    @serde.serde
    @dataclasses.dataclass
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(v=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"v": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_nested_dataclass_ignore_wrapper_options() -> None:
    @dataclasses.dataclass
    class Foo:
        myLongName: int

    @serde.serde(rename_all="kebabcase")
    @dataclasses.dataclass
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(myLongName=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"myLongName": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)
