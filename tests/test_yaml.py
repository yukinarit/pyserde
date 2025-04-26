from serde import serde
from serde.yaml import to_yaml, from_yaml
from typing import Optional


def test_yaml_basics() -> None:
    @serde
    class Foo:
        v: Optional[int]

    f = Foo(10)
    assert "v: 10\n" == to_yaml(f)
    assert f == from_yaml(Foo, "v: 10\n")

    @serde
    class Bar:
        v: set[int]

    b = Bar({1, 2, 3})
    assert "v:\n- 1\n- 2\n- 3\n" == to_yaml(b)
    assert b == from_yaml(Bar, "v:\n- 1\n- 2\n- 3\n")


def test_skip_none() -> None:
    @serde
    class Foo:
        a: int
        b: Optional[int]

    f = Foo(10, 100)
    assert (
        to_yaml(f, skip_none=True)
        == """\
a: 10
b: 100
"""
    )

    f = Foo(10, None)
    assert (
        to_yaml(f, skip_none=True)
        == """\
a: 10
"""
    )
