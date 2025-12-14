from collections.abc import MutableSet, Set

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    s: Set[int]
    ms: MutableSet[int]


def main() -> None:
    f = Foo(s=frozenset({1, 2}), ms=set({3, 4}))
    print(f"Into Json: {to_json(f)}")

    s = '{"s":[1,2],"ms":[3,4]}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
