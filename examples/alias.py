from serde import field, serde
from serde.json import from_json


@serde
class Foo:
    a: int = field(alias=["b", "c", "d"])


def main() -> None:
    s = '{"a": 10}'
    print(f"From Json: {from_json(Foo, s)}")

    s = '{"b": 20}'
    print(f"From Json: {from_json(Foo, s)}")

    s = '{"c": 30}'
    print(f"From Json: {from_json(Foo, s)}")

    s = '{"d": 40}'
    print(f"From Json: {from_json(Foo, s)}")

    try:
        s = '{"e": 50}'
        print(f"From Json: {from_json(Foo, s)}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
