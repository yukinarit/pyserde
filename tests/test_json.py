from serde import serde
from serde.json import to_json, from_json
from typing import Optional, Union, List


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


def test_skip_none_nested() -> None:
    """Test that skip_none propagates to nested objects."""

    @serde
    class Inner:
        a: int
        b: Optional[int]

    @serde
    class Outer:
        i: Inner
        j: int
        k: Optional[int]

    # Test nested dataclass with skip_none
    o = Outer(i=Inner(a=1, b=None), j=3, k=None)
    result = to_json(o, skip_none=True)
    expected = '{"i":{"a":1},"j":3}'
    assert result == expected

    # Test union with nested dataclass and skip_none
    @serde
    class WithUnion:
        u: Union[Inner, str]
        value: Optional[str]

    u = WithUnion(u=Inner(a=5, b=None), value=None)
    result = to_json(u, skip_none=True)
    expected = '{"u":{"Inner":{"a":5}}}'
    assert result == expected

    # Test list with nested objects and skip_none
    @serde
    class WithList:
        items: List[Inner]
        name: Optional[str]

    w = WithList(items=[Inner(a=1, b=None), Inner(a=2, b=3)], name=None)
    result = to_json(w, skip_none=True)
    expected = '{"items":[{"a":1},{"a":2,"b":3}]}'
    assert result == expected
