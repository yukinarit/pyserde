# pyright: reportUndefinedVariable=false
# Pyright is pinned to an older Python and does not understand PEP 649 forward references.

"""
Tests for PEP 649 / PEP 749 deferred evaluation of annotations (Python 3.14+).

Unlike `test_lazy_type_evaluation.py`, this module intentionally does NOT use
`from __future__ import annotations`. On Python 3.14, annotations are compiled into an
`__annotate__` function and only evaluated on first access, so unquoted forward references
are legal at class definition time.
"""

import dataclasses
import enum
import typing
from typing import ClassVar

import pytest

from serde import SerdeError, deserialize, disabled, from_dict, serde, serialize, to_dict
from serde.compat import dataclass_fields
from serde.json import from_json, to_json

# Stop importing this module on Python < 3.14 because the classes below rely on PEP 649.
annotationlib = pytest.importorskip("annotationlib", reason="PEP 649 requires Python 3.14+")


class Status(enum.Enum):
    OK = "ok"
    ERR = "err"


@serde
class Leaf:
    i: int
    s: str
    status: Status


@serde
class Tree:
    leaf: Leaf
    leaves: list[Leaf]
    mapping: dict[str, Leaf]
    pair: tuple[int, Leaf]
    optional: Leaf | None = None


def test_deferred_annotations_resolve_to_real_types() -> None:
    for f in dataclass_fields(Tree):
        assert not isinstance(f.type, (str, annotationlib.ForwardRef))

    assert dataclasses.fields(Tree)[0].type is Leaf
    assert dataclasses.fields(Tree)[4].type == Leaf | None

    leaf = Leaf(1, "foo", Status.OK)
    tree = Tree(leaf, [leaf], {"k": leaf}, (2, leaf), leaf)
    leaf_dict = {"i": 1, "s": "foo", "status": "ok"}
    tree_dict = {
        "leaf": leaf_dict,
        "leaves": [leaf_dict],
        "mapping": {"k": leaf_dict},
        "pair": (2, leaf_dict),
        "optional": leaf_dict,
    }

    assert to_dict(tree) == tree_dict
    assert from_dict(Tree, tree_dict) == tree
    assert from_json(Tree, to_json(tree)) == tree


# `UndecoratedOwner` refers to `UndecoratedChild` before it is defined, without quotes.
class UndecoratedOwner:
    child: UndecoratedChild
    children: list[UndecoratedChild]
    optional: UndecoratedChild | None = None


@serde
class UndecoratedChild:
    i: int


def test_forward_reference_on_undecorated_class() -> None:
    # The class was created before `UndecoratedChild` existed; annotations are evaluated now.
    annotations = annotationlib.get_annotations(
        UndecoratedOwner, format=annotationlib.Format.FORWARDREF
    )
    assert annotations["child"] is UndecoratedChild

    serde(UndecoratedOwner)

    owner = UndecoratedOwner(UndecoratedChild(1), [UndecoratedChild(2)])  # type: ignore
    owner_dict = {"child": {"i": 1}, "children": [{"i": 2}], "optional": None}
    assert to_dict(owner) == owner_dict
    assert from_dict(UndecoratedOwner, owner_dict) == owner


@dataclasses.dataclass
class DataclassOwnerUnchecked:
    child: DataclassChild


@dataclasses.dataclass
class DataclassOwnerStrict:
    child: DataclassChild


@serde
class DataclassChild:
    i: int


def test_forward_reference_on_dataclass_type_check_disabled() -> None:
    # `dataclasses` evaluates annotations with `Format.FORWARDREF` on 3.14, so the field
    # type is a `ForwardRef` until pyserde resolves it.
    assert isinstance(dataclasses.fields(DataclassOwnerUnchecked)[0].type, annotationlib.ForwardRef)

    serialize(DataclassOwnerUnchecked, type_check=disabled)
    deserialize(DataclassOwnerUnchecked, type_check=disabled)

    assert dataclasses.fields(DataclassOwnerUnchecked)[0].type is DataclassChild

    owner = DataclassOwnerUnchecked(DataclassChild(10))
    assert to_dict(owner) == {"child": {"i": 10}}
    assert from_dict(DataclassOwnerUnchecked, {"child": {"i": 10}}) == owner


@pytest.mark.xfail(
    raises=RuntimeError,
    strict=True,
    reason="beartype iterates cls.__dict__ while Python 3.14 lazily inserts "
    "'__annotations_cache__' into it (dictionary changed size during iteration)",
)
def test_forward_reference_on_dataclass_type_check_strict() -> None:
    serialize(DataclassOwnerStrict)
    deserialize(DataclassOwnerStrict)

    owner = DataclassOwnerStrict(DataclassChild(10))
    assert to_dict(owner) == {"child": {"i": 10}}
    assert from_dict(DataclassOwnerStrict, {"child": {"i": 10}}) == owner


@dataclasses.dataclass
class LinkedNode:
    value: int
    next: LinkedNode | None = None
    children: list[LinkedNode] = dataclasses.field(default_factory=list)


def test_self_referencing_class() -> None:
    serde(LinkedNode)

    node = LinkedNode(1, LinkedNode(2), [LinkedNode(3)])
    node_dict = {
        "value": 1,
        "next": {"value": 2, "next": None, "children": []},
        "children": [{"value": 3, "next": None, "children": []}],
    }
    assert to_dict(node) == node_dict
    assert from_dict(LinkedNode, node_dict) == node


def test_local_classes_in_definition_order() -> None:
    @serde
    class Inner:
        i: int

    @serde
    class Outer:
        inner: Inner
        items: list[Inner]

    outer = Outer(Inner(1), [Inner(2)])
    outer_dict = {"inner": {"i": 1}, "items": [{"i": 2}]}
    assert to_dict(outer) == outer_dict
    assert from_dict(Outer, outer_dict) == outer


def test_unresolved_forward_reference_throws() -> None:
    # PEP 649: defining the class is fine, the annotation is never evaluated.
    class Unresolved:
        bar: DoesNotExist  # type: ignore # noqa: F821

    with pytest.raises(NameError):
        annotationlib.get_annotations(Unresolved)

    with pytest.raises(SerdeError, match="Failed to resolve type hints for Unresolved"):
        serde(Unresolved)


if typing.TYPE_CHECKING:
    from decimal import Decimal


class OnlyForTypeCheckers:
    d: Decimal


def test_type_checking_only_import_throws() -> None:
    with pytest.raises(SerdeError, match="Failed to resolve type hints for OnlyForTypeCheckers"):
        serde(OnlyForTypeCheckers)


@dataclasses.dataclass
class Base:
    a: int


def test_inheritance() -> None:
    @serde
    class DerivedNoAnnotations(Base):
        pass

    @serde
    class Derived(Base):
        b: Leaf | None = None

    assert to_dict(DerivedNoAnnotations(1)) == {"a": 1}
    assert from_dict(DerivedNoAnnotations, {"a": 1}) == DerivedNoAnnotations(1)

    leaf = Leaf(1, "foo", Status.ERR)
    derived_dict = {"a": 1, "b": {"i": 1, "s": "foo", "status": "err"}}
    assert to_dict(Derived(1, leaf)) == derived_dict
    assert from_dict(Derived, derived_dict) == Derived(1, leaf)


def test_class_var() -> None:
    @serde(serialize_class_var=True)
    class WithClassVar:
        a: int
        name: ClassVar[str] = "foo"

    assert to_dict(WithClassVar(1)) == {"a": 1, "name": "foo"}
    assert from_dict(WithClassVar, {"a": 1}) == WithClassVar(1)


def test_strict_type_check() -> None:
    @serde
    class Strict:
        leaf: Leaf

    with pytest.raises(SerdeError):
        Strict(1)  # type: ignore


def test_make_dataclass() -> None:
    Made = dataclasses.make_dataclass("Made", [("x", int), ("leaves", list[Leaf])])
    serde(Made)

    leaf = Leaf(1, "foo", Status.OK)
    made_dict = {"x": 1, "leaves": [{"i": 1, "s": "foo", "status": "ok"}]}
    assert to_dict(Made(1, [leaf])) == made_dict
    assert from_dict(Made, made_dict) == Made(1, [leaf])


def test_custom_annotate_function() -> None:
    # PEP 649/749: a class can provide annotations through `__annotate__` directly.
    class Annotated:
        pass

    def annotate(format: int) -> dict[str, typing.Any]:
        if format != annotationlib.Format.VALUE:
            raise NotImplementedError
        return {"x": int, "leaf": Leaf}

    Annotated.__annotate__ = annotate  # type: ignore
    serde(Annotated)

    leaf = Leaf(1, "foo", Status.OK)
    annotated_dict = {"x": 1, "leaf": {"i": 1, "s": "foo", "status": "ok"}}
    assert to_dict(Annotated(1, leaf)) == annotated_dict  # type: ignore
    assert from_dict(Annotated, annotated_dict) == Annotated(1, leaf)  # type: ignore
