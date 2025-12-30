import pytest

from serde import SerdeError, field, from_dict, from_tuple, serde, to_dict, to_tuple
from serde.json import from_json, to_json


def test_transparent_primitive() -> None:
    @serde(transparent=True)
    class IntWrap:
        value: int

    assert to_dict(IntWrap(5)) == 5
    assert to_json(IntWrap(5)) == "5"
    assert from_dict(IntWrap, 5) == IntWrap(5)  # type: ignore[arg-type]
    assert from_json(IntWrap, "5") == IntWrap(5)


def test_transparent_nested_dataclass() -> None:
    @serde
    class Inner:
        i: int
        s: str

    @serde(transparent=True)
    class Wrap:
        inner: Inner

    w = Wrap(Inner(1, "x"))
    assert to_json(w) == '{"i":1,"s":"x"}'
    assert to_tuple(w) == (1, "x")
    assert from_json(Wrap, '{"i":1,"s":"x"}') == w
    assert from_tuple(Wrap, (1, "x")) == w


def test_transparent_allows_skipped_init_false_fields() -> None:
    @serde(transparent=True)
    class WrapWithCache:
        value: int
        cache: int = field(default=0, init=False, skip=True)

    assert to_json(WrapWithCache(10)) == "10"
    assert from_json(WrapWithCache, "10") == WrapWithCache(10)


def test_transparent_validation() -> None:
    with pytest.raises(SerdeError):

        @serde(transparent=True)
        class Bad:
            a: int
            b: int
