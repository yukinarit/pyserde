from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    a: list[str]
    b: tuple[str, bool]
    c: dict[str, list[int]]


def main() -> None:
    h = Foo(["1", "2"], ("foo", True), {"bar": [10, 20]})
    print(f"Into Json: {to_json(h)}")

    s = '{"a": ["1", "2"], "b": ["foo", true], "c": {"bar": [10, 20]}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
