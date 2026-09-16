"""
Static typing regression tests for the PEP 747 `TypeForm` overloads.

`assert_type` is a no-op at runtime, so these run as ordinary pytest tests while the
real assertions are made by pyright (see `[tool.pyright] include` in pyproject.toml).
Without them, a refactor could silently collapse the `TypeForm[T]` overloads back to
the `Any` fallback and every runtime test would still pass.
"""

from typing import Any, Optional, TypeVar, Union, assert_type

from serde import from_dict, from_tuple, serde
from serde.core import InternalTagging, Untagged
from serde.json import from_json, to_json

T = TypeVar("T")


@serde
class Foo:
    i: int


@serde
class Bar:
    s: str


def test_plain_class() -> None:
    assert_type(from_json(Foo, '{"i": 10}'), Foo)
    assert_type(from_dict(Foo, {"i": 10}), Foo)
    assert_type(from_tuple(Foo, (10,)), Foo)


def test_generic_alias() -> None:
    assert_type(from_json(list[Foo], '[{"i": 10}]'), list[Foo])
    assert_type(from_json(dict[str, Foo], '{"a": {"i": 10}}'), dict[str, Foo])
    assert_type(from_json(tuple[Foo, ...], '[{"i": 10}]'), tuple[Foo, ...])
    assert_type(from_dict(list[Foo], [{"i": 10}]), list[Foo])


def test_optional() -> None:
    assert_type(from_json(Foo | None, '{"i": 10}'), Union[Foo, None])
    assert_type(from_json(Optional[Foo], '{"i": 10}'), Optional[Foo])


def test_union() -> None:
    s = to_json(Bar("bar"), cls=Union[Foo, Bar])
    assert_type(from_json(Foo | Bar, s), Union[Foo, Bar])
    assert_type(from_json(Union[Foo, Bar], s), Union[Foo, Bar])


def test_type_var_forwarding() -> None:
    """The common downstream pattern: forwarding a `type[T]` variable."""

    def load(cls: type[T], s: str) -> T:
        return from_json(cls, s)

    assert_type(load(Foo, '{"i": 10}'), Foo)


def test_tagging_instances_fall_back_to_any() -> None:
    """Tagging instances are objects, not type expressions, so they keep hitting
    the trailing `Any` overload."""
    s = to_json(Bar("bar"), cls=Untagged(Foo | Bar))
    assert_type(from_json(Untagged(Foo | Bar), s), Any)

    s = to_json(Bar("bar"), cls=InternalTagging("type", Foo | Bar))
    assert_type(from_json(InternalTagging("type", Foo | Bar), s), Any)
