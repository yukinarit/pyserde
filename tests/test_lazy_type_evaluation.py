from __future__ import annotations  # this is the line this test file is all about

import dataclasses
from enum import Enum
from typing import List, Tuple

import pytest

from serde import SerdeError, deserialize, from_dict, serde, serialize, to_dict
from serde.compat import dataclass_fields


class Status(Enum):
    OK = "ok"
    ERR = "err"


@serde
class A:
    a: int
    b: Status
    c: List[str]


@serde
class B:
    a: A
    b: Tuple[str, A]
    c: Status


# only works with global classes
def test_serde_with_lazy_type_annotations():
    a = A(1, Status.ERR, ["foo"])
    a_dict = {"a": 1, "b": "err", "c": ["foo"]}

    assert a == from_dict(A, a_dict)
    assert a_dict == to_dict(a)

    b = B(a, ("foo", a), Status.OK)
    b_dict = {"a": a_dict, "b": ("foo", a_dict), "c": "ok"}

    assert b == from_dict(B, b_dict)
    assert b_dict == to_dict(b)


# test_forward_reference_works currently only works with global visible classes
@dataclasses.dataclass
class ForwardReferenceFoo:
    # this is not a string forward reference because we use PEP 563 (see 1st line of this file)
    bar: ForwardReferenceBar


@serde
class ForwardReferenceBar:
    i: int


# assert type is str
assert 'ForwardReferenceBar' == dataclasses.fields(ForwardReferenceFoo)[0].type

# setup pyserde for Foo after Bar becomes visible to global scope
deserialize(ForwardReferenceFoo)
serialize(ForwardReferenceFoo)

# now the type really is of type Bar
assert ForwardReferenceBar == dataclasses.fields(ForwardReferenceFoo)[0].type
assert ForwardReferenceBar == next(dataclass_fields(ForwardReferenceFoo)).type


# verify usage works
def test_forward_reference_works():
    h = ForwardReferenceFoo(bar=ForwardReferenceBar(i=10))
    h_dict = {"bar": {"i": 10}}

    assert to_dict(h) == h_dict
    assert from_dict(ForwardReferenceFoo, h_dict) == h


# trying to use forward reference normally will throw
def test_unresolved_forward_reference_throws():
    with pytest.raises(SerdeError) as e:

        @serde
        class UnresolvedForwardFoo:
            bar: UnresolvedForwardBar

        @serde
        class UnresolvedForwardBar:
            i: int

    assert "Failed to resolve type hints for UnresolvedForwardFoo" in str(e)


# trying to use string forward reference will throw
def test_string_forward_reference_throws():
    with pytest.raises(SerdeError) as e:

        @serde
        class UnresolvedStringForwardFoo:
            # string forward references are not compatible with PEP 563 and will throw
            bar: 'UnresolvedStringForwardBar'

        @serde
        class UnresolvedStringForwardBar:
            i: int

    # message is different between <= 3.8 & >= 3.9
    assert "Failed to resolve " in str(e.value)
