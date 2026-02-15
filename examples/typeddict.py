"""
TypedDict example

TypedDict allows defining dict types with specific named keys and per-key types.
This is useful for JSON API responses where you want type safety without
full dataclass overhead.
"""

from typing import NotRequired, TypedDict

from serde import serde
from serde.json import from_json, to_json


# TypedDict with all required fields
class Movie(TypedDict):
    title: str
    year: int
    director: str


# TypedDict with optional fields
class Person(TypedDict):
    name: str
    age: int
    email: NotRequired[str]  # Optional field


# Nested TypedDict
class Library(TypedDict):
    name: str
    movies: list[Movie]


# Using TypedDict as a field in a serde dataclass
@serde
class Cinema:
    location: str
    featured: Movie


def main() -> None:
    # Create a Movie TypedDict
    movie: Movie = {"title": "Inception", "year": 2010, "director": "Christopher Nolan"}
    print(f"Movie: {movie}")

    # Create a Cinema with a Movie field
    cinema = Cinema(location="Downtown", featured=movie)
    print(f"Cinema: {cinema}")

    # Serialize to JSON
    json_str = to_json(cinema)
    print(f"To JSON: {json_str}")

    # Deserialize from JSON
    restored = from_json(Cinema, json_str)
    print(f"From JSON: {restored}")

    # Verify the nested TypedDict
    print(f"Featured movie title: {restored.featured['title']}")

    # Test with optional fields
    person: Person = {"name": "Alice", "age": 30}  # email is optional
    print(f"Person without email: {person}")

    person_with_email: Person = {"name": "Bob", "age": 25, "email": "bob@example.com"}
    print(f"Person with email: {person_with_email}")


if __name__ == "__main__":
    main()
