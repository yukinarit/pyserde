from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    i: frozenset[int]


def main() -> None:
    f = Foo(i=frozenset({1, 2}))
    print(f"Into Json: {to_json(f)}")

    s = '{"i": [1, 2]}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
