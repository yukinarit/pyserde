from dataclasses import dataclass
from typing import Generic, TypeVar

from serde import from_dict, serde, to_dict

T = TypeVar('T')


@serde
@dataclass
class Bar:
    n: int


@serde
@dataclass
class Foo(Generic[T]):
    inner: T


@serde
@dataclass
class Baz(Generic[T]):
    foo: Foo[T]


def main():
    # Use dataclass as type parameter
    f = Foo[Bar](Bar(10))
    d = to_dict(f)
    print(from_dict(Foo[Bar], d))

    # Use primitive as type parameter
    f = Foo[int](10)
    d = to_dict(f)
    print(from_dict(Foo[int], d))

    # No type parameter. Any is deduced.
    f = Foo(Bar(10))
    d = to_dict(f)
    print(from_dict(Foo, d))

    # Nested
    b = Baz[int](Foo[int](10))
    d = to_dict(b)
    print(from_dict(Baz[int], d))


if __name__ == "__main__":
    main()
