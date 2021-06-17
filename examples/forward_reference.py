from dataclasses import dataclass

from serde import deserialize, serialize
from serde.json import from_json, to_json


@dataclass
class Foo:
    i: int
    s: str
    bar: 'Bar'  # Specify type annotation in string.


@deserialize
@serialize
@dataclass
class Bar:
    f: float
    b: bool


# Evaluate pyserde decorators after `Bar` is defined.
deserialize(Foo)
serialize(Foo)


def main():
    f = Foo(i=10, s='foo', bar=Bar(f=100.0, b=True))
    print(f"Into Json: {to_json(f)}")

    s = '{"i": 10, "s": "foo", "bar": {"f": 100.0, "b": true}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
