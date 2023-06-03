# mypy: ignore-errors
from serde import serde
from serde.json import from_json, to_json


# Thanks to PEP681 @dataclass_transform, @dataclass decorator is no longer mandatory
# if you use PEP681 supported type check such as pyright. If you are a mypy user,
# you still need @dataclass decorator.
@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool


def main() -> None:
    f = Foo(10, "foo", 100.0, True)
    print(f"Into Json: {to_json(f)}")

    s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
