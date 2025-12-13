from collections.abc import Sequence

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    xs: Sequence[int]


def main() -> None:
    # Any non-string Sequence works (e.g. tuple, list).
    foo = Foo(xs=(1, 2, 3))
    print(f"Into Json: {to_json(foo)}")  # -> {"xs":[1,2,3]}

    s = '{"xs":[1,2,3]}'
    print(f"From Json: {from_json(Foo, s)}")  # -> Foo(xs=[1, 2, 3])


if __name__ == "__main__":
    main()
