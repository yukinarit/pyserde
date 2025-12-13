from serde import serde
from serde.toml import to_toml, from_toml
import pytest


def test_toml_basics() -> None:
    @serde
    class Foo:
        v: int | None

    f = Foo(10)
    assert "v = 10\n" == to_toml(f)
    assert f == from_toml(Foo, "v = 10\n")

    @serde
    class Bar:
        v: set[int]

    toml_literal = """\
v = [
    1,
    2,
    3,
]
"""
    b = Bar({1, 2, 3})
    assert toml_literal == to_toml(b)
    assert b == from_toml(Bar, toml_literal)


def test_skip_none() -> None:
    @serde
    class Foo:
        a: int
        b: int | None

    f = Foo(10, 100)
    assert (
        to_toml(f)
        == """\
a = 10
b = 100
"""
    )

    f = Foo(10, None)
    assert (
        to_toml(f)
        == """\
a = 10
"""
    )


def test_skip_none_container_not_supported_yet() -> None:
    @serde
    class Foo:
        a: int
        b: list[int | None]

    f = Foo(10, [100, None])
    with pytest.raises(TypeError):
        to_toml(f)
