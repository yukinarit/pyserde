import datetime
import decimal
import ipaddress
import itertools
import os
import pathlib
import uuid
from collections.abc import MutableSequence, MutableSet, Sequence, Set
from typing import (
    Any,
    Generic,
    NewType,
    Optional,
    TypeVar,
    Union,
    Callable,
)
from typing_extensions import TypeAlias

import more_itertools

from serde import from_dict, from_tuple, serde, to_dict, to_tuple
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack
from serde.pickle import from_pickle, to_pickle
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml
from tests import data

FormatFuncs: TypeAlias = list[tuple[Callable[..., Any], Callable[..., Any]]]

format_dict: FormatFuncs = [(to_dict, from_dict)]

format_tuple: FormatFuncs = [(to_tuple, from_tuple)]

format_json: FormatFuncs = [(to_json, from_json)]

format_msgpack: FormatFuncs = [(to_msgpack, from_msgpack)]

format_yaml: FormatFuncs = [(to_yaml, from_yaml)]

format_toml: FormatFuncs = [(to_toml, from_toml)]

format_pickle: FormatFuncs = [(to_pickle, from_pickle)]

all_formats: FormatFuncs = (
    format_dict
    + format_tuple
    + format_json
    + format_msgpack
    + format_yaml
    + format_toml
    + format_pickle
)

T = TypeVar("T")

U = TypeVar("U")

V = TypeVar("V")


@serde
class GenericClass(Generic[T, U]):
    a: T
    b: U


@serde
class Inner(Generic[T]):
    c: T


@serde
class NestedGenericClass(Generic[U, V]):
    a: U
    b: Inner[V]


Filter: TypeAlias = Callable[..., bool]


def param(val: T, typ: U, filter: Optional[Filter] = None) -> tuple[T, U, Filter]:
    """
    Create a test parameter

    * `val` is the expected value
    * `typ` is the expected type
    * If `filter` evaluates to True, it will filter this test case.
    """
    return (val, typ, filter or (lambda se, de, opt: False))


def toml_not_supported(se: Any, de: Any, opt: Any) -> bool:
    return se is to_toml


def yaml_not_supported(se: Any, de: Any, opt: Any) -> bool:
    return se is to_yaml


types: list[tuple[Any, Any, Any]] = [
    param(10, int),  # Primitive
    param("foo", str),
    param(100.0, float),
    param(True, bool),
    param(10, Optional[int]),  # Optional
    param(None, Optional[int], toml_not_supported),
    param([1, 2], list[int]),  # Container
    param([1, 2], list),
    param([], list[int]),
    param([1, 2], Sequence[int]),
    param([1, 2], Sequence),
    param([1, 2], MutableSequence[int]),
    param([1, 2], MutableSequence),
    param({1, 2}, set[int], toml_not_supported),
    param({1, 2}, set, toml_not_supported),
    param(set(), set[int], toml_not_supported),
    param(frozenset({1, 2}), frozenset[int], toml_not_supported),
    param(frozenset({1, 2}), Set[int], toml_not_supported),
    param({1, 2}, Set, toml_not_supported),
    param({1, 2}, MutableSet[int], toml_not_supported),
    param({1, 2}, MutableSet, toml_not_supported),
    param((1, 1), tuple[int, int]),
    param((1, 1), tuple),
    param((1, 2, 3), tuple[int, ...]),
    param({"a": 1}, dict[str, int]),
    param({"a": 1}, dict),
    param({"a": 1}, dict),
    param({}, dict[str, int]),
    param({"a": 1}, dict[str, int]),
    # param({"a": 1}, defaultdict[str, int]),
    # param({"a": [1]}, defaultdict[str, list[int]]),
    param(data.Pri(10, "foo", 100.0, True), data.Pri),  # dataclass
    param(data.Pri(10, "foo", 100.0, True), Optional[data.Pri]),
    param(
        data.PrimitiveSubclass(data.StrSubclass("a")), data.PrimitiveSubclass, yaml_not_supported
    ),
    param(None, Optional[data.Pri], toml_not_supported),
    param(data.Recur(data.Recur(None, None, None), None, None), data.Recur, toml_not_supported),
    param(
        data.RecurContainer([data.RecurContainer([], {})], {"c": data.RecurContainer([], {})}),
        data.RecurContainer,
        toml_not_supported,
    ),
    param(data.Init(1), data.Init),
    param(10, NewType("Int", int)),  # NewType
    param({"a": 1}, Any),  # Any
    param(GenericClass[str, int]("foo", 10), GenericClass[str, int]),
    param(NestedGenericClass[str, int]("foo", Inner[int](10)), NestedGenericClass[str, int]),
    param(pathlib.Path("/tmp/foo"), pathlib.Path),  # Extended types
    param(pathlib.Path("/tmp/foo"), Optional[pathlib.Path]),
    param(None, Optional[pathlib.Path], toml_not_supported),
    param(pathlib.PurePath("/tmp/foo"), pathlib.PurePath),
    param(pathlib.PurePosixPath("/tmp/foo"), pathlib.PurePosixPath),
    param(pathlib.PureWindowsPath("C:\\tmp"), pathlib.PureWindowsPath),
    param(uuid.UUID("8f85b32c-a0be-466c-87eb-b7bbf7a01683"), uuid.UUID),
    param(ipaddress.IPv4Address("127.0.0.1"), ipaddress.IPv4Address),
    param(ipaddress.IPv6Address("::1"), ipaddress.IPv6Address),
    param(ipaddress.IPv4Network("127.0.0.0/8"), ipaddress.IPv4Network),
    param(ipaddress.IPv6Network("::/128"), ipaddress.IPv6Network),
    param(ipaddress.IPv4Interface("192.168.1.1/24"), ipaddress.IPv4Interface),
    param(ipaddress.IPv6Interface("::1/128"), ipaddress.IPv6Interface),
    param(decimal.Decimal(10), decimal.Decimal),
    param(datetime.datetime.strptime("Jan 1 2021 1:55PM", "%b %d %Y %I:%M%p"), datetime.datetime),
    param(
        datetime.datetime.strptime("Jan 1 2021 1:55PM", "%b %d %Y %I:%M%p").date(), datetime.date
    ),
    param(
        datetime.datetime.strptime("Jan 1 2021 1:55PM", "%b %d %Y %I:%M%p").time(), datetime.time
    ),
]

# these types can only be instantiated on their corresponding system
if os.name == "posix":
    types.append(param(pathlib.PosixPath("/tmp/foo"), pathlib.PosixPath))
if os.name == "nt":
    types.append(param(pathlib.WindowsPath("C:\\tmp"), pathlib.WindowsPath))

types_combinations: list[Any] = [
    list(more_itertools.flatten(c)) for c in itertools.combinations(types, 2)
]

opt_case: list[dict[str, Union[bool, str]]] = [
    {"reuse_instances_default": False},
    {"reuse_instances_default": False, "rename_all": "camelcase"},
    {"reuse_instances_default": False, "rename_all": "snakecase"},
]


def make_id_from_dict(d: dict[str, Union[bool, str]]) -> str:
    if not d:
        return "none"
    else:
        key = list(d)[0]
        return f"{key}-{d[key]}"


def opt_case_ids() -> list[str]:
    """
    Create parametrize test id
    """
    return list(map(make_id_from_dict, opt_case))


def type_ids() -> list[str]:
    """
    Create parametrize test id
    """
    from serde.compat import typename

    def make_id(pair: tuple[Any, ...]) -> str:
        t, T, _ = pair
        return f"{typename(T)}({t})"

    return list(map(make_id, types))


def type_combinations_ids() -> list[str]:
    """
    Create parametrize test id
    """
    from serde.compat import typename

    def make_id(quad: tuple[Any, ...]) -> str:
        t, T, u, U = quad
        return f"{typename(T)}({t})-{typename(U)}({u})"

    return list(map(make_id, types_combinations))
