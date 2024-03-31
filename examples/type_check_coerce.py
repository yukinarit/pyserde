from serde import coerce, serde
from serde.json import from_json, to_json


@serde(type_check=coerce)
class Bar:
    e: int


@serde(type_check=coerce)
class Foo:
    a: int
    b: list[int]
    c: list[dict[str, int]]
    d: Bar | None = None


def main() -> None:
    f = Foo(a="1", b=[True], c=[{10: 1.0}])  # type: ignore
    print(f"Into Json: {to_json(f)}")

    s = '{"a": "1", "b": [false], "c": [{"10": 1.0}], "d": {"e": "100"}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
