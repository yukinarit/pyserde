from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import pytest

from serde import deserialize, serialize
from tests.test_basics import format_json, format_toml, format_yaml


@deserialize
@serialize
@dataclass
class Foo:
    d: Decimal
    d2: Decimal = Decimal('10.0')


@deserialize
@serialize
@dataclass
class Bar:
    p: Path
    p2: Path = Path('/etc')


@pytest.mark.parametrize('se,de', format_json + format_yaml + format_toml)  # type: ignore
def test_decimal(se, de):
    f = Foo(d=Decimal('0.1'))
    assert f == de(Foo, se(f))

    f = Foo(d=Decimal(0.1))
    ff = de(Foo, se(f))
    assert f == ff
    assert f.d == Decimal(0.1)
    assert f.d2 == Decimal(10.0)


@pytest.mark.parametrize('se,de', format_json + format_yaml + format_toml)  # type: ignore
def test_path(se, de):
    f = Bar(p=Path('/tmp'))
    ff = de(Bar, se(f))
    assert f == ff
    assert Path('/tmp') == ff.p
    assert Path('/etc') == ff.p2
