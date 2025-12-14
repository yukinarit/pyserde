from collections.abc import Sequence, MutableSequence

from serde import serde, to_dict
from serde.de import from_dict
from serde.json import from_json, to_json


def test_sequence_field_roundtrip() -> None:
    @serde
    class Foo:
        xs: Sequence[int]

    foo = Foo(xs=(1, 2, 3))
    assert to_dict(foo) == {"xs": [1, 2, 3]}

    foo2 = from_dict(Foo, {"xs": [1, 2, 3]})
    assert foo2.xs == [1, 2, 3]


def test_sequence_field_json_roundtrip() -> None:
    @serde
    class Foo:
        xs: Sequence[int]

    foo = Foo(xs=(1, 2, 3))
    assert to_json(foo) == '{"xs":[1,2,3]}'
    foo2 = from_json(Foo, '{"xs":[1,2,3]}')
    assert foo2.xs == [1, 2, 3]


def test_mutablesequence_field_roundtrip() -> None:
    @serde
    class Foo:
        xs: MutableSequence[int]

    foo = Foo(xs=[1, 2, 3])
    assert to_dict(foo) == {"xs": [1, 2, 3]}

    foo2 = from_dict(Foo, {"xs": [1, 2, 3]})
    assert foo2.xs == [1, 2, 3]

    assert to_json(foo) == '{"xs":[1,2,3]}'
    foo3 = from_json(Foo, '{"xs":[1,2,3]}')
    assert foo3.xs == [1, 2, 3]
