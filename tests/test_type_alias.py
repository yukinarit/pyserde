import sys
import typing

import pytest

from serde import serde, from_dict, to_dict


try:
    from typing import TypeAliasType
except ImportError:  # pragma: no cover
    from typing_extensions import TypeAliasType


_PEP695_REASON = "PEP 695 `type` statement requires Python 3.12+."

# `typing.TypeAliasType` aliases must be defined at module or class scope.
Bar = TypeAliasType("Bar", list[int])
Baz = TypeAliasType("Baz", Bar)


@pytest.mark.skipif(sys.version_info < (3, 12), reason=_PEP695_REASON)
def test_pep695_type_alias() -> None:
    ns: dict[str, object] = {"serde": serde}
    exec(
        """
type Foo = str

@serde
class Bar:
    s: Foo
""",
        ns,
    )
    BarClass = typing.cast(type, ns["Bar"])

    value = BarClass("foo")
    assert value == from_dict(BarClass, to_dict(value))


@pytest.mark.skipif(sys.version_info < (3, 12), reason=_PEP695_REASON)
def test_pep695_type_alias_union() -> None:
    ns: dict[str, object] = {"serde": serde}
    exec(
        """
type Foo = int | str

@serde
class Bar:
    x: Foo
""",
        ns,
    )
    BarClass = typing.cast(type, ns["Bar"])

    value = BarClass(10)
    assert value == from_dict(BarClass, to_dict(value))


@pytest.mark.skipif(sys.version_info < (3, 12), reason=_PEP695_REASON)
def test_pep695_type_alias_variable_tuple() -> None:
    ns: dict[str, object] = {"serde": serde}
    exec(
        """
type Foo = tuple[float, float]
type Bar = tuple[Foo, ...]

@serde(rename_all="camelcase")
class Baz:
    name: str
    bar: Bar
""",
        ns,
    )
    BazClass = typing.cast(type, ns["Baz"])

    value = BazClass("test", ((0.0, 0.0), (1.0, 1.73)))
    assert value == from_dict(BazClass, to_dict(value))


def test_typealiastype_list() -> None:
    @serde
    class Foo:
        nums: Bar

    value = Foo([1, 2, 3])
    assert value == from_dict(Foo, to_dict(value))


def test_typealiastype_nested_alias() -> None:
    @serde(rename_all="camelcase")
    class Foo:
        name: str
        baz: Baz

    value = Foo("alias", [1, 2, 3])
    assert value == from_dict(Foo, to_dict(value))
