import pytest
from collections.abc import Sequence, MutableSequence

import serde as serde_pkg
from serde import serde
from serde.json import deserialize_json_numbers, from_json, to_json


def test_json_basics() -> None:
    @serde
    class Foo:
        v: int | None

    f = Foo(10)
    assert '{"v":10}' == to_json(f)
    assert f == from_json(Foo, '{"v":10}')

    @serde
    class Bar:
        v: set[int]

    b = Bar({1, 2, 3})
    assert '{"v":[1,2,3]}' == to_json(b)
    assert b == from_json(Bar, '{"v":[1,2,3]}')

    @serde
    class Baz:
        v: Sequence[int]

    baz = Baz((1, 2, 3))
    assert '{"v":[1,2,3]}' == to_json(baz)
    assert from_json(Baz, '{"v":[1,2,3]}').v == [1, 2, 3]

    @serde
    class Qux:
        v: MutableSequence[int]

    qux = Qux([1, 2, 3])
    assert '{"v":[1,2,3]}' == to_json(qux)
    assert from_json(Qux, '{"v":[1,2,3]}').v == [1, 2, 3]


def test_skip_none() -> None:
    @serde
    class Foo:
        a: int
        b: int | None

    f = Foo(10, 100)
    assert to_json(f, skip_none=True) == '{"a":10,"b":100}'

    f = Foo(10, None)
    assert to_json(f, skip_none=True) == '{"a":10}'


def test_skip_none_nested() -> None:
    """Test that skip_none propagates to nested objects."""

    @serde
    class Inner:
        a: int
        b: int | None

    @serde
    class Outer:
        i: Inner
        j: int
        k: int | None

    # Test nested dataclass with skip_none
    o = Outer(i=Inner(a=1, b=None), j=3, k=None)
    result = to_json(o, skip_none=True)
    expected = '{"i":{"a":1},"j":3}'
    assert result == expected

    # Test union with nested dataclass and skip_none
    @serde
    class WithUnion:
        u: Inner | str
        value: str | None

    u = WithUnion(u=Inner(a=5, b=None), value=None)
    result = to_json(u, skip_none=True)
    expected = '{"u":{"Inner":{"a":5}}}'
    assert result == expected

    # Test list with nested objects and skip_none
    @serde
    class WithList:
        items: list[Inner]
        name: str | None

    w = WithList(items=[Inner(a=1, b=None), Inner(a=2, b=3)], name=None)
    result = to_json(w, skip_none=True)
    expected = '{"items":[{"a":1},{"a":2,"b":3}]}'
    assert result == expected


def test_deserialize_json_numbers() -> None:
    @serde
    class Foo:
        value: float = serde_pkg.field(deserializer=deserialize_json_numbers)

    assert from_json(Foo, '{"value": 0}').value == 0.0
    assert from_json(Foo, '{"value": 0.5}').value == 0.5

    with pytest.raises(serde_pkg.SerdeError):
        from_json(Foo, '{"value": true}')


def test_coerce_numbers_json() -> None:
    @serde
    class Foo:
        value: float

    foo = from_json(Foo, '{"value": 1}')
    assert foo.value == 1.0

    @serde
    class Bar:
        values: list[float]

    bar = from_json(Bar, '{"values":[1,2]}')
    assert bar.values == [1.0, 2.0]

    with pytest.raises(serde_pkg.SerdeError):
        from_json(Bar, '{"values":[1,"2"]}')

    with pytest.raises(serde_pkg.SerdeError):
        from_json(Foo, '{"value": 1}', coerce_numbers=False)

    with pytest.raises(serde_pkg.SerdeError):
        from_json(Foo, '{"value": true}')


def test_json_numbers_with_union() -> None:
    @serde
    class Foo:
        value: float | int

    assert from_json(Foo, '{"value": 1}').value == 1.0

    with pytest.raises(serde_pkg.SerdeError):
        from_json(Foo, '{"value": "1"}')

    @serde
    class Bar:
        value: int | float

    assert from_json(Bar, '{"value": 1}').value == 1

    with pytest.raises(serde_pkg.SerdeError):
        from_json(Bar, '{"value": "1"}')
