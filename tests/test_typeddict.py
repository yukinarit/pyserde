"""
Tests for TypedDict support, covering PEP 655, PEP 705 and PEP 728.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal, NotRequired, Optional, TypedDict, Union

import pytest
import typing_extensions as te

from serde import field, from_dict, from_tuple, serde, to_dict, to_tuple
from serde.compat import (
    SerdeError,
    is_typeddict,
    typeddict_extra_items,
    typeddict_items,
)
from serde.core import is_instance
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack


class Movie(TypedDict):
    title: str
    year: int


class Person(TypedDict):
    name: str
    email: NotRequired[str]


class Node(TypedDict):
    """Recursive: a forward reference must resolve at module scope."""

    name: str
    children: list["Node"]


@serde
class Cinema:
    location: str
    featured: Movie


# --- Basics -------------------------------------------------------------------------


def test_field_roundtrip() -> None:
    cinema = Cinema(location="Downtown", featured={"title": "Inception", "year": 2010})
    assert to_dict(cinema) == {
        "location": "Downtown",
        "featured": {"title": "Inception", "year": 2010},
    }
    assert from_dict(Cinema, to_dict(cinema)) == cinema

    assert to_json(cinema) == '{"location":"Downtown","featured":{"title":"Inception","year":2010}}'
    assert from_json(Cinema, to_json(cinema)) == cinema


def test_missing_required_key() -> None:
    with pytest.raises(SerdeError) as exc_info:
        from_dict(Cinema, {"location": "Downtown", "featured": {"title": "Inception"}})
    # The error names the TypedDict and the key, not pyserde's internals.
    assert "missing required fields: ['year']" in str(exc_info.value)
    assert "Movie" in str(exc_info.value)


def test_wrong_value_type() -> None:
    """
    beartype reduces a TypedDict to Mapping[str, object], so pyserde has to check values
    itself. Without that, this payload would be accepted silently.
    """
    with pytest.raises(SerdeError):
        from_dict(Cinema, {"location": "Downtown", "featured": {"title": "x", "year": "nope"}})


def test_unknown_key_rejected() -> None:
    """A TypedDict declares the full set of its keys (PEP 589)."""
    with pytest.raises(SerdeError) as exc_info:
        from_dict(Cinema, {"location": "D", "featured": {"title": "x", "year": 1, "zzz": 9}})
    assert "unknown fields: ['zzz']" in str(exc_info.value)


def test_bare_typeddict() -> None:
    """A TypedDict can be a target in its own right, not only a field type."""
    assert from_dict(Movie, {"title": "Inception", "year": 2010}) == {
        "title": "Inception",
        "year": 2010,
    }
    assert to_dict({"title": "Inception", "year": 2010}, c=Movie) == {
        "title": "Inception",
        "year": 2010,
    }
    assert from_json(Movie, '{"title":"Inception","year":2010}') == {
        "title": "Inception",
        "year": 2010,
    }

    with pytest.raises(SerdeError):
        from_dict(Movie, {"title": "Inception"})
    with pytest.raises(SerdeError):
        from_dict(Movie, {"title": "Inception", "year": "nope"})


def test_typing_extensions_typeddict() -> None:
    """PEP 728 forces users onto typing_extensions.TypedDict, so it must work too."""

    class TeMovie(te.TypedDict):
        title: str
        year: int

    @serde
    class Foo:
        v: TeMovie

    foo = Foo(v={"title": "t", "year": 1})
    assert to_dict(foo) == {"v": {"title": "t", "year": 1}}
    assert from_dict(Foo, to_dict(foo)) == foo


# --- PEP 655: Required / NotRequired / total ------------------------------------------


@serde
class Contact:
    person: Person


def test_notrequired_present() -> None:
    contact = Contact(person={"name": "Alice", "email": "alice@example.com"})
    assert to_dict(contact) == {"person": {"name": "Alice", "email": "alice@example.com"}}
    assert from_dict(Contact, to_dict(contact)) == contact


def test_notrequired_absent_stays_absent() -> None:
    """An absent optional key must not materialize as None."""
    contact = Contact(person={"name": "Alice"})
    assert to_dict(contact) == {"person": {"name": "Alice"}}

    restored = from_dict(Contact, {"person": {"name": "Alice"}})
    assert "email" not in restored.person
    assert restored == contact


def test_total_false() -> None:
    class Partial(TypedDict, total=False):
        name: str
        age: int

    @serde
    class Foo:
        v: Partial

    for payload in ({"name": "a", "age": 1}, {"name": "a"}, {}):
        foo = Foo(v=payload)  # type: ignore[typeddict-item]
        assert to_dict(foo) == {"v": payload}
        assert from_dict(Foo, {"v": payload}) == foo


def test_required_within_total_false() -> None:
    class Mixed(TypedDict, total=False):
        name: te.Required[str]
        age: int

    assert typeddict_items(Mixed)["name"].required is True
    assert typeddict_items(Mixed)["age"].required is False

    @serde
    class Foo:
        v: Mixed

    assert from_dict(Foo, {"v": {"name": "a"}}) == Foo(v={"name": "a"})
    with pytest.raises(SerdeError):
        from_dict(Foo, {"v": {"age": 1}})


def test_inheritance_across_total() -> None:
    class Base(TypedDict):
        a: int

    class Child(Base, total=False):
        b: str

    assert typeddict_items(Child)["a"].required is True
    assert typeddict_items(Child)["b"].required is False

    @serde
    class Foo:
        v: Child

    assert from_dict(Foo, {"v": {"a": 1}}) == Foo(v={"a": 1})
    assert from_dict(Foo, {"v": {"a": 1, "b": "x"}}) == Foo(v={"a": 1, "b": "x"})


# --- PEP 705: ReadOnly ----------------------------------------------------------------


def test_readonly_both_nesting_orders() -> None:
    class Config(TypedDict):
        a: te.ReadOnly[int]
        b: te.ReadOnly[NotRequired[str]]
        c: NotRequired[te.ReadOnly[str]]

    items = typeddict_items(Config)
    # The qualifier is stripped regardless of nesting order, and requiredness survives it.
    assert items["a"] == type(items["a"])(type=int, required=True, readonly=True)
    assert items["b"] == type(items["b"])(type=str, required=False, readonly=True)
    assert items["c"] == type(items["c"])(type=str, required=False, readonly=True)

    @serde
    class Foo:
        v: Config

    # ReadOnly is a type-checker concept only: it must not change the wire format.
    foo = Foo(v={"a": 1, "c": "z"})
    assert to_dict(foo) == {"v": {"a": 1, "c": "z"}}
    assert from_dict(Foo, {"v": {"a": 1, "c": "z"}}) == foo


def test_readonly_total_false() -> None:
    class Config(TypedDict, total=False):
        debug: te.ReadOnly[bool]

    assert typeddict_items(Config)["debug"].required is False
    assert typeddict_items(Config)["debug"].readonly is True


# --- PEP 728: closed / extra_items ----------------------------------------------------


def test_closed_true() -> None:
    class Closed(te.TypedDict, closed=True):
        a: int

    assert typeddict_extra_items(Closed) is None

    @serde
    class Foo:
        v: Closed

    assert from_dict(Foo, {"v": {"a": 1}}) == Foo(v={"a": 1})

    # Strict in: an undeclared key on the wire is an error.
    with pytest.raises(SerdeError):
        from_dict(Foo, {"v": {"a": 1, "b": 2}})

    # Lenient out: a stray runtime key is simply dropped.
    assert to_dict(Foo(v={"a": 1, "b": 2})) == {"v": {"a": 1}}  # type: ignore[typeddict-unknown-key]


def test_extra_items_typed() -> None:
    class Extra(te.TypedDict, extra_items=int):
        a: str

    assert typeddict_extra_items(Extra) is int

    @serde
    class Foo:
        v: Extra

    foo = Foo(v={"a": "x", "n": 5})  # type: ignore[typeddict-unknown-key]
    assert to_dict(foo) == {"v": {"a": "x", "n": 5}}
    assert from_dict(Foo, {"v": {"a": "x", "n": 5}}) == foo

    # Extra items are typed, so a bad extra value is still an error.
    with pytest.raises(SerdeError):
        from_dict(Foo, {"v": {"a": "x", "n": "notanint"}})


def test_extra_items_never_is_closed() -> None:
    class Extra(te.TypedDict, extra_items=te.Never):
        a: int

    assert typeddict_extra_items(Extra) is None

    @serde
    class Foo:
        v: Extra

    with pytest.raises(SerdeError):
        from_dict(Foo, {"v": {"a": 1, "b": 2}})


def test_closed_false_passes_extras_through() -> None:
    class Open(te.TypedDict, closed=False):
        a: int

    @serde
    class Foo:
        v: Open

    payload = {"a": 1, "junk": [1, 2]}
    assert from_dict(Foo, {"v": payload}) == Foo(v=payload)  # type: ignore[typeddict-unknown-key]
    assert to_dict(Foo(v=payload)) == {"v": payload}  # type: ignore[typeddict-unknown-key]


def test_extra_items_readonly() -> None:
    class Extra(te.TypedDict, extra_items=te.ReadOnly[int]):
        a: str

    assert typeddict_extra_items(Extra) is int


def test_extra_items_is_not_inherited() -> None:
    """
    typing_extensions does not propagate extra_items to subclasses, so a subclass is
    closed again. pyserde reports whatever the runtime says.
    """

    class Base(te.TypedDict, extra_items=int):
        a: str

    class Child(Base):
        b: int

    assert typeddict_extra_items(Base) is int
    assert typeddict_extra_items(Child) is None


# --- Nesting --------------------------------------------------------------------------


def test_nested_typeddict_and_list() -> None:
    class Library(TypedDict):
        name: str
        movies: list[Movie]

    @serde
    class Foo:
        v: Library

    foo = Foo(v={"name": "L", "movies": [{"title": "t", "year": 1}]})
    assert to_dict(foo) == {"v": {"name": "L", "movies": [{"title": "t", "year": 1}]}}
    assert from_dict(Foo, to_dict(foo)) == foo


def test_typeddict_inside_containers() -> None:
    @serde
    class Foo:
        lst: list[Movie]
        dct: dict[str, Movie]

    foo = Foo(lst=[{"title": "t", "year": 1}], dct={"k": {"title": "u", "year": 2}})
    assert to_dict(foo) == {
        "lst": [{"title": "t", "year": 1}],
        "dct": {"k": {"title": "u", "year": 2}},
    }
    assert from_dict(Foo, to_dict(foo)) == foo


def test_dataclass_inside_typeddict() -> None:
    """Proves iter_types recurses into a TypedDict, so the inner dataclass gets a scope."""

    @dataclass
    class Inner:
        x: int

    class Outer(TypedDict):
        inner: Inner

    @serde
    class Foo:
        v: Outer

    assert to_dict(Foo(v={"inner": Inner(1)})) == {"v": {"inner": {"x": 1}}}
    assert from_dict(Foo, {"v": {"inner": {"x": 1}}}) == Foo(v={"inner": Inner(1)})


def test_literal_and_enum_inside_typeddict() -> None:
    """Proves iter_literals recurses into a TypedDict."""

    class Color(Enum):
        RED = "red"

    class Outer(TypedDict):
        lit: Literal["a", "b"]
        color: Color
        when: datetime

    @serde
    class Foo:
        v: Outer

    payload = {"v": {"lit": "a", "color": "red", "when": "2020-01-02T03:04:05"}}
    foo = from_dict(Foo, payload)
    assert foo.v["color"] is Color.RED
    assert foo.v["when"] == datetime(2020, 1, 2, 3, 4, 5)
    assert to_dict(foo, reuse_instances=False) == payload


def test_union_inside_typeddict() -> None:
    """Proves iter_unions recurses into a TypedDict, so the union func gets generated."""

    class Outer(TypedDict):
        u: Union[int, str]

    @serde
    class Foo:
        v: Outer

    assert from_dict(Foo, {"v": {"u": "s"}}) == Foo(v={"u": "s"})
    assert from_dict(Foo, {"v": {"u": 1}}) == Foo(v={"u": 1})
    assert to_dict(Foo(v={"u": "s"})) == {"v": {"u": "s"}}


def test_optional_inside_typeddict() -> None:
    class Outer(TypedDict):
        a: Optional[int]
        b: NotRequired[Optional[str]]

    @serde
    class Foo:
        v: Outer

    assert from_dict(Foo, {"v": {"a": None}}) == Foo(v={"a": None})
    assert from_dict(Foo, {"v": {"a": 1, "b": "x"}}) == Foo(v={"a": 1, "b": "x"})
    assert to_dict(Foo(v={"a": None})) == {"v": {"a": None}}


# --- Union of TypedDicts --------------------------------------------------------------


def test_union_of_typeddicts() -> None:
    """
    Disambiguating two TypedDict arms needs pyserde's own deep check: beartype accepts
    any dict for any TypedDict, so the first arm would always win.
    """

    @serde
    class Foo:
        v: Union[Movie, Person]

    movie = Foo(v={"title": "t", "year": 1})
    person = Foo(v={"name": "n"})

    assert from_dict(Foo, {"v": {"title": "t", "year": 1}}) == movie
    assert from_dict(Foo, {"v": {"name": "n"}}) == person
    assert to_dict(movie) == {"v": {"title": "t", "year": 1}}
    assert to_dict(person) == {"v": {"name": "n"}}


# --- is_instance ----------------------------------------------------------------------


def test_is_instance_accepts_valid() -> None:
    assert is_instance({"title": "t", "year": 1}, Movie)
    assert is_instance({"name": "n"}, Person)
    assert is_instance({"name": "n", "email": "e"}, Person)


@pytest.mark.parametrize(
    "obj",
    [
        pytest.param({"title": "t", "year": "notanint"}, id="wrong-value-type"),
        pytest.param({"title": "t"}, id="missing-required-key"),
        pytest.param({"title": "t", "year": 1, "zzz": 9}, id="extra-unknown-key"),
        pytest.param({"title": "t", "year": 1, 3: 9}, id="non-str-key"),
        pytest.param({}, id="empty-dict"),
        pytest.param({"foo": object()}, id="unrelated-dict"),
        pytest.param("not a dict", id="not-a-dict"),
        pytest.param(123, id="not-a-mapping"),
    ],
)
def test_is_instance_rejects(obj: object) -> None:
    """
    Every one of these is a false positive under beartype's is_bearable, which reduces a
    TypedDict to Mapping[str, object]. This pins that pyserde no longer reaches it.
    """
    assert not is_instance(obj, Movie)


def test_is_instance_nested() -> None:
    class Library(TypedDict):
        movies: list[Movie]

    assert is_instance({"movies": [{"title": "t", "year": 1}]}, Library)
    assert not is_instance({"movies": [{"title": "t", "year": "bad"}]}, Library)


def test_is_instance_extra_items() -> None:
    class Extra(te.TypedDict, extra_items=int):
        a: str

    assert is_instance({"a": "x", "n": 5}, Extra)
    assert not is_instance({"a": "x", "n": "notanint"}, Extra)


# --- Formats --------------------------------------------------------------------------


def test_msgpack_roundtrip() -> None:
    cinema = Cinema(location="Downtown", featured={"title": "Inception", "year": 2010})
    assert from_msgpack(Cinema, to_msgpack(cinema)) == cinema


def test_tuple_format_keeps_typeddict_as_dict() -> None:
    """In iter-based formats a TypedDict stays a dict, as a plain dict field does."""
    cinema = Cinema(location="Downtown", featured={"title": "Inception", "year": 2010})
    assert to_tuple(cinema) == ("Downtown", {"title": "Inception", "year": 2010})
    assert from_tuple(Cinema, to_tuple(cinema)) == cinema

    packed = to_msgpack(cinema, named=False)
    assert from_msgpack(Cinema, packed, named=False) == cinema


# --- Interaction with class attributes ------------------------------------------------


def test_rename_all_does_not_rename_typeddict_keys() -> None:
    """A TypedDict has no decorator of its own, so its keys are the wire contract."""

    class Snake(TypedDict):
        first_name: str

    @serde(rename_all="camelcase")
    class Foo:
        my_field: Snake

    assert to_dict(Foo(my_field={"first_name": "a"})) == {"myField": {"first_name": "a"}}
    assert from_dict(Foo, {"myField": {"first_name": "a"}}) == Foo(my_field={"first_name": "a"})


# --- Unsupported ----------------------------------------------------------------------


def test_serde_decorator_on_typeddict_is_rejected() -> None:
    with pytest.raises(SerdeError) as exc_info:

        @serde
        class Bad(TypedDict):
            a: int

    assert "does not need a pyserde decorator" in str(exc_info.value)


def test_generic_typeddict_is_rejected() -> None:
    T = te.TypeVar("T")

    class Box(TypedDict, te.Generic[T]):
        v: T

    with pytest.raises(SerdeError) as exc_info:
        from_dict(Box[int], {"v": 1})

    assert "Generic TypedDict is not supported yet" in str(exc_info.value)


def test_recursive_typeddict_is_rejected() -> None:
    with pytest.raises(SerdeError) as exc_info:

        @serde
        class Foo:
            v: Node

    assert "Recursive TypedDict is not supported yet" in str(exc_info.value)


def test_flatten_on_typeddict_is_rejected() -> None:
    with pytest.raises(SerdeError) as exc_info:

        @serde
        class Foo:
            v: Movie = field(flatten=True)

    assert "does not support flatten attribute" in str(exc_info.value)


# --- Predicates -----------------------------------------------------------------------


def test_is_typeddict() -> None:
    assert is_typeddict(Movie)
    assert is_typeddict(te.TypedDict("TeMovie", {"title": str}))
    assert not is_typeddict(dict)
    assert not is_typeddict(dict[str, int])
    assert not is_typeddict(Cinema)
