from dataclasses import dataclass
from typing import FrozenSet

from serde import serde
from serde.json import from_json, to_json


@serde
@dataclass
class Foo:
    i: FrozenSet[int]


def main():
    f = Foo(i={1, 2})
    print(f"Into Json: {to_json(f)}")

    s = '{"i": [1, 2]}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
