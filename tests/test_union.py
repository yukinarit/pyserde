import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from serde import deserialize
from serde import init as serde_init
from serde import logger, serialize
from serde.json import from_json, to_json

logging.basicConfig(level=logging.WARNING)
logger.setLevel(logging.DEBUG)

serde_init(True)


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class PriUnion:
    """
    Union Primitives.
    """

    v: Union[int, str, float, bool]


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class PriOptUnion:
    """
    Union Primitives.
    """

    v: Union[Optional[int], Optional[str], Optional[float], Optional[bool]]


@deserialize
@serialize
@dataclass(unsafe_hash=True)
class ContUnion:
    """
    Union Containers.
    """

    v: Union[List[int], List[str], Dict[str, int]]


def test_union():
    v = PriUnion(10)
    s = '{"v": 10}'
    assert s == to_json(v)
    print(f'foo {v.__serde_hidden__.code}')
    assert v == from_json(PriUnion, s, strict=False)

    v = PriUnion(10.0)
    s = '{"v": 10.0}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion('foo')
    s = '{"v": "foo"}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)

    v = PriUnion(True)
    s = '{"v": true}'
    assert s == to_json(v)
    assert v == from_json(PriUnion, s)


def test_union_optional():
    v = PriOptUnion(10)
    s = '{"v": 10}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(None)
    s = '{"v": null}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion("foo")
    s = '{"v": "foo"}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(10.0)
    s = '{"v": 10.0}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)

    v = PriOptUnion(False)
    s = '{"v": false}'
    assert s == to_json(v)
    assert v == from_json(PriOptUnion, s)


def test_union_containers():
    v = ContUnion([1, 2, 3])
    s = '{"v": [1, 2, 3]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion(['1', '2', '3'])
    s = '{"v": ["1", "2", "3"]}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)

    v = ContUnion({'a': 1, 'b': 2, 'c': 3})
    s = '{"v": {"a": 1, "b": 2, "c": 3}}'
    assert s == to_json(v)
    assert v == from_json(ContUnion, s)
