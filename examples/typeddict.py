"""
typeddict.py

Example usage of TypedDict, including PEP 655, PEP 705 and PEP 728.
"""

from typing import NotRequired, TypedDict

import typing_extensions as te

from serde import from_dict, serde, to_dict
from serde.json import from_json, to_json


class Movie(TypedDict):
    title: str
    year: int


class Person(TypedDict):
    name: str
    # PEP 655: this key may be omitted.
    email: NotRequired[str]
    # PEP 705: read-only for a type checker, no effect on the wire format.
    # Spelled via typing_extensions, since typing.ReadOnly is Python 3.13+.
    id: te.ReadOnly[int]


class Config(te.TypedDict, extra_items=int):
    """PEP 728: undeclared keys are allowed here, and must be ints."""

    name: str


@serde
class Cinema:
    location: str
    featured: Movie


def main() -> None:
    cinema = Cinema(location="Downtown", featured={"title": "Inception", "year": 2010})
    print(f"Into Json: {to_json(cinema)}")
    # -> {"location":"Downtown","featured":{"title":"Inception","year":2010}}

    print(f"From Json: {from_json(Cinema, to_json(cinema))}")
    # -> Cinema(location='Downtown', featured={'title': 'Inception', 'year': 2010})

    # A TypedDict can also be (de)serialized on its own. Serialization needs the type
    # passed as `c`, because a TypedDict value is just a dict at runtime.
    print(f"Bare from_dict: {from_dict(Movie, {'title': 'Arrival', 'year': 2016})}")
    # -> {'title': 'Arrival', 'year': 2016}
    print(f"Bare to_dict: {to_dict({'title': 'Arrival', 'year': 2016}, c=Movie)}")
    # -> {'title': 'Arrival', 'year': 2016}

    # A NotRequired key that is absent stays absent; it does not become None.
    print(f"Without email: {to_dict({'name': 'Alice', 'id': 1}, c=Person)}")
    # -> {'name': 'Alice', 'id': 1}
    print(f"With email: {to_dict({'name': 'Bob', 'id': 2, 'email': 'b@example.com'}, c=Person)}")
    # -> {'name': 'Bob', 'email': 'b@example.com', 'id': 2}  (declaration order)

    # extra_items=int carries undeclared keys through, deserialized as int.
    print(f"Extra items: {from_dict(Config, {'name': 'app', 'retries': 3})}")
    # -> {'name': 'app', 'retries': 3}

    # Undeclared keys are rejected unless the TypedDict opts in, as Movie does not.
    try:
        from_dict(Movie, {"title": "Arrival", "year": 2016, "director": "Villeneuve"})
    except Exception as e:
        print(f"Unknown key: {e}")
    # -> unknown fields: ['director'], expected one of ['title', 'year'] ...


if __name__ == "__main__":
    main()
