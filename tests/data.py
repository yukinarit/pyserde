from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from serde import deserialize, serialize


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Int:
    """
    Integer.
    """

    i: int


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Str:
    """
    String.
    """

    s: str


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Float:
    """
    Float.
    """

    f: float


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Bool:
    """
    Boolean.
    """

    b: bool


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class Pri:
    """
    Primitives.
    """

    i: int
    s: str
    f: float
    b: bool


@deserialize
@serialize
@dataclass
class PriOpt:
    """
    Optional Primitives.
    """

    i: Optional[int]
    s: Optional[str]
    f: Optional[float]
    b: Optional[bool]


@deserialize
@serialize
@dataclass
class PriList:
    """
    List containing primitives.
    """

    i: List[int]
    s: List[str]
    f: List[float]
    b: List[bool]


@deserialize
@serialize
@dataclass
class PriDict:
    """
    Dict containing primitives.
    """

    i: Dict[int, int]
    s: Dict[str, str]
    f: Dict[float, float]
    b: Dict[bool, bool]


@deserialize
@serialize
@dataclass
class PriTuple:
    """
    Tuple containing primitives.
    """

    i: Tuple[int, int, int]
    s: Tuple[str, str, str, str]
    f: Tuple[float, float, float, float, float]
    b: Tuple[bool, bool, bool, bool, bool, bool]


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class NestedInt:
    """
    Nested integer.
    """

    i: Int


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class NestedPri:
    """
    Nested primitives.
    """

    i: Int
    s: Str
    f: Float
    b: Bool


@deserialize
@serialize
@dataclass
class NestedPriOpt:
    """
    Optional Primitives.
    """

    i: Optional[Int]
    s: Optional[Str]
    f: Optional[Float]
    b: Optional[Bool]


@deserialize
@serialize
@dataclass
class NestedPriList:
    """
    List containing nested primitives.
    """

    i: List[Int]
    s: List[Str]
    f: List[Float]
    b: List[Bool]


@deserialize
@serialize
@dataclass
class NestedPriDict:
    """
    Dict containing nested primitives.
    """

    i: Dict[Str, Int]
    s: Dict[Str, Str]
    f: Dict[Str, Float]
    b: Dict[Str, Bool]


@deserialize
@serialize
@dataclass
class NestedPriTuple:
    """
    Tuple containing nested primitives.
    """

    i: Tuple[Int, Int, Int]
    s: Tuple[Str, Str, Str, Str]
    f: Tuple[Float, Float, Float, Float, Float]
    b: Tuple[Bool, Bool, Bool, Bool, Bool, Bool]


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class PriDefault:
    """
    Primitives.
    """

    i: int = 10
    s: str = 'foo'
    f: float = 100.0
    b: bool = True


INT = Int(10)

STR = Str('foo')

FLOAT = Float(100.0)

BOOL = Bool(True)

PRI = Pri(10, 'foo', 100.0, True)

PRI_TUPLE = (10, 'foo', 100.0, True)

PRILIST = ([10], ['foo'], [100.0], [True])

NESTED_PRILIST = ([INT], [STR], [FLOAT], [BOOL])

NESTED_PRILIST_TUPLE = ([(10,)], [('foo',)], [(100.0,)], [(True,)])
