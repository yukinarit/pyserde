import logging
from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Dict, Generic, List, Optional, Tuple, TypeVar, Union
from uuid import UUID

import pytest

from serde import SerdeError, from_dict, from_tuple
from serde import init as serde_init
from serde import logger, serde, to_dict, to_tuple
from serde.json import from_json, to_json

logging.basicConfig(level=logging.WARNING)
logger.setLevel(logging.DEBUG)

serde_init(True)


@serde
@dataclass(unsafe_hash=True)
class PriUnion:
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
class ContUnion:
    """
    Union Containers.
    """

    v: Union[Dict[str, int], List[int], List[str]]


def test_union():
    v = PriUnion(10)
    s = '{"v": 10}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion(10.0)
    s = '{"v": 10.0}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion('foo')
    s = '{"v": "foo"}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion(True)
    s = '{"v": true}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)


def test_union_optional():
    v = PriOptUnion(10)
    s = '{"v": 10}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(None)
    s = '{"v": null}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion("foo")
    s = '{"v": "foo"}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(10.0)
    s = '{"v": 10.0}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(False)
    s = '{"v": false}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)


def test_union_containers():
    v = ContUnion([1, 2, 3])
    s = '{"v": [1, 2, 3]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion(['1', '2', '3'])
    s = '{"v": ["1", "2", "3"]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion({'a': 1, 'b': 2, 'c': 3})
    s = '{"v": {"a": 1, "b": 2, "c": 3}}'
    assert s == to_json(v)
    # Note: this only works because Dict[str, int] comes first in Union otherwise a List would win
    assert v == from_json(ContUnion, s)


def test_union_with_complex_types():
    @serde
    class A:
        v: Union[int, IPv4Address, UUID]

    a_int = A(1)
    a_int_json = '{"v": 1}'
    assert to_json(a_int) == a_int_json
    assert from_json(A, a_int_json) == a_int
    assert a_int == from_dict(A, to_dict(a_int))

    a_ip = A(IPv4Address("127.0.0.1"))
    a_ip_json = '{"v": "127.0.0.1"}'
    assert to_json(a_ip) == a_ip_json
    assert from_json(A, a_ip_json) == a_ip
    assert a_ip == from_dict(A, to_dict(a_ip))

    a_uid = A(UUID("a317958e-4cbb-4213-9f23-eaff1563c472"))
    a_uid_json = '{"v": "a317958e-4cbb-4213-9f23-eaff1563c472"}'
    assert to_json(a_uid) == a_uid_json
    assert from_json(A, a_uid_json) == a_uid
    assert a_uid == from_dict(A, to_dict(a_uid))


def test_union_with_complex_types_and_reuse_instances():
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


def test_optional_union_with_complex_types():
    @serde
    class A:
        v: Optional[Union[int, IPv4Address, UUID]]

    a = A(123)
    assert a == from_dict(A, to_dict(a, reuse_instances=False), reuse_instances=False)
    assert a == from_dict(A, to_dict(a, reuse_instances=True), reuse_instances=True)

    a_none = A(None)
    assert a_none == from_dict(A, to_dict(a_none, reuse_instances=False), reuse_instances=False)
    assert a_none == from_dict(A, to_dict(a_none, reuse_instances=True), reuse_instances=True)


def test_union_with_complex_types_in_containers():
    @serde
    class A:
        v: Union[List[IPv4Address], List[UUID]]

    a_ips = A([IPv4Address("127.0.0.1"), IPv4Address("10.0.0.1")])
    assert a_ips == from_dict(A, to_dict(a_ips, reuse_instances=False), reuse_instances=False)
    assert a_ips == from_dict(A, to_dict(a_ips, reuse_instances=True), reuse_instances=True)

    a_uids = A([UUID("9c244009-c60d-452b-a378-b8afdc0c2d90"), UUID("5831dc09-20fe-4433-b476-5866b7143364")])
    assert a_uids == from_dict(A, to_dict(a_uids, reuse_instances=False), reuse_instances=False)
    assert a_uids == from_dict(A, to_dict(a_uids, reuse_instances=True), reuse_instances=True)

    a_empty = A([])
    assert a_empty == from_dict(A, to_dict(a_empty, reuse_instances=False), reuse_instances=False)
    assert a_empty == from_dict(A, to_dict(a_empty, reuse_instances=True), reuse_instances=True)


def test_union_exception_if_nothing_matches():
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
    assert str(ex3.value).startswith("Can not deserialize None of type NoneType into Union[IPv4Address, UUID].")

    with pytest.raises(SerdeError) as ex4:
        to_dict(A("not-ip-or-uuid"))
    assert str(ex4.value) == "Can not serialize 'not-ip-or-uuid' of type str for Union[IPv4Address, UUID]"

    with pytest.raises(SerdeError) as ex5:
        to_dict(A("not-ip-or-uuid"), reuse_instances=True)
    assert str(ex5.value) == "Can not serialize 'not-ip-or-uuid' of type str for Union[IPv4Address, UUID]"

    with pytest.raises(SerdeError) as ex6:
        to_dict(A(None), reuse_instances=True)
    assert str(ex6.value) == "Can not serialize None of type NoneType for Union[IPv4Address, UUID]"


def test_union_in_union():
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


def test_union_in_other_type():
    @serde
    class A:
        v: Dict[str, Union[UUID, int]]

    a_uuid = A({"key": UUID("00611ee9-7ca3-41d3-9607-ea7268e264ea")})
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=False), reuse_instances=False)
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=True), reuse_instances=True)

    a_int = A({"key": 1})
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=False), reuse_instances=False)
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=True), reuse_instances=True)


def test_union_rename_all():
    @serde(rename_all='pascalcase')
    class Foo:
        bar_baz: Union[int, str]

    assert to_dict(Foo(10)) == {'BarBaz': 10}
    assert from_dict(Foo, {'BarBaz': 'foo'}) == Foo('foo')


def test_union_with_list_of_other_class():
    @serde
    class A:
        a: int

    @serde
    class B:
        b: Union[List[A], str]

    b = B([A(1)])
    b_dict = {"b": [{"a": 1}]}
    assert to_dict(b) == b_dict
    assert from_dict(B, b_dict) == b


# relates to https://github.com/yukinarit/pyserde/issues/113
def test_union_with_union_in_nested_types():
    @serde
    class A:
        v: Union[UUID, List[Union[UUID, int]]]

    a_uuid = A([UUID("00611ee9-7ca3-41d3-9607-ea7268e264ea")])
    assert to_dict(a_uuid, reuse_instances=False) == {"v": ["00611ee9-7ca3-41d3-9607-ea7268e264ea"]}
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=False), reuse_instances=False)
    assert a_uuid == from_dict(A, to_dict(a_uuid, reuse_instances=True), reuse_instances=True)

    a_int = A([1])
    assert to_dict(a_int) == {"v": [1]}
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=False), reuse_instances=False)
    assert a_int == from_dict(A, to_dict(a_int, reuse_instances=True), reuse_instances=True)


# relates to https://github.com/yukinarit/pyserde/issues/113
def test_union_with_union_in_nested_tuple():
    @serde
    class A:
        v: Union[bool, Tuple[Union[str, int]]]

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


def test_generic_union():
    T = TypeVar('T')
    U = TypeVar('U')

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

    a = A(Foo[str]("foo"))
    assert a == from_dict(A, to_dict(a))
    assert a == from_tuple(A, to_tuple(a))

    @serde
    class B(Generic[T, U]):
        v: Union[Foo[T], Bar[U]]

    b = B[int, str](Foo[int](10))
    assert b == from_dict(B[int, str], to_dict(b))
    assert b == from_tuple(B[int, str], to_tuple(b))

    b = B[Foo[int], Bar[str]](Foo(Foo(10)))
    assert {'v': {'v': {'v': 10}}} == to_dict(b)
    # TODO Nested union generic still doesn't work
    # assert b == from_dict(B[Foo[int], Bar[str]], to_dict(b))


def test_external_tagging():
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
        c: Union[Dict[int, str], List[int]]
        d: Union[int, Nested]

    f = Foo(Bar(10), 'foo', {10: 'bar'}, Nested(Baz(100)))
    d = {
        "a": {"Bar": {"b": 10}},  # Union of dataclasses will be (de)serialized with external tagging
        "b": "foo",  # non dataclass will be untagged
        "c": {10: "bar"},
        "d": {"Nested": {"v": {"Baz": {"b": 100}}}},
    }
    assert to_dict(f) == d
    assert from_dict(Foo, d) == f

    @serde
    class Foo:
        a: Union[Bar, int]  # Mix of dataclass and non dataclass

    f = Foo(Bar(10))
    assert from_dict(Foo, to_dict(f)) == f
    f = Foo(10)
    assert from_dict(Foo, to_dict(f)) == f

    @serde
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Bar(10))

    # Tag not found
    with pytest.raises(Exception):
        assert from_dict(Foo, {"a": {"TagNotFound": {"b": 10}}})

    # Tag is correct, but incompatible data
    with pytest.raises(Exception):
        assert from_dict(Foo, {"a": {"Bar": {"c": 10}}})


def test_internal_tagging():
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
    class Foo:
        a: Union[Bar, Baz]
        b: Union[int, str]
        c: Union[Dict[int, str], List[int]]
        d: Union[int, Nested]

    f = Foo(Bar(10), 'foo', {10: 'bar'}, Nested(Baz(100)))
    d = {
        "a": {"type": "Bar", "v": 10},  # Union of dataclasses will be (de)serialized with internal tagging
        "b": "foo",  # non dataclass will be untagged
        "c": {10: "bar"},
        "d": {"type": "Nested", "v": {"type": "Baz", "v": 100}},
    }
    assert to_dict(f) == d
    assert from_dict(Foo, d) == f

    @serde(tagging=InternalTagging("type"))
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Bar(10))

    # Tag not found
    with pytest.raises(Exception):
        assert from_dict(Foo, {"a": {"TagNotFound": "", "v": 10}})

    # Tag is correct, but incompatible data
    with pytest.raises(Exception):
        assert from_dict(Foo, {"a": {"type": "Bar", "c": 10}})

    with pytest.raises(SerdeError):
        # Tag is not specified in attribute
        @serde(tagging=InternalTagging())
        class Foo:
            pass


def test_adjacent_tagging():
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
        c: Union[Dict[int, str], List[int]]
        d: Union[int, Nested]

    f = Foo(Bar(10), 'foo', {10: 'bar'}, Nested(Baz(100)))
    d = {
        "a": {"type": "Bar", "content": {"v": 10}},  # Union of dataclasses will be (de)serialized with adjacent tagging
        "b": "foo",  # non dataclass will be untagged
        "c": {10: "bar"},
        "d": {"type": "Nested", "content": {"v": {"type": "Baz", "content": {"v": 100}}}},
    }
    assert to_dict(f) == d
    assert from_dict(Foo, d) == f

    @serde(tagging=AdjacentTagging("type", "content"))
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Bar(10))

    # Tag not found
    with pytest.raises(Exception):
        assert from_dict(Foo, {"a": {"TagNotFound": "", "content": {"v": 10}}})

    # Content tag not found
    with pytest.raises(Exception):
        assert from_dict(Foo, {"a": {"type": "Bar", "TagNotFound": {"v": 10}}})

    # Tag is correct, but incompatible data
    with pytest.raises(Exception):
        assert from_dict(Foo, {"a": {"type": "Bar", "content": {"c": 10}}})

    with pytest.raises(SerdeError):
        # Tag is not specified in attribute
        @serde(tagging=AdjacentTagging(content="content"))
        class Foo:
            pass

    with pytest.raises(SerdeError):
        # Content is not specified in attribute
        @serde(tagging=AdjacentTagging(tag="tag"))
        class Foo:
            pass

    with pytest.raises(SerdeError):
        # Tag/Content is not specified in attribute
        @serde(tagging=AdjacentTagging())
        class Foo:
            pass


def test_untagged():
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
        c: Union[Dict[int, str], List[int]]
        d: Union[int, Nested]

    f = Foo(Bar(10), 'foo', {10: 'bar'}, Nested(Bar(100)))
    d = {"a": {"v": 10}, "b": "foo", "c": {10: "bar"}, "d": {"v": {"v": 100}}}
    assert to_dict(f) == d
    assert from_dict(Foo, d) == f

    @serde(tagging=Untagged)
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Baz(10))

    # Untagged can't differenciate the dataclass with similar fields
    with pytest.raises(Exception):
        assert to_dict(from_dict(Foo, d)) == f

    # Untaggled can't differenciate Dict and List.
    @serde
    class Foo:
        a: Union[List[int], Dict[int, str]]

    f = Foo({10: 'bar'})
    with pytest.raises(Exception):
        assert to_dict(from_dict(Foo, d)) == f
