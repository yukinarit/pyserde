from serde import serde
from serde.json import from_json, to_json


@serde
class Bar:
    b: int


@serde
class Foo:
    a: Bar


def main() -> None:
    f = Foo(Bar(10))
    print(f"Into Json: {to_json(f)}")

    s = '{"a": {"b": 10}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
