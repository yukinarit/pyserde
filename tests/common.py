import datetime
import decimal
import ipaddress
import itertools
import os
import pathlib
import sys
import uuid
from typing import Any, Dict, List, NewType, Optional, Set, Tuple

import more_itertools

from serde import from_dict, from_tuple, to_dict, to_tuple
from serde.json import from_json, to_json
from serde.msgpack import from_msgpack, to_msgpack
from serde.toml import from_toml, to_toml
from serde.yaml import from_yaml, to_yaml
from tests import data

format_dict: List = [(to_dict, from_dict)]

format_tuple: List = [(to_tuple, from_tuple)]

format_json: List = [(to_json, from_json)]

format_msgpack: List = [(to_msgpack, from_msgpack)]

format_yaml: List = [(to_yaml, from_yaml)]

format_toml: List = [(to_toml, from_toml)]

all_formats: List = format_dict + format_tuple + format_json + format_msgpack + format_yaml + format_toml

types: List = [
    (10, int),  # Primitive
    ('foo', str),
    (100.0, float),
    (True, bool),
    (10, Optional[int]),  # Optional
    (None, Optional[int]),
    ([1, 2], List[int]),  # Container
    ([1, 2], List),
    ([1, 2], list),
    ([], List[int]),
    ({1, 2}, Set[int]),
    ({1, 2}, Set),
    ({1, 2}, set),
    (set(), Set[int]),
    ((1, 1), Tuple[int, int]),
    ((1, 1), Tuple),
    ({'a': 1}, Dict[str, int]),
    ({'a': 1}, Dict),
    ({'a': 1}, dict),
    ({}, Dict[str, int]),
    (data.Pri(10, 'foo', 100.0, True), data.Pri),  # dataclass
    (data.Pri(10, 'foo', 100.0, True), Optional[data.Pri]),
    (None, Optional[data.Pri]),
    (10, NewType('Int', int)),  # NewType
    ({'a': 1}, Any),  # Any
    (pathlib.Path('/tmp/foo'), pathlib.Path),  # Extended types
    (pathlib.Path('/tmp/foo'), Optional[pathlib.Path]),
    (None, Optional[pathlib.Path]),
    (pathlib.PurePath('/tmp/foo'), pathlib.PurePath),
    (pathlib.PurePosixPath('/tmp/foo'), pathlib.PurePosixPath),
    (pathlib.PureWindowsPath('C:\\tmp'), pathlib.PureWindowsPath),
    (uuid.UUID("8f85b32c-a0be-466c-87eb-b7bbf7a01683"), uuid.UUID),
    (ipaddress.IPv4Address("127.0.0.1"), ipaddress.IPv4Address),
    (ipaddress.IPv6Address("::1"), ipaddress.IPv6Address),
    (ipaddress.IPv4Network("127.0.0.0/8"), ipaddress.IPv4Network),
    (ipaddress.IPv6Network("::/128"), ipaddress.IPv6Network),
    (ipaddress.IPv4Interface("192.168.1.1/24"), ipaddress.IPv4Interface),
    (ipaddress.IPv6Interface("::1/128"), ipaddress.IPv6Interface),
    (decimal.Decimal(10), decimal.Decimal),
    (datetime.datetime.strptime('Jan 1 2021 1:55PM', '%b %d %Y %I:%M%p'), datetime.datetime),
    (datetime.datetime.strptime('Jan 1 2021 1:55PM', '%b %d %Y %I:%M%p').date(), datetime.date),
    (datetime.datetime.strptime('Jan 1 2021 1:55PM', '%b %d %Y %I:%M%p').time(), datetime.time),
]

# these types can only be instantiated on their corresponding system
if os.name == "posix":
    types.append((pathlib.PosixPath('/tmp/foo'), pathlib.PosixPath))
if os.name == "nt":
    types.append((pathlib.WindowsPath('C:\\tmp'), pathlib.WindowsPath))

if sys.version_info[:3] >= (3, 9, 0):
    types.extend([([1, 2], list[int]), ({'a': 1}, dict[str, int]), ((1, 1), tuple[int, int])])

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
        t, T = pair
        return f'{typename(T)}({t})'

    return list(map(make_id, types))


def type_combinations_ids():
    from serde.compat import typename

    def make_id(quad: Tuple):
        t, T, u, U = quad
        return f'{typename(T)}({t})-{typename(U)}({u})'

    return list(map(make_id, types_combinations))
