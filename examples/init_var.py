from dataclasses import InitVar, dataclass
from typing import Optional

from serde import serde
from serde.json import from_json, to_json


@serde
@dataclass
class Foo:
    i: int
    j: Optional[int] = None
    k: InitVar[Optional[int]] = None


def main():
    f = Foo(i=10, j=20)
    print(f"Into Json: {to_json(f)}")

    s = '{"i": 10, "j": 20}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
