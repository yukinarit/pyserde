import sys
import typing

import pytest

from serde import serde, field, from_dict, to_dict

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
def test_pep695_type_alias_as_top_level_union() -> None:
    # A `type T = Foo | Bar` alias passed as the top-level `cls` must be treated
    # as the union it aliases, not silently serialized without tagging. See #753.
    ns: dict[str, object] = {"serde": serde}
    exec(
        """
@serde
class Foo:
    a: int = 123

@serde
class Dummy:
    b: int = 456

type T = Foo | Dummy
""",
        ns,
    )
    Foo = typing.cast(type, ns["Foo"])
    Dummy = typing.cast(type, ns["Dummy"])
    T = ns["T"]

    value = Foo()
    expected = to_dict(value, c=typing.cast(type, Foo | Dummy))
    assert expected == {"Foo": {"a": 123}}
    # the alias must produce the same tagged output as the real union ...
    assert to_dict(value, c=typing.cast(type, T)) == expected
    # ... and round-trip back through the alias.
    assert value == from_dict(typing.cast(type, T), to_dict(value, c=typing.cast(type, T)))


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


@pytest.mark.skipif(sys.version_info < (3, 12), reason=_PEP695_REASON)
def test_pep695_recursive_type_alias_skipped_field() -> None:
    ns: dict[str, object] = {
        "field": field,
        "from_dict": from_dict,
        "serde": serde,
        "to_dict": to_dict,
    }
    exec(
        """
type NestedDict = dict[str, NestedDict | int]

@serde
class Config:
    name: str
    internal: NestedDict | None = field(default=None, skip=True)
""",
        ns,
    )
    Config = typing.cast(type, ns["Config"])

    value = Config(name="test")
    assert {"name": "test"} == to_dict(value)
    assert value == from_dict(Config, {"name": "test"})
