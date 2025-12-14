import sys
import pytest
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generic, NewType, Optional, TypeVar, Union, Literal
from collections.abc import Sequence, MutableSequence

from serde import serde, field, is_serializable, is_deserializable, SerdeError
from serde.compat import (
    get_generic_arg,
    is_dict,
    is_generic,
    is_list,
    is_opt,
    is_primitive,
    is_set,
    is_tuple,
    is_union,
    iter_types,
    iter_unions,
    type_args,
    typename,
    union_args,
)
from serde.core import is_instance

from .data import Bool, Float, Int, Pri, PriOpt, Str

T = TypeVar("T")
U = TypeVar("U")


def test_types() -> None:
    assert is_list(list[int])
    assert is_list(list)
    assert is_list(Sequence[int])
    assert is_list(Sequence)
    assert is_list(MutableSequence[int])
    assert is_list(MutableSequence)
    assert is_set(set[int])
    assert is_set(set)
    assert is_tuple(tuple[int, int, int])
    assert is_tuple(tuple)
    assert is_tuple(tuple[int, ...])
    assert is_dict(dict[str, int])
    assert is_dict(dict)
    assert is_opt(Optional[int])
    assert is_opt(Union[int, None])
    assert is_union(Union[int, str])
    assert is_union(Union[Optional[int], Optional[str]])
    assert is_union(Optional[int])
    assert not is_opt(Union[Optional[int], Optional[str]])
    assert is_union(Union[Optional[int], Optional[str]])

    assert is_list(list)
    assert is_set(set)
    assert is_tuple(tuple)
    assert is_dict(dict)

    Int = NewType("Int", int)
    assert is_primitive(int)
    assert is_primitive(Int)  # type: ignore[arg-type]

    if sys.version_info[:3] >= (3, 10, 0):
        assert is_union(str | int)
        assert is_union(str | None)
        assert is_opt(str | None)


def test_typename() -> None:
    @serde
    class Bar(Generic[T]):
        v: T

    @serde
    class Foo(Generic[T]):
        nested: Bar[T]

    assert typename(Foo[int]) == "Foo"
    assert typename(Foo) == "Foo"
    assert typename(list[int]) == "list[int]"
    assert typename(Optional) == "Optional"
    assert typename(list) == "list"
    assert typename(list[int]) == "list[int]"
    assert typename(tuple) == "tuple"
    assert typename(tuple[int, str]) == "tuple[int, str]"
    assert typename(tuple[int, ...]) == "tuple[int, ...]"
    assert typename(dict) == "dict"
    assert typename(dict[str, Foo]) == "dict[str, Foo]"  # type: ignore
    assert typename(set) == "set"
    assert typename(set[int]) == "set[int]"
    assert typename(Literal[1, True, "Hey"]) == "Literal[1, True, 'Hey']"


def test_iter_types() -> None:
    assert {Pri, int, str, float, bool} == set(iter_types(Pri))
    assert {dict, str, Pri, int, float, bool} == set(iter_types(dict[str, Pri]))
    assert {list, str} == set(iter_types(list[str]))
    assert {set, str} == set(iter_types(set[str]))
    assert {tuple, int, str, bool, float} == set(iter_types(tuple[int, str, bool, float]))
    assert {tuple, int, Ellipsis} == set(iter_types(tuple[int, ...]))
    assert {PriOpt, Optional, int, str, float, bool} == set(iter_types(PriOpt))

    @serde
    class Foo:
        a: int
        b: datetime
        c: datetime
        d: Optional[str] = None
        e: Union[str, int] = 10
        f: list[int] = field(default_factory=list)
        g: set[int] = field(default_factory=set)

    assert {Foo, datetime, Optional, str, Union, list, set, int} == set(iter_types(Foo))


def test_iter_unions() -> None:
    assert [Union[str, int]] == list(iter_unions(Union[str, int]))
    assert [Union[str, int]] == list(iter_unions(dict[str, Union[str, int]]))
    assert [Union[str, int]] == list(iter_unions(tuple[Union[str, int]]))
    assert [Union[str, int]] == list(iter_unions(list[Union[str, int]]))
    assert [Union[str, int]] == list(iter_unions(set[Union[str, int]]))
    assert [Union[str, int, type(None)]] == list(iter_unions(Optional[Union[str, int]]))

    @dataclass
    class A:
        a: list[Union[int, str]]
        b: dict[str, list[Union[float, int]]]
        C: dict[Union[bool, str], Union[float, int]]

    assert {Union[int, str], Union[float, int], Union[bool, str], Union[float, int]} == set(
        iter_unions(A)
    )


def test_type_args() -> None:
    assert (int,) == type_args(list[int])
    assert (int, str) == type_args(dict[int, str])
    assert (int, type(None)) == type_args(Optional[int])
    assert (Optional[int],) == type_args(list[Optional[int]])  # type: ignore
    assert (list[int], type(None)) == type_args(Optional[list[int]])
    assert (list[int], dict[str, int]) == type_args(Union[list[int], dict[str, int]])
    assert (int, type(None), str) == type_args(Union[Optional[int], str])
    assert (int, Ellipsis) == type_args(tuple[int, ...])  # type: ignore


def test_union_args() -> None:
    assert (int, str) == union_args(Union[int, str])
    assert (list[int], dict[int, str]) == union_args(Union[list[int], dict[int, str]])
    assert (Optional[int], str) == union_args(Union[Optional[int], str])  # type: ignore


def test_is_instance() -> None:
    # primitive
    assert is_instance(10, int)
    assert is_instance("str", str)
    assert is_instance(1.0, float)
    assert is_instance(False, bool)
    assert not is_instance(10.0, int)
    assert not is_instance("10", int)
    assert is_instance(True, int)  # see why this is true https://stackoverflow.com/a/37888668

    # dataclass
    p = Pri(i=10, s="foo", f=100.0, b=True)
    assert is_instance(p, Pri)
    p.i = 10.0  # type: ignore
    assert is_instance(p, Pri)  # there is no way to check mulated properties.

    # dataclass (Nested)
    @dataclass
    class Foo:
        p: Pri

    h = Foo(Pri(i=10, s="foo", f=100.0, b=True))
    assert is_instance(h, Foo)
    h.p.i = 10.0  # type: ignore
    assert is_instance(h, Foo)

    # list
    assert is_instance([], list[int])
    assert is_instance([10], list)
    assert is_instance([10], list)
    assert is_instance([10], list[int])
    assert not is_instance([10.0], list[int])
    assert not is_instance((10, 20), list[int])

    # list of dataclass
    assert is_instance([Int(n) for n in range(1, 10)], list[Int])
    assert not is_instance([Str("foo")], list[Int])

    # sequence
    assert is_instance([10], Sequence[int])
    assert is_instance((10, 20), Sequence[int])
    assert not is_instance(("a", "b"), Sequence[int])
    assert not is_instance("ab", Sequence[str])

    # mutable sequence
    assert is_instance([10], MutableSequence[int])
    assert not is_instance((10, 20), MutableSequence[int])
    assert not is_instance("ab", MutableSequence[str])

    # set
    assert is_instance(set(), set[int])
    assert is_instance({10}, set)
    assert is_instance({10}, set[int])
    assert not is_instance({10.0}, set[int])

    # set of dataclass
    assert is_instance({Int(n) for n in range(1, 10)}, set[Int])
    assert not is_instance({Str("foo")}, set[Int])
    # tuple
    assert not is_instance((), tuple[int, str, float, bool])
    assert is_instance((10, "a"), tuple)
    assert is_instance((10, "foo", 100.0, True), tuple[int, str, float, bool])
    assert not is_instance((10, "foo", 100.0, "last-type-is-wrong"), tuple[int, str, float, bool])
    assert is_instance((10, 20), tuple[int, ...])
    assert is_instance((10, 20, 30), tuple[int, ...])
    assert is_instance((), tuple[()])
    assert is_instance((), tuple[int, ...])
    assert not is_instance((10, "a"), tuple[int, ...])

    # tuple of dataclasses
    assert is_instance(
        (Int(10), Str("foo"), Float(100.0), Bool(True)), tuple[Int, Str, Float, Bool]
    )
    assert not is_instance(
        (Int(10), Str("foo"), Str("wrong-class"), Bool(True)), tuple[Int, Str, Float, Bool]
    )

    # dict
    assert is_instance({}, dict[str, int])
    assert is_instance({"a": "b"}, dict)
    assert is_instance({"a": "b"}, dict)
    assert is_instance({"foo": 10, "bar": 20}, dict[str, int])
    assert not is_instance({"foo": 10.0, "bar": 20}, dict[str, int])

    # dict of dataclass
    assert is_instance({Str("foo"): Int(10), Str("bar"): Int(20)}, dict[Str, Int])
    assert not is_instance({Str("foo"): Str("wrong-type"), Str("bar"): Int(10)}, dict[Str, Int])

    # optional
    assert is_instance(None, type(None))
    assert is_instance(10, Optional[int])
    assert is_instance(None, Optional[int])
    assert not is_instance("wrong-type", Optional[int])

    # optional of dataclass
    assert is_instance(Int(10), Optional[Int])
    assert not is_instance("wrong-type", Optional[Int])

    # nested containers
    assert is_instance([({"a": "b"}, 10, [True])], list[tuple[dict[str, str], int, list[bool]]])
    assert not is_instance(
        [({"a": "b"}, 10, ["wrong-type"])], list[tuple[dict[str, str], int, list[bool]]]
    )


@serde
class GenericFoo(Generic[T]):
    t: T


def test_is_generic() -> None:
    assert not is_generic(int)
    assert not is_generic(list[int])
    assert not is_generic(list)
    assert not is_generic(GenericFoo)
    assert is_generic(GenericFoo[int])
    assert is_generic(GenericFoo[list[int]])
    assert not is_generic(Optional[int])
    assert not is_generic(Optional[list[int]])
    assert is_serializable(GenericFoo)
    assert not is_serializable(GenericFoo[list[int]])
    assert is_deserializable(GenericFoo)
    assert not is_deserializable(GenericFoo[list[int]])


def test_get_generic_arg() -> None:
    class GenericFoo(Generic[T, U]):
        pass

    assert get_generic_arg(GenericFoo[int, str], ["T", "U"], ["T", "U"], 0) is int
    assert get_generic_arg(GenericFoo[int, str], ["T", "U"], ["T", "U"], 1) is str
    assert get_generic_arg(GenericFoo[int, str], ["T", "U"], ["U"], 0) is str
    assert get_generic_arg(GenericFoo[int, str], ["T", "U"], ["V"], 0) == Any

    with pytest.raises(SerdeError):
        get_generic_arg(GenericFoo[int, str], ["T"], ["T"], 0)

    with pytest.raises(SerdeError):
        get_generic_arg(GenericFoo[int, str], ["T"], ["U"], 0)
