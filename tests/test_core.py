from dataclasses import dataclass, is_dataclass

from serde.core import should_impl_dataclass


def test_should_impl_dataclass() -> None:
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
    class Base2:
        pass

    class Derived2(Base2):
        pass

    is_dataclass(Base2)
    is_dataclass(Derived2)
    assert not should_impl_dataclass(Base2)
    assert not should_impl_dataclass(Derived2)

    @dataclass
    class Base3:
        pass

    class Derived3(Base3):
        b: int

    is_dataclass(Base3)
    is_dataclass(Derived3)
    assert not should_impl_dataclass(Base3)
    assert should_impl_dataclass(Derived3)

    class Base4:
        a: int

    @dataclass
    class Derived4(Base4):
        b: int

    is_dataclass(Base4)
    is_dataclass(Derived4)
    assert should_impl_dataclass(Base4)
    assert not should_impl_dataclass(Derived4)

    class Base5:
        a: int

    class Derived5(Base5):
        b: int

    is_dataclass(Base5)
    is_dataclass(Derived5)
    assert should_impl_dataclass(Base5)
    assert should_impl_dataclass(Derived5)

    @dataclass
    class Base1:
        a: int

    @dataclass
    class Base6:
        a: int

    class Derived6(Base1, Base6):
        c: int

    is_dataclass(Base1)
    is_dataclass(Derived6)
    assert not should_impl_dataclass(Base1)
    assert not should_impl_dataclass(Base6)
    assert should_impl_dataclass(Derived6)
