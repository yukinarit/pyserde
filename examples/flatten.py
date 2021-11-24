from dataclasses import field

from serde import serde
from serde.json import from_json, to_json


@serde
class Bar:
    c: float
    d: bool


@serde
class Foo:
    a: int
    b: str
    bar: Bar = field(metadata={'serde_flatten': True})


def main():
    f = Foo(a=10, b='foo', bar=Bar(c=100.0, d=True))
    print(f"Into Json: {to_json(f)}")

    s = '{"a": 10, "b": "foo", "c": 100.0, "d": true}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
