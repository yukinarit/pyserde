from dataclasses import dataclass
from decimal import Decimal

import pytest

from serde import deserialize, serialize
from tests.test_basics import format_dict, format_json, format_toml, format_yaml


@deserialize
@serialize
@dataclass
class Foo:
    d: Decimal


@pytest.mark.parametrize('se,de', format_json + format_yaml + format_toml)  # type: ignore
def test_decimal(se, de):
    f = Foo(d=Decimal('0.1'))
    assert f == de(Foo, se(f))

    f = Foo(d=Decimal(0.1))
    assert f == de(Foo, se(f))
