import enum
from dataclasses import dataclass
from serde import serialize, deserialize
from serde.json import to_json, from_json

import imported


class Nested(enum.Enum):
    S = 'foo'


class E(enum.Enum):
    S = 'foo'
    F = 10.0
    B = True
    N = Nested.S


class IE(enum.IntEnum):
    V0 = enum.auto()
    V1 = enum.auto()
    V2 = enum.auto()


@deserialize
@serialize
@dataclass
class Foo:
    v0: IE
    v1: IE = IE.V1  # Default enum value.
    v2: E = E.S
    v3: imported.ImportedEnum = imported.ImportedEnum.V3  # Use enum imported from other module.
    # v3: E = E.N  # Sorry nested is not yet supported.


if __name__ == "__main__":
    f = Foo(IE.V0)
    s = to_json(f)
    print(s)

    f = from_json(Foo, s)
    print(f)
    s = to_json(f)

    # Non Enum values cause type mismatch error.
    # s = to_json(Foo(0))
