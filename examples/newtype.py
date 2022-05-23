from dataclasses import dataclass
from typing import NewType

from serde import serde
from serde.json import from_json, to_json

UserId = NewType("UserId", int)


@serde
@dataclass
class Foo:
    id: UserId


def main():
    f = Foo(id=UserId(10))
    print(f"Into Json: {to_json(f)}")

    s = '{"id": 10}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
