import pytest

import serde as serde_pkg
from serde import serde
from serde.yaml import to_yaml, from_yaml


def test_yaml_basics() -> None:
    @serde
    class Foo:
        v: int | None

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
        b: int | None

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


def test_coerce_numbers_yaml() -> None:
    @serde
    class Foo:
        value: float

    foo = from_yaml(Foo, "value: 1\n")
    assert foo.value == 1.0

    @serde
    class Bar:
        values: list[float]

    bar = from_yaml(Bar, 'values:\n- 1\n- "2"\n')
    assert bar.values == [1.0, 2.0]

    baz = from_yaml(Foo, "value: 1e-3\n")
    assert baz.value == 0.001

    with pytest.raises(serde_pkg.SerdeError):
        from_yaml(Foo, "value: 1\n", coerce_numbers=False)


def test_yaml_numbers_with_union() -> None:
    @serde
    class Foo:
        value: float | int

    assert from_yaml(Foo, "value: 1\n").value == 1.0

    with pytest.raises(serde_pkg.SerdeError):
        from_yaml(Foo, 'value: "1"\n')

    @serde
    class Bar:
        value: int | float

    assert from_yaml(Bar, "value: 1\n").value == 1

    with pytest.raises(serde_pkg.SerdeError):
        from_yaml(Bar, 'value: "1"\n')
