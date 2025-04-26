from serde import serde
from serde.json import to_json, from_json
from typing import Optional


def test_json_basics() -> None:
    @serde
    class Foo:
        v: Optional[int]

    f = Foo(10)
    assert '{"v":10}' == to_json(f)
    assert f == from_json(Foo, '{"v":10}')

    @serde
    class Bar:
        v: set[int]

    b = Bar({1, 2, 3})
    assert '{"v":[1,2,3]}' == to_json(b)
    assert b == from_json(Bar, '{"v":[1,2,3]}')


def test_skip_none() -> None:
    @serde
    class Foo:
        a: int
        b: Optional[int]

    f = Foo(10, 100)
    assert to_json(f, skip_none=True) == '{"a":10,"b":100}'

    f = Foo(10, None)
    assert to_json(f, skip_none=True) == '{"a":10}'
