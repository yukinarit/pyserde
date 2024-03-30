import enum

import imported

from serde import serde
from serde.json import from_json, to_json


class Nested(enum.Enum):
    S = "foo"


class E(enum.Enum):
    S = "foo"
    F = 10.0
    B = True
    N = Nested.S


class IE(enum.IntEnum):
    V0 = enum.auto()
    V1 = enum.auto()
    V2 = enum.auto()


@serde
class Foo:
    v0: IE
    v1: IE = IE.V1  # Default enum value.
    v2: E = E.S
    v3: imported.ImportedEnum = imported.ImportedEnum.V3  # Use enum imported from other module.
    v4: E = E.N  # Use nested enum.


def main() -> None:
    f = Foo(IE.V0)
    s = to_json(f)
    print(s)

    f = from_json(Foo, s)
    print(f)
    s = to_json(f)

    s = to_json(Foo(IE(3)))
    print(s)


if __name__ == "__main__":
    main()
