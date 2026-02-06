from typing import Generic, TypeVar

from serde import from_dict, serde, to_dict

T = TypeVar("T")


@serde
class Bar:
    n: int


@serde
class Foo(Generic[T]):
    inner: T


@serde
class Baz(Generic[T]):
    foo: Foo[T]


def main() -> None:
    # Use dataclass as type parameter
    foobar = Foo[Bar](Bar(10))
    d = to_dict(foobar)
    print(from_dict(Foo[Bar], d))

    # Use primitive as type parameter
    fooint = Foo[int](10)
    d = to_dict(fooint)
    print(from_dict(Foo[int], d))

    # No type parameter. Any is deduced.
    foobar = Foo(Bar(10))
    d = to_dict(foobar)
    print(from_dict(Foo, d))

    # Nested
    bazint = Baz[int](Foo[int](10))
    d = to_dict(bazint)
    print(from_dict(Baz[int], d))


if __name__ == "__main__":
    main()
