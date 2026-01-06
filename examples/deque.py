from collections import deque

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    items: deque[int]


def main() -> None:
    f = Foo(items=deque([1, 2, 3]))
    print(f"Into Json: {to_json(f)}")

    s = '{"items": [1, 2, 3]}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
