import sys
from dataclasses import dataclass, make_dataclass
import typing

import pytest

from serde import SerdeError, serde, field, from_dict, to_dict, from_tuple, to_tuple
from serde.core import disabled
from serde.se import serialize
from serde.de import deserialize
from serde.json import from_json, to_json

try:
    from typing import TypeAliasType
except ImportError:
    from typing_extensions import TypeAliasType


_PEP695_REASON = "PEP 695 `type` statement requires Python 3.12+."

# `typing.TypeAliasType` aliases must be defined at module or class scope.
Bar = TypeAliasType("Bar", list[int])
Baz = TypeAliasType("Baz", Bar)
Number = TypeAliasType("Number", typing.Annotated[int, "metadata"])


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


@pytest.mark.skipif(sys.version_info < (3, 12), reason=_PEP695_REASON)
def test_pep695_generic_type_alias() -> None:
    ns: dict[str, object] = {"serde": serde}
    exec(
        """
type Point[T] = tuple[T, T]
type Polygon[T] = tuple[Point[T], ...]

@serde
class Figure:
    name: str
    polygon: Polygon[float]
""",
        ns,
    )
    FigureClass = typing.cast(type, ns["Figure"])

    value = FigureClass("test", ((0.0, 0.0), (1.0, 1.73), (-1.0, 1.73)))
    assert value == from_dict(FigureClass, to_dict(value))


@pytest.mark.skipif(sys.version_info < (3, 12), reason=_PEP695_REASON)
def test_pep695_type_alias_literal() -> None:
    ns: dict[str, object] = {"serde": serde, "Literal": typing.Literal}
    exec(
        """
type Mode = Literal["trailing", "mean-reversion"]

@serde
class Foo:
    value: Mode
""",
        ns,
    )
    FooClass = typing.cast(type, ns["Foo"])

    value = FooClass("trailing")
    assert {"value": "trailing"} == to_dict(value)
    assert value == from_dict(FooClass, {"value": "trailing"})


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


@pytest.mark.skipif(sys.version_info < (3, 12), reason=_PEP695_REASON)
def test_pep695_annotated_type_alias() -> None:
    ns: dict[str, object] = {"serde": serde}
    exec(
        """
from typing import Annotated
from beartype.vale import Is

type Natural = Annotated[int, Is[lambda x: 0 <= x]]

@serde
class User:
    id: Natural
    name: str
""",
        ns,
    )
    User = typing.cast(type, ns["User"])
    value = User(0, "John Doe")
    assert to_dict(value) == {"id": 0, "name": "John Doe"}
    assert from_dict(User, to_dict(value)) == value
    assert from_json(User, to_json(value)) == value
    assert from_tuple(User, to_tuple(value)) == value
    # Code generation must not erase the original validator annotation.
    assert typing.get_type_hints(User)["id"] is ns["Natural"]
    with pytest.raises(SerdeError):
        from_dict(User, {"id": -1, "name": "John Doe"})


# Use the native alias for strict end-to-end tests. Backport code generation is
# covered in test_se/test_de and discovery in test_compat, without requiring
# Beartype to support a distinct typing_extensions.TypeAliasType implementation.
@pytest.mark.parametrize("value", [1, "text"])
def test_annotated_type_alias_union(value: int | str) -> None:
    alias_type: typing.Any = TypeAliasType
    alias = alias_type("Choice", typing.Annotated[int | str, "metadata"])
    Item = serde(make_dataclass("Item", [("value", alias)]))

    item = Item(value)
    assert from_dict(Item, to_dict(item)) == item
    assert from_json(Item, to_json(item)) == item
    assert from_tuple(Item, to_tuple(item)) == item


def test_annotated_type_alias_literal() -> None:
    alias_type: typing.Any = TypeAliasType
    alias = alias_type("Mode", typing.Annotated[typing.Literal["a", "b"], "metadata"])
    Item = serde(make_dataclass("Item", [("value", alias)]))

    item = Item("a")
    assert from_dict(Item, to_dict(item)) == item
    assert from_json(Item, to_json(item)) == item
    assert from_tuple(Item, to_tuple(item)) == item
    with pytest.raises(SerdeError):
        from_dict(Item, {"value": "c"})


def test_annotated_type_alias_nested_dataclass() -> None:
    alias_type: typing.Any = TypeAliasType

    @dataclass
    class Child:
        value: int

    child = alias_type("AnnotatedChild", typing.Annotated[Child, "metadata"])
    children = alias_type("Children", typing.Annotated[list[child], "metadata"])
    alias = alias_type("Alias", children)
    Item = serde(make_dataclass("Item", [("values", alias)]))

    item = Item([Child(1), Child(2)])
    assert to_dict(item) == {"values": [{"value": 1}, {"value": 2}]}
    assert from_dict(Item, to_dict(item)) == item
    assert from_json(Item, to_json(item)) == item
    assert from_tuple(Item, to_tuple(item)) == item


def test_annotated_type_alias_field_options() -> None:
    alias_type: typing.Any = TypeAliasType
    alias = alias_type("Number", typing.Annotated[int, "metadata"])
    numbers = alias_type("Numbers", list[alias])

    Item = serde(
        make_dataclass(
            "Item",
            [
                ("value", alias, field(default=1, rename="renamed")),
                ("values", numbers, field(default_factory=list)),
                (
                    "custom",
                    alias,
                    field(
                        default=2,
                        serializer=lambda value: str(value),
                        deserializer=lambda value: int(value),
                    ),
                ),
                ("ignored", alias, field(default=3, skip=True)),
            ],
        )
    )

    item = Item()
    assert to_dict(item) == {"renamed": 1, "values": [], "custom": "2"}
    assert from_dict(Item, {}) == item
    assert from_dict(Item, to_dict(item)) == item
    assert from_json(Item, to_json(item)) == item
    assert from_tuple(Item, to_tuple(item)) == item
    assert Item.__dataclass_fields__["value"].metadata["serde_rename"] == "renamed"
    assert typing.get_type_hints(Item)["value"] is alias


@pytest.mark.parametrize("decorator", [serialize, deserialize])
def test_annotated_type_alias_standalone(decorator: typing.Any) -> None:
    @decorator
    class Item:
        value: Number

    item = Item(1)
    if decorator is serialize:
        assert to_dict(item) == {"value": 1}
        assert to_tuple(item) == (1,)
    else:
        assert from_dict(Item, {"value": 1}) == item
        assert from_tuple(Item, (1,)) == item


@pytest.mark.parametrize("metadata", [{"description": "value"}, ["metadata"]])
def test_annotated_type_alias_unhashable_metadata(metadata: typing.Any) -> None:
    class Aliases:
        Number = TypeAliasType("Number", typing.Annotated[int, metadata])

    # Beartype cannot validate aliases containing unhashable metadata.
    @serde(type_check=disabled)
    class Item:
        value: Aliases.Number

    item = Item(1)
    assert from_dict(Item, to_dict(item)) == item
    assert from_json(Item, to_json(item)) == item
    assert from_tuple(Item, to_tuple(item)) == item
    assert typing.get_args(Aliases.Number.__value__)[1] is metadata
