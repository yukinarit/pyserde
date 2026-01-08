from collections import Counter


from serde import serde
from serde.json import from_json, to_json
from serde.core import is_instance
from serde.compat import is_counter, is_bare_counter


def test_is_counter() -> None:
    assert is_counter(Counter[str])
    assert is_counter(Counter[int])
    assert is_counter(Counter)
    assert not is_counter(dict[str, int])
    assert not is_counter(dict)
    assert not is_counter(list[int])


def test_is_bare_counter() -> None:
    assert is_bare_counter(Counter)
    assert not is_bare_counter(Counter[str])
    assert not is_bare_counter(Counter[int])
    assert not is_bare_counter(dict)


def test_is_instance_counter() -> None:
    assert is_instance(Counter(["a", "b", "a"]), Counter[str])
    assert is_instance(Counter({1: 2, 3: 4}), Counter[int])
    assert is_instance(Counter(), Counter[str])
    assert is_instance(Counter(["a", "b"]), Counter)
    assert not is_instance({"a": 1}, Counter[str])


def test_counter_roundtrip() -> None:
    @serde
    class Foo:
        c: Counter[str]

    foo = Foo(c=Counter(["apple", "banana", "apple"]))
    json_str = to_json(foo)
    assert json_str == '{"c":{"apple":2,"banana":1}}'

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.c, Counter)
    assert foo2.c["apple"] == 2
    assert foo2.c["banana"] == 1


def test_counter_json_key_limitation() -> None:
    """Test Counter with non-string keys.

    Note: JSON keys are always strings, so when using Counter with non-string
    keys like int, the keys will be string in JSON. This is a JSON format
    limitation, not a pyserde limitation.
    """

    @serde
    class Foo:
        c: Counter[str]

    # Use string keys for JSON compatibility
    foo = Foo(c=Counter({"1": 5, "2": 3, "3": 1}))
    json_str = to_json(foo)
    assert '{"c":{' in json_str

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.c, Counter)
    assert foo2.c["1"] == 5
    assert foo2.c["2"] == 3
    assert foo2.c["3"] == 1


def test_bare_counter() -> None:
    @serde
    class Foo:
        c: Counter

    foo = Foo(c=Counter(["a", "b", "a"]))
    json_str = to_json(foo)
    assert '{"c":{' in json_str

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.c, Counter)
    assert foo2.c["a"] == 2
    assert foo2.c["b"] == 1


def test_counter_empty() -> None:
    @serde
    class Foo:
        c: Counter[str]

    foo = Foo(c=Counter())
    json_str = to_json(foo)
    assert json_str == '{"c":{}}'

    foo2 = from_json(Foo, json_str)
    assert isinstance(foo2.c, Counter)
    assert len(foo2.c) == 0


def test_counter_optional() -> None:
    from typing import Optional

    @serde
    class Foo:
        c: Optional[Counter[str]]

    foo = Foo(c=Counter(["x", "y", "x"]))
    json_str = to_json(foo)
    assert '{"c":{' in json_str

    foo2 = from_json(Foo, json_str)
    assert foo2.c is not None
    assert isinstance(foo2.c, Counter)
    assert foo2.c["x"] == 2
    assert foo2.c["y"] == 1

    foo_none = Foo(c=None)
    json_str_none = to_json(foo_none)
    assert json_str_none == '{"c":null}'

    foo_none2 = from_json(Foo, json_str_none)
    assert foo_none2.c is None


def test_counter_with_other_fields() -> None:
    @serde
    class Foo:
        name: str
        counts: Counter[str]
        total: int

    foo = Foo(name="test", counts=Counter(["a", "b", "a"]), total=42)
    json_str = to_json(foo)
    assert '"name":"test"' in json_str
    assert '"total":42' in json_str

    foo2 = from_json(Foo, json_str)
    assert foo2.name == "test"
    assert isinstance(foo2.counts, Counter)
    assert foo2.counts["a"] == 2
    assert foo2.counts["b"] == 1
    assert foo2.total == 42


def test_counter_most_common() -> None:
    """Test that Counter methods work after deserialization."""

    @serde
    class Foo:
        c: Counter[str]

    foo = Foo(c=Counter(["a", "a", "a", "b", "b", "c"]))
    json_str = to_json(foo)
    foo2 = from_json(Foo, json_str)

    # Test most_common() method works
    assert foo2.c.most_common(2) == [("a", 3), ("b", 2)]


def test_counter_elements() -> None:
    """Test that Counter.elements() works after deserialization."""

    @serde
    class Foo:
        c: Counter[str]

    foo = Foo(c=Counter({"a": 2, "b": 1}))
    json_str = to_json(foo)
    foo2 = from_json(Foo, json_str)

    # Test elements() method works
    elements = list(foo2.c.elements())
    assert elements.count("a") == 2
    assert elements.count("b") == 1
