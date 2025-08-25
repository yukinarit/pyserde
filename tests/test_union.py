import logging
import sys
import uuid
from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import (
    Generic,
    NewType,
    Optional,
    TypeVar,
    Union,
    Any,
    Literal,
)
from uuid import UUID

import pytest

from serde import (
    SerdeError,
    from_dict,
    from_tuple,
    init as serde_init,
    logger,
    serde,
    to_dict,
    to_tuple,
    InternalTagging,
    AdjacentTagging,
    Untagged,
)
from serde.json import from_json, to_json

logging.basicConfig(level=logging.WARNING)
logger.setLevel(logging.DEBUG)

serde_init(True)


if sys.version_info[:3] >= (3, 10, 0):

    @serde
    @dataclass(unsafe_hash=True)
    class PriUnion:  # pyright: ignore[reportRedeclaration] # Version-specific redefinition
        """
        Union Primitives.
        """

        v: int | str | float | bool

else:

    @serde
    @dataclass(unsafe_hash=True)
    class PriUnion:  # type: ignore[no-redef] # pyright: ignore[reportRedeclaration] # Version-specific redefinition
        """
        Union Primitives.
        """

        v: Union[int, str, float, bool]


@serde
@dataclass(unsafe_hash=True)
class PriOptUnion:
    """
    Union Primitives.
    """

    v: Union[Optional[int], Optional[str], Optional[float], Optional[bool]]


@serde
@dataclass(unsafe_hash=True)
class OptionalUnion:
    """
    Union Primitives.
    """

    v: Optional[Union[int, str]]


@serde
@dataclass(unsafe_hash=True)
class ContUnion:
    """
    Union Containers.
    """

    v: Union[dict[str, int], list[int], list[str]]


@serde
@dataclass(unsafe_hash=True)
class LitUnion:
    """
    Union of literals
    """

    v: Union[int, Literal["foo", "bar", "*"]]  # noqa


def test_union() -> None:
    v = PriUnion(10)
    s = '{"v":10}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion(10.0)
    s = '{"v":10.0}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion("foo")
    s = '{"v":"foo"}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion(True)
    s = '{"v":true}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)


def test_union_optional() -> None:
    v = PriOptUnion(10)
    s = '{"v":10}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(None)
    s = '{"v":null}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion("foo")
    s = '{"v":"foo"}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(10.0)
    s = '{"v":10.0}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(False)
    s = '{"v":false}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    assert PriOptUnion(None) == from_json(PriOptUnion, "{}")
    assert OptionalUnion(None) == from_json(OptionalUnion, "{}")


def test_union_containers() -> None:
    v = ContUnion([1, 2, 3])
    s = '{"v":[1,2,3]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion(["1", "2", "3"])
    s = '{"v":["1","2","3"]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion({"a": 1, "b": 2, "c": 3})
    s = '{"v":{"a":1,"b":2,"c":3}}'
    assert s == to_json(v)
    # Note: this only works because dict[str, int] comes first in Union otherwise a list would win
    assert v == from_json(ContUnion, s)


def test_union_with_literal() -> None:
    v = LitUnion(10)
    s = '{"v":10}'
    assert s == to_json(v)
    assert v == from_json(LitUnion, s)

    v = LitUnion("foo")
    s = '{"v":"foo"}'
    assert s == to_json(v)
    assert v == from_json(LitUnion, s)

    v = LitUnion("bar")
    s = '{"v":"bar"}'
    assert s == to_json(v)
    assert v == from_json(LitUnion, s)

    v = LitUnion("*")
    s = '{"v":"*"}'
    assert s == to_json(v)
    assert v == from_json(LitUnion, s)

    s = '{"v":"boo"}'

    with pytest.raises(SerdeError):
        from_json(LitUnion, s)


def test_union_with_complex_types() -> None:
    @serde
    class A:
        v: Union[int, IPv4Address, UUID]

    a_int = A(1)
    a_int_json = '{"v":1}'
    assert to_json(a_int) == a_int_json
    assert from_json(A, a_int_json) == a_int
    assert a_int == from_dict(A, to_dict(a_int))

    a_ip = A(IPv4Address("127.0.0.1"))
    a_ip_json = '{"v":"127.0.0.1"}'
    assert to_json(a_ip) == a_ip_json
    assert from_json(A, a_ip_json) == a_ip
    assert a_ip == from_dict(A, to_dict(a_ip))

    a_uid = A(UUID("a317958e-4cbb-4213-9f23-eaff1563c472"))
    a_uid_json = '{"v":"a317958e-4cbb-4213-9f23-eaff1563c472"}'
    assert to_json(a_uid) == a_uid_json
    assert from_json(A, a_uid_json) == a_uid
    assert a_uid == from_dict(A, to_dict(a_uid))


def test_union_with_complex_types_and_reuse_instances() -> None:
    @serde(reuse_instances_default=True)
    class A:
        v: Union[int, IPv4Address, UUID]

    a_int = A(1)
    a_int_roundtrip = from_dict(A, to_dict(a_int))
    assert a_int == a_int_roundtrip
    assert a_int.v is a_int_roundtrip.v

    a_ip = A(IPv4Address("127.0.0.1"))
    a_ip_roundtrip = from_dict(A, to_dict(a_ip))
    assert a_ip == a_ip_roundtrip
    assert a_ip.v is a_ip_roundtrip.v

    a_uid = A(UUID("a317958e-4cbb-4213-9f23-eaff1563c472"))
    a_uid_roundtrip = from_dict(A, to_dict(a_uid))
    assert a_uid == a_uid_roundtrip
    assert a_uid.v is a_uid_roundtrip.v


def test_optional_union_with_complex_types() -> None:
    @serde
    class A:
        v: Optional[Union[int, IPv4Address, UUID]]

    a = A(123)
    assert a == from_dict(A, to_dict(a, reuse_instances=False), reuse_instances=False)
    assert a == from_dict(A, to_dict(a, reuse_instances=True), reuse_instances=True)

    a_none = A(None)
    assert a_none == from_dict(A, to_dict(a_none, reuse_instances=False), reuse_instances=False)
    assert a_none == from_dict(A, to_dict(a_none, reuse_instances=True), reuse_instances=True)


def test_optional_complex_type_with_default() -> None:
    for T, default in [
        (IPv4Address, IPv4Address("127.0.0.1")),
        (UUID, UUID("9c244009-c60d-452b-a378-b8afdc0c2d90")),
    ]:

        @serde
        class A:
            id: Optional[T] = None  # type: ignore[valid-type]

        a = A(default)
        assert a == from_dict(A, to_dict(a, reuse_instances=False), reuse_instances=False)
        assert a == from_dict(A, to_dict(a, reuse_instances=True), reuse_instances=True)

        a_none = A(None)
        assert a_none == from_dict(A, to_dict(a_none, reuse_instances=False), reuse_instances=False)
        assert a_none == from_dict(A, to_dict(a_none, reuse_instances=True), reuse_instances=True)

        a_default = A()
        assert a_default == from_dict(
            A, to_dict(a_default, reuse_instances=False), reuse_instances=False
        )
        assert a_default == from_dict(
            A, to_dict(a_default, reuse_instances=True), reuse_instances=True
        )


def test_union_with_complex_types_in_containers() -> None:
    @serde
    class A:
        v: Union[list[IPv4Address], list[UUID]]

    a_ips = A([IPv4Address("127.0.0.1"), IPv4Address("10.0.0.1")])
    assert a_ips == from_dict(A, to_dict(a_ips, reuse_instances=False), reuse_instances=False)
    assert a_ips == from_dict(A, to_dict(a_ips, reuse_instances=True), reuse_instances=True)

    a_uids = A(
        [UUID("9c244009-c60d-452b-a378-b8afdc0c2d90"), UUID("5831dc09-20fe-4433-b476-5866b7143364")]
    )
    assert a_uids == from_dict(A, to_dict(a_uids, reuse_instances=False), reuse_instances=False)
    assert a_uids == from_dict(A, to_dict(a_uids, reuse_instances=True), reuse_instances=True)

    a_empty = A([])
    assert a_empty == from_dict(A, to_dict(a_empty, reuse_instances=False), reuse_instances=False)
    assert a_empty == from_dict(A, to_dict(a_empty, reuse_instances=True), reuse_instances=True)


def test_union_exception_if_nothing_matches() -> None:
    @serde
    class A:
        v: Union[IPv4Address, UUID]

    with pytest.raises(SerdeError) as ex1:
        from_dict(A, {"v": "not-ip-or-uuid"})
    assert str(ex1.value) == (
        "Can not deserialize 'not-ip-or-uuid' of type str into Union[IPv4Address, UUID].\n"
        "Reasons:\n"
        " Failed to deserialize into IPv4Address: Expected 4 octets in 'not-ip-or-uuid'\n"
        " Failed to deserialize into UUID: badly formed hexadecimal UUID string"
    )

    with pytest.raises(SerdeError) as ex2:
        from_dict(A, {"v": "not-ip-or-uuid"}, reuse_instances=True)
    assert str(ex2.value) == (
        "Can not deserialize 'not-ip-or-uuid' of type str into Union[IPv4Address, UUID].\n"
        "Reasons:\n"
        " Failed to deserialize into IPv4Address: Expected 4 octets in 'not-ip-or-uuid'\n"
        " Failed to deserialize into UUID: badly formed hexadecimal UUID string"
    )

    with pytest.raises(SerdeError) as ex3:
        from_dict(A, {"v": None})
    # omit reason because it is not the same for all python versions & operating systems
    assert str(ex3.value).startswith(
        "Can not deserialize None of type NoneType into Union[IPv4Address, UUID]."
    )

    with pytest.raises(SerdeError) as ex4:
        a = A(uuid.uuid4())
        a.v = "not-ip-or-uuid"  # type: ignore
        to_dict(a)
    assert (
        str(ex4.value)
        == "Can not serialize 'not-ip-or-uuid' of type str for Union[IPv4Address, UUID]"
    )

    with pytest.raises(SerdeError) as ex5:
        a = A(uuid.uuid4())
        a.v = "not-ip-or-uuid"  # type: ignore
        to_dict(a, reuse_instances=True)
    assert (
        str(ex5.value)
        == "Can not serialize 'not-ip-or-uuid' of type str for Union[IPv4Address, UUID]"
    )

    with pytest.raises(SerdeError) as ex6:
        a = A(uuid.uuid4())
        a.v = None  # type: ignore
        to_dict(a, reuse_instances=True)
    assert str(ex6.value) == "Can not serialize None of type NoneType for Union[IPv4Address, UUID]"


def test_union_in_union() -> None:
    @serde
    class A:
        v: Union[UUID, Union[int, str]]

    a_uuid = A(UUID("00611ee9-7ca3-41d3-9607-ea7268e264ea"))
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=False), reuse_instances=False)
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=True), reuse_instances=True)

    a_int = A(1)
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=False), reuse_instances=False)
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=True), reuse_instances=True)

    a_str = A("hello")
    assert a_str == from_dict(A, to_dict(a_str, reuse_instances=False), reuse_instances=False)
    assert a_str == from_dict(A, to_dict(a_str, reuse_instances=True), reuse_instances=True)


def test_union_in_other_type() -> None:
    @serde
    class A:
        v: dict[str, Union[UUID, int]]

    a_uuid = A({"key": UUID("00611ee9-7ca3-41d3-9607-ea7268e264ea")})
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=False), reuse_instances=False)
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=True), reuse_instances=True)

    a_int = A({"key": 1})
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=False), reuse_instances=False)
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=True), reuse_instances=True)


def test_union_rename_all() -> None:
    @serde(rename_all="pascalcase")
    class Foo:
        bar_baz: Union[int, str]

    assert to_dict(Foo(10)) == {"BarBaz": 10}
    assert from_dict(Foo, {"BarBaz": "foo"}) == Foo("foo")


def test_union_with_list_of_other_class() -> None:
    @serde
    class A:
        a: int

    @serde
    class B:
        b: Union[list[A], str]

    b = B([A(1)])
    b_dict = {"b": [{"a": 1}]}
    assert to_dict(b) == b_dict
    assert from_dict(B, b_dict) == b


# relates to https://github.com/yukinarit/pyserde/issues/113
def test_union_with_union_in_nested_types() -> None:
    @serde
    class A:
        v: Union[UUID, list[Union[UUID, int]]]

    a_uuid = A([UUID("00611ee9-7ca3-41d3-9607-ea7268e264ea")])
    assert to_dict(a_uuid, reuse_instances=False) == {"v": ["00611ee9-7ca3-41d3-9607-ea7268e264ea"]}
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=False), reuse_instances=False)
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=True), reuse_instances=True)

    a_int = A([1])
    assert to_dict(a_int) == {"v": [1]}
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=False), reuse_instances=False)
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=True), reuse_instances=True)


# relates to https://github.com/yukinarit/pyserde/issues/113
def test_union_with_union_in_nested_tuple() -> None:
    @serde
    class A:
        v: Union[bool, tuple[Union[str, int]]]

    a_bool = A(False)
    a_bool_dict = {"v": False}
    assert to_dict(a_bool) == a_bool_dict
    assert from_dict(A, a_bool_dict) == a_bool

    a_str = A(("a",))
    a_str_dict = {"v": ("a",)}
    assert to_dict(a_str) == a_str_dict
    assert from_dict(A, a_str_dict) == a_str

    a_int = A((1,))
    a_int_dict = {"v": (1,)}
    assert to_dict(a_int) == a_int_dict
    assert from_dict(A, a_int_dict) == a_int


@pytest.mark.skip(reason="Known issue with generic union deserialization - TODO fix")
def test_generic_union() -> None:
    T = TypeVar("T")
    U = TypeVar("U")

    @serde
    class Foo(Generic[T]):
        v: T

    @serde
    class Bar(Generic[U]):
        v: U

    @serde
    class A:
        v: Union[Foo[int], Bar[str]]

    a = A(Foo[int](10))
    assert a == from_dict(A, to_dict(a))
    assert a == from_tuple(A, to_tuple(a))

    a = A(Bar[str]("foo"))
    assert a == from_dict(A, to_dict(a))
    assert a == from_tuple(A, to_tuple(a))

    @serde
    class B(Generic[T, U]):
        v: Union[Foo[T], Bar[U]]

    b = B[int, str](Foo[int](10))
    assert b == from_dict(B[int, str], to_dict(b))
    assert b == from_tuple(B[int, str], to_tuple(b))

    b = B[Foo[int], Bar[str]](Foo(Foo(10)))  # type: ignore[assignment]
    assert {"v": {"v": {"v": 10}}} == to_dict(b)
    # TODO Nested union generic still doesn't work
    # assert b == from_dict(B[Foo[int], Bar[str]], to_dict(b))


def test_external_tagging() -> None:
    @serde
    class Bar:
        b: int

    @serde
    class Baz:
        b: int

    @serde
    class Nested:
        v: Union[Bar, Baz]

    @serde
    class Foo:
        a: Union[Bar, Baz]
        b: Union[int, str]
        c: Union[dict[int, str], list[int]]
        d: Union[int, Nested]

    f = Foo(Bar(10), "foo", {10: "bar"}, Nested(Baz(100)))
    d = {
        "a": {
            "Bar": {"b": 10}
        },  # Union of dataclasses will be (de)serialized with external tagging
        "b": "foo",  # non dataclass will be untagged
        "c": {10: "bar"},
        "d": {"Nested": {"v": {"Baz": {"b": 100}}}},
    }
    assert to_dict(f) == d
    assert from_dict(Foo, d) == f

    @serde
    class FooMixed:
        a: Union[Bar, int]  # Mix of dataclass and non dataclass

    f_mixed = FooMixed(Bar(10))
    assert from_dict(FooMixed, to_dict(f_mixed)) == f_mixed
    f_mixed2 = FooMixed(10)
    assert from_dict(FooMixed, to_dict(f_mixed2)) == f_mixed2

    @serde
    class FooUnion:
        a: Union[Bar, Baz]

    f_union = FooUnion(Bar(10))
    assert f_union  # Use the variable

    # Tag not found
    with pytest.raises(SerdeError):
        assert from_dict(Foo, {"a": {"TagNotFound": {"b": 10}}})

    # Tag is correct, but incompatible data
    with pytest.raises(SerdeError):
        assert from_dict(Foo, {"a": {"Bar": {"c": 10}}})


def test_internal_tagging() -> None:
    from serde import InternalTagging

    @serde
    class Bar:
        v: int

    @serde
    class Baz:
        v: int

    @serde(tagging=InternalTagging("type"))
    class Nested:
        v: Union[Bar, Baz]

    @serde(tagging=InternalTagging("type"))
    class FooInternalComplete:
        a: Union[Bar, Baz]
        b: Union[int, str]
        c: Union[dict[int, str], list[int]]
        d: Union[int, Nested]

    f = FooInternalComplete(Bar(10), "foo", {10: "bar"}, Nested(Baz(100)))
    d = {
        "a": {
            "type": "Bar",
            "v": 10,
        },  # Union of dataclasses will be (de)serialized with internal tagging
        "b": "foo",  # non dataclass will be untagged
        "c": {10: "bar"},
        "d": {"type": "Nested", "v": {"type": "Baz", "v": 100}},
    }
    assert to_dict(f) == d
    assert from_dict(FooInternalComplete, d) == f

    @serde(tagging=InternalTagging("type"))
    class FooInternal:
        a: Union[Bar, Baz]

    f_internal = FooInternal(Bar(10))
    assert f_internal  # Use the variable

    # Tag not found
    with pytest.raises(SerdeError):
        assert from_dict(FooInternal, {"a": {"TagNotFound": "", "v": 10}})

    # Tag is correct, but incompatible data
    with pytest.raises(SerdeError):
        assert from_dict(FooInternal, {"a": {"type": "Bar", "c": 10}})

    with pytest.raises(TypeError):
        # Tag is not specified in attribute
        @serde(tagging=InternalTagging())  # type: ignore[call-overload]
        class FooErrorTest:
            pass


def test_adjacent_tagging() -> None:
    from serde import AdjacentTagging

    @serde
    class Bar:
        v: int

    @serde
    class Baz:
        v: int

    @serde(tagging=AdjacentTagging("type", "content"))
    class Nested:
        v: Union[Bar, Baz]

    @serde(tagging=AdjacentTagging("type", "content"))
    class Foo:
        a: Union[Bar, Baz]
        b: Union[int, str]
        c: Union[dict[int, str], list[int]]
        d: Union[int, Nested]

    f = Foo(Bar(10), "foo", {10: "bar"}, Nested(Baz(100)))
    d = {
        "a": {
            "type": "Bar",
            "content": {"v": 10},
        },  # Union of dataclasses will be (de)serialized with adjacent tagging
        "b": "foo",  # non dataclass will be untagged
        "c": {10: "bar"},
        "d": {"type": "Nested", "content": {"v": {"type": "Baz", "content": {"v": 100}}}},
    }
    assert to_dict(f) == d
    assert from_dict(Foo, d) == f

    @serde(tagging=AdjacentTagging("type", "content"))
    class FooAdjacent:
        a: Union[Bar, Baz]

    f_adjacent = FooAdjacent(Bar(10))
    assert f_adjacent  # Use the variable

    # Tag not found
    with pytest.raises(SerdeError):
        assert from_dict(FooAdjacent, {"a": {"TagNotFound": "", "content": {"v": 10}}})

    # Content tag not found
    with pytest.raises(SerdeError):
        assert from_dict(FooAdjacent, {"a": {"type": "Bar", "TagNotFound": {"v": 10}}})

    # Tag is correct, but incompatible data
    with pytest.raises(SerdeError):
        assert from_dict(FooAdjacent, {"a": {"type": "Bar", "content": {"c": 10}}})

    with pytest.raises(TypeError):
        # Tag is not specified in attribute
        @serde(tagging=AdjacentTagging(content="content"))  # type: ignore[call-overload]
        class FooContentError:
            pass

    with pytest.raises(TypeError):
        # Content is not specified in attribute
        @serde(tagging=AdjacentTagging(tag="tag"))  # type: ignore[call-overload]
        class FooTagError:
            pass

    with pytest.raises(TypeError):
        # Tag/Content is not specified in attribute
        @serde(tagging=AdjacentTagging())  # type: ignore[call-overload]
        class FooNoArgsError:
            pass


def test_untagged() -> None:
    from serde import Untagged

    @serde
    class Bar:
        v: int

    @serde
    class Baz:
        v: int

    @serde(tagging=Untagged)
    class Nested:
        v: Union[Bar, Baz]

    @serde(tagging=Untagged)
    class Foo:
        a: Union[Bar, Baz]
        b: Union[int, str]
        c: Union[dict[int, str], list[int]]
        d: Union[int, Nested]

    f = Foo(Bar(10), "foo", {10: "bar"}, Nested(Bar(100)))
    d = {"a": {"v": 10}, "b": "foo", "c": {10: "bar"}, "d": {"v": {"v": 100}}}
    assert to_dict(f) == d
    assert from_dict(Foo, d) == f

    @serde(tagging=Untagged)
    class FooUntagged:
        a: Union[Bar, Baz]

    f_untagged = FooUntagged(Baz(10))

    # Untagged can't differenciate the dataclass with similar fields
    with pytest.raises(AssertionError):
        assert to_dict(from_dict(FooUntagged, d)) == f_untagged  # type: ignore[comparison-overlap]

    # Untaggled can't differenciate dict and list.
    @serde
    class FooListDict:
        a: Union[list[int], dict[int, str]]

    f_listdict = FooListDict({10: "bar"})
    with pytest.raises(SerdeError):
        assert to_dict(from_dict(FooListDict, d)) == f_listdict  # type: ignore[comparison-overlap]


def test_newtype_and_untagged_union() -> None:
    """
    Regression test for
    https://github.com/yukinarit/pyserde/issues/292
    """
    from serde import Untagged

    OtherNewtypeThing = NewType("OtherNewtypeThing", str)

    @serde
    class SupposedlyUnrelated:
        name: OtherNewtypeThing

    @serde
    class Innerclass:
        inner_value: str = "SHOULD_NOT_APPEAR"

    @serde(tagging=Untagged)
    class MyDataclass:
        unrelateds: list[SupposedlyUnrelated]
        buggy_field: list[Union[str, Innerclass]]

    data = {"unrelateds": [], "buggy_field": [{"inner_value": "value"}, "something"]}
    actual = from_dict(MyDataclass, data)

    assert isinstance(actual.buggy_field[0], Innerclass)
    assert isinstance(actual.buggy_field[1], str)


def test_union_directly() -> None:
    @dataclass
    class Foo:
        v: int

    @dataclass
    class Bar:
        w: str

    bar = Bar("bar")

    # externally tagged
    s = to_json(bar, cls=Union[Foo, Bar])
    assert bar == from_json(Union[Foo, Bar], s)

    # internally tagged
    s = to_json(bar, cls=InternalTagging("type", Union[Foo, Bar]))
    assert bar == from_json(InternalTagging("type", Union[Foo, Bar]), s)

    # adjacently tagged
    s = to_json(bar, cls=AdjacentTagging("type", "content", Union[Foo, Bar]))
    assert bar == from_json(AdjacentTagging("type", "content", Union[Foo, Bar]), s)

    # untagged tagged
    s = to_json(bar, cls=Untagged(Union[Foo, Bar]))
    assert bar == from_json(Untagged(Union[Foo, Bar]), s)


def test_union_frozenset_with_prim() -> None:
    @serde
    @dataclass
    class Foo:
        a: Union[frozenset[int], int]

    assert to_dict(Foo(frozenset({1}))) == {"a": {1}}


def test_union_with_any() -> None:
    @dataclass
    class FooWithString:
        foo: str

    @dataclass
    class BarWithDict:
        bar: dict[str, Any]

    @serde(tagging=Untagged)
    @dataclass
    class Class:
        foobars: list[Union[FooWithString, BarWithDict]]

    c = Class([FooWithString("string"), BarWithDict({"key": "value"})])
    assert c == from_json(Class, to_json(c))


def test_union_with_different_ordering() -> None:

    @serde
    class Expr:
        expr: str

    @serde
    class Foo:
        a: Union[str, Expr]
        b: Union[Expr, str]
        c: Union[Expr, str]

    f = Foo("1", Expr("2"), "3")
    s = '{"a":"1","b":{"Expr":{"expr":"2"}},"c":"3"}'
    assert s == to_json(f)
    assert f == from_json(Foo, s)


def test_union_internal_tagging_for_non_dataclass() -> None:
    @serde
    class Bar:
        a: int

    @serde(tagging=InternalTagging("type"))
    class Foo:
        x: Union[list[int], Bar]

    f = Foo(Bar(1))
    assert f == from_json(Foo, to_json(f))

    f = Foo([10])
    assert f == from_json(Foo, to_json(f))


def test_union_internal_tagging_cache_conflict_different_case() -> None:
    @serde
    class Foo:
        v: int

    @serde
    class Bar:
        v: int

    union_upper = InternalTagging("TAG")(Union[Foo, Bar])
    deserialized_upper = Foo(1)
    serialized_upper = '{"v":1,"TAG":"Foo"}'
    assert from_json(union_upper, serialized_upper) == deserialized_upper
    assert to_json(deserialized_upper, union_upper) == serialized_upper

    union_lower = InternalTagging("tag")(Union[Foo, Bar])
    deserialized_lower = Foo(1)
    serialized_lower = '{"v":1,"tag":"Foo"}'
    assert from_json(union_lower, serialized_lower) == deserialized_lower
    assert to_json(deserialized_lower, union_lower) == serialized_lower
