import datetime
import decimal
import ipaddress
import itertools
import os
import pathlib
import sys
import uuid
from typing import Any, Callable, Dict, FrozenSet, Generic, List, NewType, Optional, Set, Tuple, TypeVar

import more_itertools

from serde import from_dict, from_tuple, serde, to_dict, to_tuple
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack
from serde.pickle import from_pickle, to_pickle
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml
from tests import data

format_dict: List = [(to_dict, from_dict)]

format_tuple: List = [(to_tuple, from_tuple)]

format_json: List = [(to_json, from_json)]

format_msgpack: List = [(to_msgpack, from_msgpack)]

format_yaml: List = [(to_yaml, from_yaml)]

format_toml: List = [(to_toml, from_toml)]

format_pickle: List = [(to_pickle, from_pickle)]

all_formats: List = (
    format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_toml + format_pickle
)

T = TypeVar('T')

U = TypeVar('U')


@serde
class GenericClass(Generic[T, U]):
    a: T
    b: U


def param(val, typ, filter: Optional[Callable] = None):
    """
    Create a test parameter

    * `val` is the expected value
    * `typ` is the expected type
    * If `filter` evaluates to True, it will filter this test case.
    """
    return (val, typ, filter or (lambda se, de, opt: False))


def toml_not_supported(se, de, opt) -> bool:
    return se is to_toml


types: List = [
    param(10, int),  # Primitive
    param('foo', str),
    param(100.0, float),
    param(True, bool),
    param(10, Optional[int]),  # Optional
    param(None, Optional[int], toml_not_supported),
    param([1, 2], List[int]),  # Container
    param([1, 2], List),
    param([1, 2], list),
    param([], List[int]),
    param({1, 2}, Set[int], toml_not_supported),
    param({1, 2}, Set, toml_not_supported),
    param({1, 2}, set, toml_not_supported),
    param(set(), Set[int], toml_not_supported),
    param({1, 2}, FrozenSet[int], toml_not_supported),
    param((1, 1), Tuple[int, int]),
    param((1, 1), Tuple),
    param((1, 1), Tuple[int, ...]),
    param({'a': 1}, Dict[str, int]),
    param({'a': 1}, Dict),
    param({'a': 1}, dict),
    param({}, Dict[str, int]),
    param(data.Pri(10, 'foo', 100.0, True), data.Pri),  # dataclass
    param(data.Pri(10, 'foo', 100.0, True), Optional[data.Pri]),
    param(None, Optional[data.Pri], toml_not_supported),
    param(10, NewType('Int', int)),  # NewType
    param({'a': 1}, Any),  # Any
    param(GenericClass[str, int]('foo', 10), GenericClass[str, int]),  # Generic
    param(pathlib.Path('/tmp/foo'), pathlib.Path),  # Extended types
    param(pathlib.Path('/tmp/foo'), Optional[pathlib.Path]),
    param(None, Optional[pathlib.Path], toml_not_supported),
    param(pathlib.PurePath('/tmp/foo'), pathlib.PurePath),
    param(pathlib.PurePosixPath('/tmp/foo'), pathlib.PurePosixPath),
    param(pathlib.PureWindowsPath('C:\\tmp'), pathlib.PureWindowsPath),
    param(uuid.UUID("8f85b32c-a0be-466c-87eb-b7bbf7a01683"), uuid.UUID),
    param(ipaddress.IPv4Address("127.0.0.1"), ipaddress.IPv4Address),
    param(ipaddress.IPv6Address("::1"), ipaddress.IPv6Address),
    param(ipaddress.IPv4Network("127.0.0.0/8"), ipaddress.IPv4Network),
    param(ipaddress.IPv6Network("::/128"), ipaddress.IPv6Network),
    param(ipaddress.IPv4Interface("192.168.1.1/24"), ipaddress.IPv4Interface),
    param(ipaddress.IPv6Interface("::1/128"), ipaddress.IPv6Interface),
    param(decimal.Decimal(10), decimal.Decimal),
    param(datetime.datetime.strptime('Jan 1 2021 1:55PM', '%b %d %Y %I:%M%p'), datetime.datetime),
    param(datetime.datetime.strptime('Jan 1 2021 1:55PM', '%b %d %Y %I:%M%p').date(), datetime.date),
    param(datetime.datetime.strptime('Jan 1 2021 1:55PM', '%b %d %Y %I:%M%p').time(), datetime.time),
]

# these types can only be instantiated on their corresponding system
if os.name == "posix":
    types.append(param(pathlib.PosixPath('/tmp/foo'), pathlib.PosixPath))
if os.name == "nt":
    types.append(param(pathlib.WindowsPath('C:\\tmp'), pathlib.WindowsPath))

if sys.version_info[:3] >= (3, 9, 0):
    types.extend([param([1, 2], list[int]), param({'a': 1}, dict[str, int]), param((1, 1), tuple[int, int])])

types_combinations: List = list(map(lambda c: list(more_itertools.flatten(c)), itertools.combinations(types, 2)))

opt_case: List = [
    {'reuse_instances_default': False},
    {'reuse_instances_default': False, 'rename_all': 'camelcase'},
    {'reuse_instances_default': False, 'rename_all': 'snakecase'},
]


def make_id_from_dict(d: Dict) -> str:
    if not d:
        return 'none'
    else:
        key = list(d)[0]
        return f'{key}-{d[key]}'


def opt_case_ids():
    return list(map(make_id_from_dict, opt_case))


def type_ids():
    from serde.compat import typename

    def make_id(pair: Tuple):
        t, T, _ = pair
        return f'{typename(T)}({t})'

    return list(map(make_id, types))


def type_combinations_ids():
    from serde.compat import typename

    def make_id(quad: Tuple):
        t, T, u, U = quad
        return f'{typename(T)}({t})-{typename(U)}({u})'

    return list(map(make_id, types_combinations))
