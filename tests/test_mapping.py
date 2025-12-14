from collections.abc import Mapping, MutableMapping
from collections import UserDict
from types import MappingProxyType

from serde import serde, to_dict
from serde.de import from_dict
from serde.json import from_json, to_json


def test_mapping_field_roundtrip() -> None:
    @serde
    class Foo:
        m: Mapping[str, int]

    foo = Foo(m=MappingProxyType({"a": 1, "b": 2}))
    assert to_dict(foo) == {"m": {"a": 1, "b": 2}}

    foo2 = from_dict(Foo, {"m": {"a": 1, "b": 2}})
    assert foo2.m == {"a": 1, "b": 2}

    assert to_json(foo) == '{"m":{"a":1,"b":2}}'
    foo3 = from_json(Foo, '{"m":{"a":1,"b":2}}')
    assert foo3.m == {"a": 1, "b": 2}


def test_mutablemapping_field_roundtrip() -> None:
    @serde
    class Foo:
        mm: MutableMapping[str, int]

    foo = Foo(mm=UserDict({"a": 1, "b": 2}))
    assert to_dict(foo) == {"mm": {"a": 1, "b": 2}}

    foo2 = from_dict(Foo, {"mm": {"a": 1, "b": 2}})
    assert foo2.mm == {"a": 1, "b": 2}

    assert to_json(foo) == '{"mm":{"a":1,"b":2}}'
    foo3 = from_json(Foo, '{"mm":{"a":1,"b":2}}')
    assert foo3.mm == {"a": 1, "b": 2}
