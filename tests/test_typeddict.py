"""
Tests for TypedDict support in pyserde.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

import pytest

from serde import serde
from serde.core import is_instance
from serde.compat import SerdeError
from serde.de import from_dict
from serde.json import from_json, to_json
from serde.se import to_dict

# --- TypedDict type definitions ---


class Movie(TypedDict):
    title: str
    year: int
    director: str


class PersonOptEmail(TypedDict):
    name: str
    age: int
    email: NotRequired[str]


class PersonTotalFalse(TypedDict, total=False):
    name: str
    age: int


class Library(TypedDict):
    name: str
    movies: list[Movie]


class NestedTypedDict(TypedDict):
    library: Library
    active: bool


# --- Dataclasses with TypedDict fields ---


@serde
class Cinema:
    location: str
    featured: Movie


@serde
class CinemaOptPerson:
    name: str
    contact: PersonOptEmail


@serde
class CinemaTotalFalse:
    name: str
    staff: PersonTotalFalse


@serde
class CinemaLibrary:
    region: str
    library: Library


@serde
class CinemaDeep:
    city: str
    data: NestedTypedDict


# --- Tests: TypedDict as field in serde dataclass ---


def test_typeddict_field_to_dict():
    movie: Movie = {"title": "Inception", "year": 2010, "director": "Christopher Nolan"}
    cinema = Cinema(location="Downtown", featured=movie)
    d = to_dict(cinema)
    assert d == {
        "location": "Downtown",
        "featured": {"title": "Inception", "year": 2010, "director": "Christopher Nolan"},
    }


def test_typeddict_field_from_dict():
    d = {
        "location": "Downtown",
        "featured": {"title": "Inception", "year": 2010, "director": "Christopher Nolan"},
    }
    cinema = from_dict(Cinema, d)
    assert cinema.location == "Downtown"
    assert cinema.featured["title"] == "Inception"
    assert cinema.featured["year"] == 2010


def test_typeddict_field_json_roundtrip():
    movie: Movie = {"title": "Inception", "year": 2010, "director": "Christopher Nolan"}
    cinema = Cinema(location="Downtown", featured=movie)
    json_str = to_json(cinema)
    restored = from_json(Cinema, json_str)
    assert restored == cinema


# --- Tests: NotRequired fields ---


def test_notrequired_present():
    person: PersonOptEmail = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    c = CinemaOptPerson(name="Grand", contact=person)
    d = to_dict(c)
    assert d["contact"]["email"] == "alice@example.com"
    restored = from_dict(CinemaOptPerson, d)
    assert restored.contact.get("email") == "alice@example.com"


def test_notrequired_absent():
    person: PersonOptEmail = {"name": "Alice", "age": 30}
    c = CinemaOptPerson(name="Grand", contact=person)
    d = to_dict(c)
    assert "email" not in d["contact"]
    restored = from_dict(CinemaOptPerson, d)
    assert "email" not in restored.contact


def test_notrequired_json_roundtrip_present():
    person: PersonOptEmail = {"name": "Bob", "age": 25, "email": "bob@example.com"}
    c = CinemaOptPerson(name="Ritz", contact=person)
    json_str = to_json(c)
    restored = from_json(CinemaOptPerson, json_str)
    assert restored == c


def test_notrequired_json_roundtrip_absent():
    person: PersonOptEmail = {"name": "Bob", "age": 25}
    c = CinemaOptPerson(name="Ritz", contact=person)
    json_str = to_json(c)
    restored = from_json(CinemaOptPerson, json_str)
    assert restored == c


# --- Tests: total=False TypedDict ---


def test_total_false_all_fields():
    staff: PersonTotalFalse = {"name": "Alice", "age": 30}
    c = CinemaTotalFalse(name="Grand", staff=staff)
    d = to_dict(c)
    assert d["staff"] == {"name": "Alice", "age": 30}
    restored = from_dict(CinemaTotalFalse, d)
    assert restored.staff == {"name": "Alice", "age": 30}


def test_total_false_partial_fields():
    staff: PersonTotalFalse = {"name": "Alice"}
    c = CinemaTotalFalse(name="Grand", staff=staff)
    d = to_dict(c)
    assert "age" not in d["staff"]
    restored = from_dict(CinemaTotalFalse, d)
    assert "age" not in restored.staff


def test_total_false_empty():
    staff: PersonTotalFalse = {}
    c = CinemaTotalFalse(name="Grand", staff=staff)
    d = to_dict(c)
    assert d["staff"] == {}
    restored = from_dict(CinemaTotalFalse, d)
    assert restored.staff == {}


# --- Tests: Nested TypedDict ---


def test_nested_typeddict():
    library: Library = {
        "name": "City Library",
        "movies": [
            {"title": "Inception", "year": 2010, "director": "Nolan"},
            {"title": "Interstellar", "year": 2014, "director": "Nolan"},
        ],
    }
    c = CinemaLibrary(region="North", library=library)
    d = to_dict(c)
    assert d["library"]["name"] == "City Library"
    assert len(d["library"]["movies"]) == 2
    restored = from_dict(CinemaLibrary, d)
    assert restored.library["movies"][0]["title"] == "Inception"


def test_deeply_nested_typeddict():
    data: NestedTypedDict = {
        "library": {
            "name": "City Library",
            "movies": [{"title": "Inception", "year": 2010, "director": "Nolan"}],
        },
        "active": True,
    }
    c = CinemaDeep(city="NYC", data=data)
    d = to_dict(c)
    assert d["data"]["library"]["movies"][0]["title"] == "Inception"
    restored = from_dict(CinemaDeep, d)
    assert restored.data["library"]["movies"][0]["title"] == "Inception"
    assert restored.data["active"] is True


# --- Tests: Direct TypedDict serialization ---


def test_direct_from_dict_required():
    d = {"title": "Inception", "year": 2010, "director": "Nolan"}
    movie = from_dict(Movie, d)
    assert movie == d


def test_direct_from_dict_notrequired_present():
    d = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    person = from_dict(PersonOptEmail, d)
    assert person.get("email") == "alice@example.com"


def test_direct_from_dict_notrequired_absent():
    d = {"name": "Alice", "age": 30}
    person = from_dict(PersonOptEmail, d)
    assert "email" not in person


def test_direct_from_dict_missing_required_raises():
    d = {"title": "Inception", "year": 2010}  # missing 'director'
    with pytest.raises(SerdeError):
        from_dict(Movie, d)


# --- Tests: is_instance with TypedDict ---


def test_is_instance_valid():
    movie: Movie = {"title": "Inception", "year": 2010, "director": "Nolan"}
    assert is_instance(movie, Movie)


def test_is_instance_missing_required_key():
    d = {"title": "Inception", "year": 2010}  # missing 'director'
    assert not is_instance(d, Movie)


def test_is_instance_wrong_type():
    assert not is_instance("not a dict", Movie)


def test_is_instance_notrequired_absent():
    person = {"name": "Alice", "age": 30}
    assert is_instance(person, PersonOptEmail)


def test_is_instance_notrequired_present():
    person = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    assert is_instance(person, PersonOptEmail)
