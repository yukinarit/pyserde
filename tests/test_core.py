import pytest
import enum

from .data import Int


def assert_raises(cls, f):
    with pytest.raises(cls):
        f()


class IE(enum.IntEnum):
    A = 1


class E(enum.Enum):
    A = 1
    B = "B"


class C:
    pass


def test_cast_int():
    assert 1 == int(1)
    assert 1 == int('1')
    assert 1 == int(1.5)
    assert 1 == int(True)
    assert 0 == int(False)
    assert 1 == int(IE.A)
    assert_raises(TypeError, lambda: int(C()))
    assert_raises(TypeError, lambda: int(E.A))
    assert_raises(TypeError, lambda: int([]))
    assert_raises(TypeError, lambda: int({}))
    assert_raises(ValueError, lambda: int('1.0'))
    assert_raises(ValueError, lambda: int('True'))
    assert_raises(ValueError, lambda: int('true'))


def test_cast_float():
    assert 1 == float(1)
    assert 1 == float('1')
    assert 1.5 == float(1.5)
    assert 1 == float(True)
    assert 0.0 == float(False)
    assert 1.0 == float(IE.A)
    assert_raises(TypeError, lambda: float(C()))
    assert_raises(TypeError, lambda: float(E.A))
    assert_raises(TypeError, lambda: float([]))
    assert_raises(TypeError, lambda: float({}))
    assert_raises(ValueError, lambda: float('True'))
    assert_raises(ValueError, lambda: float('true'))


def test_cast_str():
    assert "1" == str(1)
    assert "1" == str('1')
    assert "1.5" == str(1.5)
    assert "True" == str(True)
    assert "False" == str(False)
    assert "IE.A" == str(IE.A)
    assert "E.A" == str(E.A)
    assert "[]" == str([])
    assert "{}" == str({})


def test_cast_bool():
    assert bool(1)
    assert bool('1')
    assert bool(1.5)
    assert bool(True)
    assert not bool(False)
    assert bool(IE.A)
    assert bool(E.A)
    assert not bool([])
    assert not bool({})


def test_cast_intenum():
    assert 1 == IE(1)
    assert IE.A == IE(IE.A)
    assert IE.A == IE(1)
    assert IE.A == IE(True)
    assert IE.A == IE(1.0)
    assert_raises(ValueError, lambda: IE(False))
    assert_raises(ValueError, lambda: IE(C()))
    assert_raises(ValueError, lambda: IE(E.A))
    assert_raises(ValueError, lambda: IE([]))
    assert_raises(ValueError, lambda: IE({}))
    assert_raises(ValueError, lambda: IE('1.0'))
    assert_raises(ValueError, lambda: IE('True'))
    assert_raises(ValueError, lambda: IE('true'))


def test_cast_enum():
    assert E.A == E(IE.A)
    assert E.A == E(1)
    assert E.A == E(True)
    assert E.A == E(1.0)
    assert_raises(ValueError, lambda: E(False))
    assert_raises(ValueError, lambda: E(C()))
    assert_raises(ValueError, lambda: E([]))
    assert_raises(ValueError, lambda: E({}))
    assert_raises(ValueError, lambda: E('1.0'))
    assert_raises(ValueError, lambda: E('True'))
    assert_raises(ValueError, lambda: E('true'))


def test_cast_class():
    assert Int(1) == Int(1)
    assert Int(1) != Int('1')
    assert Int(1) != Int(1.5)
    assert Int(1) == Int(True)
    assert Int(0) == Int(False)
    assert Int(1) == Int(IE.A)
