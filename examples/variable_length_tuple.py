from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    v: tuple[int, ...]


def main() -> None:
    f = Foo(v=(1, 2, 3))
    print(f"Into Json: {to_json(f)}")

    s = '{"v": [1, 2, 3]}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
