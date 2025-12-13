from __future__ import annotations
from dataclasses import dataclass
import enum
from typing import Any

from serde import field, serde, disabled

from . import imported


@serde
class Inner:
    i: int


@serde
@dataclass(unsafe_hash=True)
class Int:
    """
    Integer.
    """

    i: int

    @staticmethod
    def uncheck_new(value: Any) -> Int:
        """
        Bypass runtime type checker by mutating inner value.
        """
        obj = Int(0)
        obj.i = value
        return obj


@serde(type_check=disabled)
@dataclass(unsafe_hash=True)
class UncheckedInt:
    """
    Integer.
    """

    i: int


@serde
@dataclass(unsafe_hash=True)
class Str:
    """
    String.
    """

    s: str


@serde
@dataclass(unsafe_hash=True)
class Float:
    """
    Float.
    """

    f: float


@serde
@dataclass(unsafe_hash=True)
class Bool:
    """
    Boolean.
    """

    b: bool


@serde
@dataclass(unsafe_hash=True)
class Pri:
    """
    Primitives.
    """

    i: int
    s: str
    f: float
    b: bool


@serde
class PriOpt:
    """
    Optional Primitives.
    """

    i: int | None
    s: str | None
    f: float | None
    b: bool | None


@serde
class PriList:
    """
    List containing primitives.
    """

    i: list[int]
    s: list[str]
    f: list[float]
    b: list[bool]


@serde
class PriDict:
    """
    Dict containing primitives.
    """

    i: dict[str, int]
    s: dict[str, str]
    f: dict[str, float]
    b: dict[str, bool]


@serde
class PriTuple:
    """
    Tuple containing primitives.
    """

    i: tuple[int, int, int]
    s: tuple[str, str, str, str]
    f: tuple[float, float, float, float, float]
    b: tuple[bool, bool, bool, bool, bool, bool]


@dataclass(unsafe_hash=True)
class NestedInt:
    """
    Nested integer.
    """

    i: Int


@serde
@dataclass(unsafe_hash=True)
class NestedPri:
    """
    Nested primitives.
    """

    i: Int
    s: Str
    f: Float
    b: Bool


@serde
class NestedPriOpt:
    """
    Optional Primitives.
    """

    i: Int | None
    s: Str | None
    f: Float | None
    b: Bool | None


@serde
class NestedPriList:
    """
    List containing nested primitives.
    """

    i: list[Int]
    s: list[Str]
    f: list[Float]
    b: list[Bool]


@serde
class NestedPriDict:
    """
    Dict containing nested primitives.
    """

    i: dict[Str, Int]
    s: dict[Str, Str]
    f: dict[Str, Float]
    b: dict[Str, Bool]


@serde
class NestedPriTuple:
    """
    Tuple containing nested primitives.
    """

    i: tuple[Int, Int, Int]
    s: tuple[Str, Str, Str, Str]
    f: tuple[Float, Float, Float, Float, Float]
    b: tuple[Bool, Bool, Bool, Bool, Bool, Bool]


@serde
@dataclass(unsafe_hash=True)
class PriDefault:
    """
    Primitives.
    """

    i: int = 10
    s: str = "foo"
    f: float = 100.0
    b: bool = True


@serde
class OptDefault:
    """
    Optionals.
    """

    n: int | None = None
    i: int | None = 10


class E(enum.Enum):
    S = "foo"
    F = 10.0
    B = True


class IE(enum.IntEnum):
    V0 = enum.auto()
    V1 = enum.auto()
    V2 = 10
    V3 = 100


@serde
class EnumInClass:
    """
    Class having enum fields.
    """

    e: IE = IE.V2
    o: E | None = E.S
    i: imported.IE = imported.IE.V1


@dataclass(unsafe_hash=True)
class Recur:
    a: Recur | None
    b: list[Recur] | None
    c: dict[str, Recur] | None


@dataclass(unsafe_hash=True)
class RecurContainer:
    a: list[RecurContainer]
    b: dict[str, RecurContainer]


serde(Recur)
serde(RecurContainer)


ListPri = list[Pri]

DictPri = dict[str, Pri]

INT = Int(10)

STR = Str("foo")

FLOAT = Float(100.0)

BOOL = Bool(True)

PRI = Pri(10, "foo", 100.0, True)

PRI_TUPLE = (10, "foo", 100.0, True)

PRILIST = ([10], ["foo"], [100.0], [True])

NESTED_PRILIST = ([INT], [STR], [FLOAT], [BOOL])

NESTED_PRILIST_TUPLE = ([(10,)], [("foo",)], [(100.0,)], [(True,)])


@serde
class Init:
    a: int
    b: int = field(init=False)

    def __post_init__(self) -> None:
        self.b = self.a * 10


class StrSubclass(str):
    pass


@serde
class PrimitiveSubclass:
    v: StrSubclass
