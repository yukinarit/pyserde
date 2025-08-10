# pyright: reportInvalidTypeForm=false, reportGeneralTypeIssues=false

import dataclasses
import enum
import logging
import uuid
import datetime
from beartype.roar import BeartypeCallHintViolation
from typing import (
    ClassVar,
    Optional,
    Any,
)
from collections import defaultdict

import pytest

import serde
import serde.toml

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
def test_simple(se: Any, de: Any, opt: Any, t: Any, T: Any, f: Any) -> None:
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    if f(se, de, opt):
        return

    @serde.serde(**opt)
    class C:
        i: int
        t: T

    c = C(10, t)
    assert c == de(C, se(c))

    # @serde.serde(**opt)
    # class Nested:
    #    t: T

    # @serde.serde(**opt)
    # class C:
    #    n: Nested

    # c = C(Nested(t))
    # assert c == de(C, se(c))

    # if se is not serde.toml.to_toml:
    #    assert t == de(T, se(t))


@pytest.mark.parametrize("t,T,f", types, ids=type_ids())
@pytest.mark.parametrize("named", (True, False))
@pytest.mark.parametrize("reuse", (True, False))
def test_from_to_obj(t: Any, T: Any, f: Any, named: bool, reuse: bool) -> None:
    obj = serde.se.to_obj(t, named, reuse, False)
    assert t == serde.de.from_obj(T, obj, named, reuse)


@pytest.mark.parametrize("t,T,filter", types, ids=type_ids())
@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", (format_dict + format_tuple))
def test_simple_with_reuse_instances(
    se: Any, de: Any, opt: Any, t: Any, T: Any, filter: Any
) -> None:
    log.info(
        f"Running test with se={se.__name__} de={de.__name__} opts={opt} while reusing instances"
    )

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
    class C2:
        n: Nested

    c2 = C2(Nested(t))
    assert c2 == de(C2, se(c2, reuse_instances=True), reuse_instances=True)


def test_non_dataclass_reuse_instances() -> None:
    dt = datetime.datetime.fromisoformat("2020-01-01 00:00:00+00:00")
    assert "2020-01-01T00:00:00+00:00" == serde.to_dict(dt, reuse_instances=False)  # type: ignore
    assert dt == serde.to_dict(dt, reuse_instances=True)
    assert dt is serde.to_dict(dt, reuse_instances=True)
    assert "2020-01-01T00:00:00+00:00" == serde.to_tuple(dt, reuse_instances=False)  # type: ignore
    assert dt == serde.to_dict(dt, reuse_instances=True)
    assert dt is serde.to_dict(dt, reuse_instances=True)


def test_non_dataclass() -> None:
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
def test_string_forward_reference_works() -> None:
    h = ForwardReferenceFoo(bar=ForwardReferenceBar(i=10))
    h_dict = {"bar": {"i": 10}}

    assert serde.to_dict(h) == h_dict
    assert serde.from_dict(ForwardReferenceFoo, h_dict) == h


# trying to use string forward reference normally will throw
def test_unresolved_forward_reference_throws() -> None:
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
def test_list(se: Any, de: Any, opt: Any) -> None:
    @serde.serde(**opt)
    class Variant:
        d: list[Any]

    # List can contain different types (except Toml).
    if se is not serde.toml.to_toml:
        p = Variant([10, "foo", 10.0, True])
        assert p == de(Variant, se(p))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_dict_with_non_str_keys(se: Any, de: Any, opt: Any) -> None:
    @serde.serde(**opt)
    class Foo:
        i: dict[int, int]
        s: dict[str, str]
        f: dict[float, float]
        b: dict[bool, bool]

    # JSON, Msgpack, Toml don't allow non string key.
    if se not in (serde.json.to_json, serde.msgpack.to_msgpack, serde.toml.to_toml):
        p = Foo({10: 10}, {"foo": "bar"}, {100.0: 100.0}, {True: False})
        assert p == de(Foo, se(p))


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_enum(se: Any, de: Any, opt: Any) -> None:
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

    f = Foo(E("foo"), IE(2), NestedEnum(Inner.V0), E(True), IE(10), NestedEnum(Inner.V0))
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


# TODO
# @pytest.mark.parametrize("se,de", all_formats)
# def test_enum_imported(se, de):
#     from .data import EnumInClass
#
#     c = EnumInClass()
#     cc = de(EnumInClass, se(c))
#     assert c == cc


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_tuple(se: Any, de: Any, opt: Any) -> None:
    @serde.serde(**opt)
    class Homogeneous:
        i: tuple[int, int]
        s: tuple[str, str]
        f: tuple[float, float]
        b: tuple[bool, bool]

    def uncheck_new(i: list[Any], s: list[Any], f: list[Any], b: list[Any]) -> Homogeneous:
        """
        Bypass runtime type checker by mutating inner value.
        """
        obj = Homogeneous((0, 0), ("", ""), (0.0, 0.0), (True, True))
        obj.i = i  # type: ignore
        obj.s = s  # type: ignore
        obj.f = f  # type: ignore
        obj.b = b  # type: ignore
        return obj

    a = Homogeneous((10, 20), ("a", "b"), (10.0, 20.0), (True, False))
    assert a == de(Homogeneous, se(a))

    # List will be type mismatch if type_check=True.
    tuple_but_actually_list = uncheck_new([10, 20], ["a", "b"], [10.0, 20.0], [True, False])
    assert tuple_but_actually_list != de(Homogeneous, se(tuple_but_actually_list))

    @serde.serde(**opt)
    class Variant:
        t: tuple[int, str, float, bool]

    # Toml doesn't support variant type of array.
    if se is not serde.toml.to_toml:
        b = Variant((10, "a", 10.0, True))
        assert b == de(Variant, se(b))

    @serde.serde(**opt)
    class Baretuple:
        t: tuple  # type: ignore

    c = Baretuple((10, 20))
    assert c == de(Baretuple, se(c))

    c = Baretuple(())
    assert c == de(Baretuple, se(c))

    @serde.serde(**opt)
    class Nested:
        i: tuple[data.Int, data.Int]
        s: tuple[data.Str, data.Str]
        f: tuple[data.Float, data.Float]
        b: tuple[data.Bool, data.Bool]

    d = Nested(
        (data.Int(10), data.Int(20)),
        (data.Str("a"), data.Str("b")),
        (data.Float(10.0), data.Float(20.0)),
        (data.Bool(True), data.Bool(False)),
    )
    assert d == de(Nested, se(d))

    @serde.serde(**opt)
    class Variabletuple:
        t: tuple[int, int, int]
        i: tuple[data.Inner, data.Inner]

    e = Variabletuple((1, 2, 3), (data.Inner(0), data.Inner(1)))
    assert e == de(Variabletuple, se(e))

    with pytest.raises((serde.SerdeError, BeartypeCallHintViolation)):
        e = Variabletuple((), ())  # type: ignore[arg-type]
        assert e == de(Variabletuple, se(e))

    with pytest.raises((serde.SerdeError, SyntaxError)):

        @serde.serde(**opt)
        class Emptytuple:
            t: tuple[()]


@pytest.mark.parametrize("se,de", all_formats)
def test_single_element_tuples(se: Any, de: Any) -> None:
    @serde.serde
    class Foo:
        a: tuple[int]
        b: tuple[uuid.UUID]

    foo = Foo(a=(1,), b=(uuid.UUID("855f07da-c3cd-46f2-9557-b8dbeb99ff42"),))
    assert serde.to_dict(foo) == {"a": foo.a, "b": foo.b}

    assert foo == de(Foo, se(foo))


@pytest.mark.parametrize("se,de", all_formats)
def test_dataclass_default_factory(se: Any, de: Any) -> None:
    @serde.serde
    class Foo:
        foo: str
        items: dict[str, int] = serde.field(default_factory=dict)

    f = Foo("bar")
    assert f == de(Foo, se(f))

    assert {"foo": "bar", "items": {}} == serde.to_dict(f)
    assert f == serde.from_dict(Foo, {"foo": "bar"})


@pytest.mark.parametrize("se,de", all_formats)
def test_default(se: Any, de: Any) -> None:
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
    "se,de",
    (format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_pickle),
)
def test_list_pri(se: Any, de: Any) -> None:
    p = [data.PRI, data.PRI]
    assert p == de(data.ListPri, se(p))

    p = []
    assert p == de(data.ListPri, se(p))


@pytest.mark.parametrize(
    "se,de",
    (format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_pickle),
)
def test_dict_pri(se: Any, de: Any) -> None:
    p = {"1": data.PRI, "2": data.PRI}
    assert p == de(data.DictPri, se(p))

    p = {}
    assert p == de(data.DictPri, se(p))


def test_json() -> None:
    p = data.Pri(10, "foo", 100.0, True)
    s = '{"i":10,"s":"foo","f":100.0,"b":true}'
    assert s == serde.json.to_json(p)
    assert '"😊"' == serde.json.to_json("😊")
    assert "10" == serde.json.to_json(10)
    assert "[10,20,30]" == serde.json.to_json([10, 20, 30])
    assert '{"foo":10,"fuga":10}' == serde.json.to_json({"foo": 10, "fuga": 10})


def test_msgpack() -> None:
    p = data.Pri(10, "foo", 100.0, True)
    d = b"\x84\xa1i\n\xa1s\xa3foo\xa1f\xcb@Y\x00\x00\x00\x00\x00\x00\xa1b\xc3"
    assert d == serde.msgpack.to_msgpack(p)
    assert p == serde.msgpack.from_msgpack(data.Pri, d)


def test_msgpack_unnamed() -> None:
    p = data.Pri(10, "foo", 100.0, True)
    d = b"\x94\n\xa3foo\xcb@Y\x00\x00\x00\x00\x00\x00\xc3"
    assert d == serde.msgpack.to_msgpack(p, named=False)
    assert p == serde.msgpack.from_msgpack(data.Pri, d, named=False)


@pytest.mark.parametrize("se,de", all_formats)
def test_rename(se: Any, de: Any) -> None:
    @serde.serde
    class Foo:
        class_name: str = serde.field(rename="class")

    f = Foo(class_name="foo")
    assert f == de(Foo, se(f))


@pytest.mark.parametrize("se,de", format_msgpack)
def test_rename_msgpack(se: Any, de: Any) -> None:
    @serde.serde(rename_all="camelcase")
    class Foo:
        class_name: str

    f = Foo(class_name="foo")
    assert f == de(Foo, se(f, named=True), named=True)
    assert f == de(Foo, se(f, named=False), named=False)


@pytest.mark.parametrize(
    "se,de", (format_dict + format_json + format_yaml + format_toml + format_pickle)
)
def test_rename_formats(se: Any, de: Any) -> None:
    @serde.serde(rename_all="camelcase")
    class Foo:
        class_name: str

    f = Foo(class_name="foo")
    assert f == de(Foo, se(f))


@pytest.mark.parametrize(
    "se,de", (format_dict + format_json + format_yaml + format_toml + format_pickle)
)
def test_alias(se: Any, de: Any) -> None:
    @serde.serde
    class Foo:
        a: str = serde.field(alias=["b", "c", "d"])  # type: ignore[literal-required]

    f = Foo(a="foo")
    assert f == de(Foo, se(f))


def test_conflicting_alias() -> None:
    @serde.serde
    class Foo:
        a: int = serde.field(alias=["b", "c", "d"])  # type: ignore[literal-required]
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


def test_rename_and_alias() -> None:
    @serde.serde
    class Foo:
        a: int = serde.field(rename="z", alias=["b", "c", "d"])  # type: ignore[literal-required]

    f = Foo(a=1)
    assert '{"z":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"b":10}')
    assert ff.a == 10


def test_rename_all_and_alias() -> None:
    @serde.serde(rename_all="pascalcase")
    class Foo:
        a_field: int = serde.field(alias=["b_field"])  # type: ignore[literal-required]

    f = Foo(1)
    assert '{"AField":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"b_field":1}')  # alias is not renamed
    assert f == ff


def test_default_and_alias() -> None:
    @serde.serde
    class Foo:
        a: int = serde.field(default=2, alias=["b", "c", "d"])  # type: ignore[literal-required]

    f = Foo(a=1)
    assert '{"a":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"b":10}')
    assert ff.a == 10
    ff = serde.json.from_json(Foo, '{"e":10}')
    assert ff.a == 2


def test_optional_and_alias() -> None:
    @serde.serde
    class Foo:
        a: Optional[int] = serde.field(alias=["b"])  # type: ignore[literal-required]

    assert Foo(1) == serde.json.from_json(Foo, '{"b":1}')
    assert Foo(None) == serde.json.from_json(Foo, '{"c":1}')


def test_default_and_rename() -> None:
    @serde.serde
    class Foo:
        a: int = serde.field(default=2, rename="z")

    f = Foo(a=1)
    assert '{"z":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"z":10}')
    assert ff.a == 10
    fff = serde.json.from_json(Foo, '{"a":10}')
    assert fff.a == 2


def test_default_rename_and_alias() -> None:
    @serde.serde
    class Foo:
        a: int = serde.field(default=2, rename="z", alias=["b", "c", "d"])  # type: ignore[literal-required]

    f = Foo(a=1)
    assert '{"z":1}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"b":10}')
    assert ff.a == 10
    ff = serde.json.from_json(Foo, '{"e":10}')
    assert ff.a == 2


@pytest.mark.parametrize(
    "se,de",
    (format_dict + format_json + format_msgpack + format_yaml + format_toml + format_pickle),
)
def test_skip_if(se: Any, de: Any) -> None:
    @serde.serde
    class Foo:
        comments: Optional[list[str]] = serde.field(
            default_factory=list, skip_if=lambda v: len(v) == 0
        )
        attrs: Optional[dict[str, str]] = serde.field(
            default_factory=dict, skip_if=lambda v: v is None or len(v) == 0
        )

    f = Foo(["foo"], {"bar": "baz"})
    assert f == de(Foo, se(f))

    f = Foo([])
    ff = de(Foo, se(f))
    assert ff.comments == []
    assert ff.attrs == {}


@pytest.mark.parametrize("se,de", all_formats)
def test_skip_if_false(se: Any, de: Any) -> None:
    @serde.serde
    class Foo:
        comments: Optional[list[str]] = serde.field(default_factory=list, skip_if_false=True)

    f = Foo(["foo"])
    assert f == de(Foo, se(f))


@pytest.mark.parametrize(
    "se,de",
    (format_dict + format_json + format_msgpack + format_yaml + format_toml + format_pickle),
)
def test_skip_if_overrides_skip_if_false(se: Any, de: Any) -> None:
    @serde.serde
    class Foo:
        comments: Optional[list[str]] = serde.field(
            default_factory=list, skip_if_false=True, skip_if=lambda v: len(v) == 1
        )

    f = Foo(["foo"])
    ff = de(Foo, se(f))
    assert ff.comments == []


@pytest.mark.parametrize("se,de", all_formats)
def test_skip_if_default(se: Any, de: Any) -> None:
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
def test_inheritance(se: Any, de: Any) -> None:
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


@pytest.mark.parametrize("se,de", format_msgpack)
def test_duplicate_decorators(se: Any, de: Any) -> None:
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
def test_ext(se: Any, de: Any) -> None:
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


def test_exception_on_not_supported_types() -> None:
    class UnsupportedClass:
        def __init__(self) -> None:
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


def test_dataclass_inheritance() -> None:
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
    # ensure the generated code of DerivedB does not overwrite the earlier generated code
    # from DerivedA
    assert getattr(Base, serde.core.SERDE_SCOPE) is not getattr(DerivedA, serde.core.SERDE_SCOPE)
    assert getattr(DerivedA, serde.core.SERDE_SCOPE) is not getattr(
        DerivedB, serde.core.SERDE_SCOPE
    )

    base = Base(i=0, s="foo")
    assert base == serde.from_dict(Base, serde.to_dict(base))

    a = DerivedA(i=0, s="foo", j=42)
    assert a == serde.from_dict(DerivedA, serde.to_dict(a))

    b = DerivedB(i=0, s="foo", k=42.0)
    assert b == serde.from_dict(DerivedB, serde.to_dict(b))


def make_serde(class_name: str, se: bool, fields: Any, *args: Any, **kwargs: Any) -> Any:
    if se:
        return serde.de.deserialize(
            serde.se._make_serialize(class_name, fields, *args, **kwargs), **kwargs
        )
    else:
        return serde.se.serialize(
            serde.de._make_deserialize(class_name, fields, *args, **kwargs), **kwargs
        )


@pytest.mark.parametrize("se", (True, False))
def test_make_serialize_deserialize(se: Any) -> None:
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
    fields = [
        ("i", int, dataclasses.field(metadata={"serde_skip": True})),
        ("j", float, dataclasses.field()),  # type: ignore[list-item]
    ]
    Foo = make_serde("Foo", se, fields)
    f = Foo(10, 100.0)
    assert serde.to_dict(f) == {"j": 100.0}

    # Test class/field attributes at the same time
    fields = [
        ("int_field", int, dataclasses.field(metadata={"serde_rename": "renamed_field"})),
        ("float_field", float, dataclasses.field()),  # type: ignore[list-item]
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


def test_exception_to_from_obj() -> None:
    @serde.serde
    class Foo:
        a: int

    class Bar:
        pass

    with pytest.raises(serde.SerdeError):
        serde.from_dict(Foo, {})


def test_user_error() -> None:
    class MyException(Exception):
        pass

    @serde.serde
    class Foo:
        v: int

        def __post_init__(self) -> None:
            if self.v == 10:
                raise MyException("Invalid value")

    with pytest.raises(MyException):
        serde.from_dict(Foo, {"v": 10})

    with pytest.raises(serde.SerdeError):
        serde.from_dict(Foo, {})


def test_frozenset() -> None:
    @serde.serde
    class Foo:
        d: frozenset[int]

    f = Foo(frozenset({1, 2}))
    assert '{"d":[1,2]}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"d":[1,2]}')
    assert f == ff
    assert isinstance(f.d, frozenset)
    assert isinstance(ff.d, frozenset)

    fs = serde.json.from_json(frozenset[int], "[1,2]")
    assert fs == frozenset([1, 2])


def test_defaultdict() -> None:
    from collections import defaultdict

    @serde.serde
    class Foo:
        v: defaultdict[str, list[int]]

    f = Foo(defaultdict(list, {"k": [1, 2]}))
    assert '{"v":{"k":[1,2]}}' == serde.json.to_json(f)
    ff = serde.json.from_json(Foo, '{"v":{"k":[1,2]}}')
    assert f == ff
    assert isinstance(f.v, defaultdict)
    assert isinstance(ff.v, defaultdict)

    dd = serde.json.from_json(defaultdict[str, list[int]], '{"k":[1,2]}')
    assert isinstance(dd, defaultdict)
    assert dd == defaultdict(list, {"k": [1, 2]})


def test_defaultdict_invalid_value_type() -> None:
    with pytest.raises(serde.SerdeError):
        serde.json.from_json(defaultdict[str, ...], '{"k":[1,2]}')  # type: ignore[misc]

    with pytest.raises(serde.SerdeError):
        serde.json.from_json(defaultdict, '{"k":[1,2]}')


def test_class_var() -> None:
    @serde.serde
    class Disabled:
        v: ClassVar[int] = 10

    a = Disabled()
    assert {} == serde.to_dict(a)
    assert a == serde.from_dict(Disabled, {})

    @serde.serde(serialize_class_var=True)
    class Enabled:
        v: ClassVar[int] = 10

    b = Enabled()
    assert {"v": 10} == serde.to_dict(b)
    assert b == serde.from_dict(Enabled, {})

    @serde.serde
    class Foo:
        v: int

    @serde.serde(serialize_class_var=True)
    class Dataclass:
        v: ClassVar[Foo] = Foo(10)

    c = Dataclass()
    assert {"v": {"v": 10}} == serde.to_dict(c)
    assert c == serde.from_dict(Dataclass, {})

    @serde.serde(serialize_class_var=True)
    class ClassList:
        v: ClassVar[list[Foo]] = [Foo(10), Foo(20)]

    d = ClassList()
    assert {"v": [{"v": 10}, {"v": 20}]} == serde.to_dict(d)
    assert d == serde.from_dict(ClassList, {})

    # Mutate class variable
    Enabled.v = 100
    e = Enabled()
    assert {"v": 100} == serde.to_dict(e)
    assert e == serde.from_dict(Enabled, {})

    @serde.serde(serialize_class_var=True)
    class Bar:
        v: ClassVar[int] = 100

    @serde.serde(serialize_class_var=True)
    class Nested:
        v: ClassVar[Bar] = Bar()

    f = Nested()
    assert {"v": {"v": 100}} == serde.to_dict(f)
    assert f == serde.from_dict(Nested, {})


def test_dataclass_without_serde() -> None:
    @serde.serde(rename_all="kebabcase")
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
    class Foo:
        myLongName: int

    @serde.deserialize
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(myLongName=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"my-long-name": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_dataclass_add_deserialize() -> None:
    @serde.serde(rename_all="kebabcase")
    class Foo:
        myLongName: int

    @serde.serialize
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
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(v=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"v": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_nested_dataclass_add_deserialize() -> None:
    @serde.serialize
    class Foo:
        v: int

    @serde.serde
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(v=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"v": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_nested_dataclass_add_serialize() -> None:
    @serde.deserialize
    class Foo:
        v: int

    @serde.serde
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
    class Wrapper:
        foo: Foo

    a = Wrapper(foo=Foo(myLongName=1))
    serialized = serde.to_dict(a)
    assert {"foo": {"myLongName": 1}} == serialized
    assert a == serde.from_dict(Wrapper, serialized)


def test_deserialize_from_incompatible_value() -> None:
    @serde.deserialize
    class Foo:
        v: int

    with pytest.raises(serde.SerdeError):
        assert serde.from_dict(Foo, None)  # type: ignore[call-overload]
    with pytest.raises(serde.SerdeError):
        assert serde.from_dict(Foo, "")  # type: ignore[call-overload]
    with pytest.raises(serde.SerdeError):
        assert serde.from_dict(Foo, 10)  # type: ignore[call-overload]


def test_frozen_dataclass() -> None:
    @serde.serde
    @dataclasses.dataclass(frozen=True)
    class Foo:
        a: int

    @serde.serde
    @dataclasses.dataclass(frozen=True)
    class Bar(Foo):  # type: ignore[misc]
        b: int

    bar = Bar(a=10, b=20)
    assert bar == serde.from_dict(Bar, serde.to_dict(bar))


def test_init_var_with_field_attribute() -> None:
    @serde.serde
    @dataclasses.dataclass
    class Foo:
        a: int = serde.field(skip=True)

    assert serde.to_dict(Foo(10)) == {}


def test_dict_str_any() -> None:
    @serde.serde
    class Foo:
        a: dict[str, Any]

    # Because the dict values are typed as Any, all values will be serialized as strings
    date = datetime.datetime(2024, 12, 3, 16, 55, 20, 220662)
    date_str = date.isoformat()

    uuid_val = uuid.UUID("efb71d76-4337-4b27-a612-5b6f95b01d42")
    uuid_str = str(uuid_val)

    foo = Foo(a={"a": uuid_val, "b": date})
    foo_se = {"a": {"a": uuid_str, "b": date_str}}
    foo_de = Foo(a={"a": uuid_str, "b": date_str})

    assert serde.to_dict(foo) == foo_se
    assert serde.from_dict(Foo, foo_se) == foo_de
