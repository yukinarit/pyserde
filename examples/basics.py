from dataclasses import dataclass
from serde import deserialize, serialize
from serde.json import from_json, to_json

# Mark the class serializable/deserializable.
@deserialize
@serialize
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool


def main():
    h = Foo(i=10, s='foo', f=100.0, b=True)
    print(f"Into Json: {to_json(h)}")

    s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
