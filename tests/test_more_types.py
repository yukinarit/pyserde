from dataclasses import dataclass
from decimal import Decimal

import pytest

from serde import deserialize, serialize
from tests.test_basics import all_formats


@deserialize
@serialize
@dataclass
class Foo:
    d: Decimal


@pytest.mark.parametrize('se,de', all_formats)
def test_decimal(se, de):
    f = Foo(d=Decimal('0.1'))
    assert f == de(Foo, se(f))

    f = Foo(d=Decimal(0.1))
    assert f == de(Foo, se(f))
