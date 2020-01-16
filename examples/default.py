from dataclasses import dataclass, field
from serde import deserialize, serialize
from serde.json import from_json, to_json


@deserialize
@serialize
@dataclass
class Foo:
    i: int = 10
    s: str = 'foo'
    f: float = field(default=100.0)  # Use dataclass field.
    b: bool = field(default=True)


def main():
    h = Foo()
    print(f"Into Json: {to_json(h)}")

    s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
