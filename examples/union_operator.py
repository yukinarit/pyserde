# mypy: ignore-errors

from serde import serde
from serde.json import from_json, to_json


@serde
class Bar:
    v: int


@serde
class Baz:
    v: float


@serde
class Foo:
    a: int | str  # type: ignore
    b: dict[str, int] | list[int]  # type: ignore
    c: Bar | Baz  # type: ignore
    d: str | None = None  # type: ignore
    # Should be treated as Optional


def main() -> None:
    f = Foo(10, [1, 2, 3], Bar(10))
    print(f"Into Json: {to_json(f)}")

    s = '{"a": 10, "b": [1, 2, 3], "c": {"Bar": {"v": 10}}}'
    print(f"From Json: {from_json(Foo, s)}")

    f = Foo("foo", {"bar": 1, "baz": 2}, Baz(100.0))
    print(f"Into Json: {to_json(f)}")

    s = '{"a": "foo", "b": {"bar": 1, "baz": 2}, "c": {"Baz": {"v": 100.0}}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
