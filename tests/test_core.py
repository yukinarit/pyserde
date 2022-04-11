from dataclasses import dataclass, is_dataclass

from serde.core import should_impl_dataclass


def test_should_impl_dataclass():
    @dataclass
    class Base:
        a: int

    class Derived(Base):
        b: int

    is_dataclass(Base)
    is_dataclass(Derived)
    assert not should_impl_dataclass(Base)
    assert should_impl_dataclass(Derived)

    @dataclass
    class Base:
        pass

    class Derived(Base):
        pass

    is_dataclass(Base)
    is_dataclass(Derived)
    assert not should_impl_dataclass(Base)
    assert not should_impl_dataclass(Derived)

    @dataclass
    class Base:
        pass

    class Derived(Base):
        b: int

    is_dataclass(Base)
    is_dataclass(Derived)
    assert not should_impl_dataclass(Base)
    assert should_impl_dataclass(Derived)

    class Base:
        a: int

    @dataclass
    class Derived(Base):
        b: int

    is_dataclass(Base)
    is_dataclass(Derived)
    assert should_impl_dataclass(Base)
    assert not should_impl_dataclass(Derived)

    class Base:
        a: int

    class Derived(Base):
        b: int

    is_dataclass(Base)
    is_dataclass(Derived)
    assert should_impl_dataclass(Base)
    assert should_impl_dataclass(Derived)

    @dataclass
    class Base1:
        a: int

    @dataclass
    class Base2:
        a: int

    class Derived(Base1, Base2):
        c: int

    is_dataclass(Base)
    is_dataclass(Derived)
    assert not should_impl_dataclass(Base1)
    assert not should_impl_dataclass(Base2)
    assert should_impl_dataclass(Derived)
