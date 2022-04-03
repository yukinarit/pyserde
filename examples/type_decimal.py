from dataclasses import dataclass
from decimal import Decimal

from serde import serde
from serde.json import from_json, to_json


@serde
@dataclass
class Foo:
    v: Decimal


def main():
    foo = Foo(Decimal(0.1))
    print(f"Into Json: {to_json(foo)}")

    s = '{"v": "0.1000000000000000055511151231257827021181583404541015625"}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
