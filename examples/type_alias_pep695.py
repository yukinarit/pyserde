from serde import serde
from serde.json import from_json, to_json


@serde
class Bar:
    a: int


@serde
class Baz:
    b: int


# BarBaz = Bar | Baz
type BarBaz = Bar | Baz


@serde
class Foo:
    barbaz: BarBaz


def main() -> None:
    f = Foo(Baz(10))
    s = to_json(f)
    print(f"Into Json: {s}")
    ff = from_json(Foo, s)
    print(f"From Json: {ff}")


if __name__ == "__main__":
    main()
