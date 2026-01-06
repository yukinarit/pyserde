from collections import deque


from serde import serde
from serde.json import from_json, to_json
from serde.core import is_instance
from serde.compat import is_deque, is_bare_deque


def test_is_deque() -> None:
    assert is_deque(deque[int])
    assert is_deque(deque[str])
    assert is_deque(deque)
    assert not is_deque(list[int])
    assert not is_deque(list)
    assert not is_deque(set[int])


def test_is_bare_deque() -> None:
    assert is_bare_deque(deque)
    assert not is_bare_deque(deque[int])
    assert not is_bare_deque(deque[str])
    assert not is_bare_deque(list)


def test_is_instance_deque() -> None:
    assert is_instance(deque([1, 2, 3]), deque[int])
    assert is_instance(deque(["a", "b"]), deque[str])
    assert is_instance(deque(), deque[int])
    assert is_instance(deque([1, 2, 3]), deque)
    assert not is_instance([1, 2, 3], deque[int])


def test_deque_roundtrip() -> None:
    @serde
    class Foo:
        d: deque[int]

    foo = Foo(d=deque([1, 2, 3]))
    json_str = to_json(foo)
    assert json_str == '{"d":[1,2,3]}'

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.d, deque)
    assert list(foo2.d) == [1, 2, 3]


def test_deque_str() -> None:
    @serde
    class Foo:
        d: deque[str]

    foo = Foo(d=deque(["a", "b", "c"]))
    json_str = to_json(foo)
    assert json_str == '{"d":["a","b","c"]}'

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.d, deque)
    assert list(foo2.d) == ["a", "b", "c"]


def test_bare_deque() -> None:
    @serde
    class Foo:
        d: deque

    foo = Foo(d=deque([1, "a", 3.0]))
    json_str = to_json(foo)
    assert json_str == '{"d":[1,"a",3.0]}'

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.d, deque)
    assert list(foo2.d) == [1, "a", 3.0]


def test_nested_deque() -> None:
    @serde
    class Inner:
        value: int

    @serde
    class Outer:
        items: deque[Inner]

    outer = Outer(items=deque([Inner(1), Inner(2), Inner(3)]))
    json_str = to_json(outer)
    assert json_str == '{"items":[{"value":1},{"value":2},{"value":3}]}'

    outer2 = from_json(Outer, json_str)
    assert isinstance(outer2.items, deque)
    assert len(outer2.items) == 3
    assert all(isinstance(item, Inner) for item in outer2.items)
    assert [item.value for item in outer2.items] == [1, 2, 3]


def test_deque_empty() -> None:
    @serde
    class Foo:
        d: deque[int]

    foo = Foo(d=deque())
    json_str = to_json(foo)
    assert json_str == '{"d":[]}'

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.d, deque)
    assert len(foo2.d) == 0


def test_deque_optional() -> None:
    from typing import Optional

    @serde
    class Foo:
        d: Optional[deque[int]]

    foo = Foo(d=deque([1, 2, 3]))
    json_str = to_json(foo)
    assert json_str == '{"d":[1,2,3]}'

    foo2 = from_json(Foo, json_str)
    assert foo2.d is not None
    assert isinstance(foo2.d, deque)
    assert list(foo2.d) == [1, 2, 3]

    foo_none = Foo(d=None)
    json_str_none = to_json(foo_none)
    assert json_str_none == '{"d":null}'

    foo_none2 = from_json(Foo, json_str_none)
    assert foo_none2.d is None


def test_deque_with_other_fields() -> None:
    @serde
    class Foo:
        name: str
        values: deque[int]
        count: int

    foo = Foo(name="test", values=deque([1, 2, 3]), count=42)
    json_str = to_json(foo)
    assert json_str == '{"name":"test","values":[1,2,3],"count":42}'

    foo2 = from_json(Foo, json_str)
    assert foo2.name == "test"
    assert isinstance(foo2.values, deque)
    assert list(foo2.values) == [1, 2, 3]
    assert foo2.count == 42
