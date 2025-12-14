from collections.abc import MutableSet, Set

from serde import serde, to_dict
from serde.de import from_dict
from serde.json import from_json, to_json


def test_abc_set_fields_roundtrip() -> None:
    @serde
    class Foo:
        s: Set[str]
        ms: MutableSet[str]

    foo = Foo(s=frozenset({"a", "b"}), ms=set({"c", "d"}))

    d = to_dict(foo, convert_sets=True)
    assert set(d["s"]) == {"a", "b"}
    assert set(d["ms"]) == {"c", "d"}

    foo2 = from_dict(Foo, d)
    assert foo2.s == {"a", "b"}
    assert foo2.ms == {"c", "d"}

    foo3 = from_json(Foo, to_json(foo))
    assert foo3.s == {"a", "b"}
    assert foo3.ms == {"c", "d"}
