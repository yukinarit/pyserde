from typing import ClassVar

from serde import serde
from serde.json import from_json, to_json


@serde
class Bar:
    v: int


@serde(serialize_class_var=True)
class Foo:
    a: ClassVar[int] = 10
    b: ClassVar[Bar] = Bar(100)
    c: ClassVar[list[Bar]] = [Bar(1), Bar(2)]


def main() -> None:
    f = Foo()
    print(f"Into Json: {to_json(f)}")
    print(f"From Json: {from_json(Foo, '{}')}")


if __name__ == "__main__":
    main()
