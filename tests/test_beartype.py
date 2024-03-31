import pytest
from beartype import beartype
from beartype.roar import BeartypeCallHintParamViolation
from dataclasses import dataclass
from serde import serde, SerdeError


def test_raises_serde_error_instead_of_beartype_error() -> None:
    @serde
    class Foo:
        v: int

    with pytest.raises(SerdeError):
        Foo("foo")  # type: ignore


def test_raises_beartype_error_if_beartype_decorated() -> None:
    # If a class already has beartype, pyserde cannot set custom validation error.
    @serde
    @beartype
    @dataclass
    class Foo:
        v: int

    with pytest.raises(BeartypeCallHintParamViolation):
        Foo("foo")  # type: ignore
