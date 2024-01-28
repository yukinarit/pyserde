from __future__ import annotations
import sys
import enum
from dataclasses import dataclass
from typing import Optional, Any
from beartype.typing import Dict, List, Tuple

from serde import field, serde, disabled

from . import imported


@serde
@dataclass
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
    def uncheck_new(value: Any) -> "Int":
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

    i: Optional[int]
    s: Optional[str]
    f: Optional[float]
    b: Optional[bool]


@serde
class PriList:
    """
    List containing primitives.
    """

    i: List[int]
    s: List[str]
    f: List[float]
    b: List[bool]


@serde
class PriDict:
    """
    Dict containing primitives.
    """

    i: Dict[str, int]
    s: Dict[str, str]
    f: Dict[str, float]
    b: Dict[str, bool]


@serde
class PriTuple:
    """
    Tuple containing primitives.
    """

    i: Tuple[int, int, int]
    s: Tuple[str, str, str, str]
    f: Tuple[float, float, float, float, float]
    b: Tuple[bool, bool, bool, bool, bool, bool]


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

    i: Optional[Int]
    s: Optional[Str]
    f: Optional[Float]
    b: Optional[Bool]


@serde
class NestedPriList:
    """
    List containing nested primitives.
    """

    i: List[Int]
    s: List[Str]
    f: List[Float]
    b: List[Bool]


@serde
class NestedPriDict:
    """
    Dict containing nested primitives.
    """

    i: Dict[Str, Int]
    s: Dict[Str, Str]
    f: Dict[Str, Float]
    b: Dict[Str, Bool]


@serde
class NestedPriTuple:
    """
    Tuple containing nested primitives.
    """

    i: Tuple[Int, Int, Int]
    s: Tuple[Str, Str, Str, Str]
    f: Tuple[Float, Float, Float, Float, Float]
    b: Tuple[Bool, Bool, Bool, Bool, Bool, Bool]


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

    n: Optional[int] = None
    i: Optional[int] = 10


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
    o: Optional[E] = E.S
    i: imported.IE = imported.IE.V1


if sys.version_info[:2] <= (3, 8):

    @dataclass(unsafe_hash=True)
    class Recur38:
        a: Optional["Recur38"]
        b: Optional[List["Recur38"]]
        c: Optional[Dict[str, "Recur38"]]

    @dataclass(unsafe_hash=True)
    class RecurContainer38:
        a: List["RecurContainer38"]
        b: Dict[str, "RecurContainer38"]

    serde(Recur38)
    serde(RecurContainer38)


@dataclass(unsafe_hash=True)
class Recur:
    a: Optional[Recur]
    b: Optional[list[Recur]]
    c: Optional[dict[str, Recur]]


@dataclass(unsafe_hash=True)
class RecurContainer:
    a: list[RecurContainer]
    b: dict[str, RecurContainer]


serde(Recur)
serde(RecurContainer)


ListPri = List[Pri]

DictPri = Dict[str, Pri]

INT = Int(10)

STR = Str("foo")

FLOAT = Float(100.0)

BOOL = Bool(True)

PRI = Pri(10, "foo", 100.0, True)

PRI_TUPLE = (10, "foo", 100.0, True)

PRILIST = ([10], ["foo"], [100.0], [True])

NESTED_PRILIST = ([INT], [STR], [FLOAT], [BOOL])

NESTED_PRILIST_TUPLE = ([(10,)], [("foo",)], [(100.0,)], [(True,)])


@dataclass
@serde
class Init:
    a: int
    b: int = field(init=False)

    def __post_init__(self) -> None:
        self.b = self.a * 10


class StrSubclass(str):
    pass


@serde
@dataclass
class PrimitiveSubclass:
    v: StrSubclass
