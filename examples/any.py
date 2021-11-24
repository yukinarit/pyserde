from typing import Any

from serde import serde
from serde.json import from_json, to_json


@serde
class Bar:
    v: float


@serde
class Foo:
    a: Any
    b: Any
    c: Any
    d: Any


def main():
    # Bar is serialized into dict.
    f = Foo(a=10, b=[1, 2], c={'foo': 'bar'}, d=Bar(100.0))
    print(f"Into Json: {to_json(f)}")

    # However, pyserde can't deserialize the dict into Bar.
    # This is because there is no "Bar" annotation in "Foo" class.
    s = '{"a": 10, "b": [1, 2], "c": {"foo": "bar"}, "d": {"v": 100.0}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
