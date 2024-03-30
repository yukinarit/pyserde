from serde import disabled, serde
from serde.json import from_json, to_json


@serde(type_check=disabled)
class Foo:
    a: int
    b: list[int]
    c: list[dict[str, int]]


def main() -> None:
    # Foo is instantiated with wrong types but serde won't complain
    f = Foo(a=1.0, b=[1.0], c=[{"k": 1.0}])  # type: ignore
    print(f"Into Json: {to_json(f)}")

    # Also, JSON contains wrong types of values but serde won't complain
    s = '{"a": 1, "b": [1], "c": [{"k": 1.0}]}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
