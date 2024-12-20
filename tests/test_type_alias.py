from serde import serde, from_dict, to_dict


type S = str


def test_pep695_type_alias() -> None:

    @serde
    class Foo:
        s: S

    f = Foo("foo")
    assert f == from_dict(Foo, to_dict(f))


@serde
class Bar:
    a: int


@serde
class Baz:
    b: int


type BarBaz = Bar | Baz


def test_pep695_type_alias_union() -> None:
    @serde
    class Foo:
        barbaz: BarBaz

    f = Foo(Baz(10))
    assert f == from_dict(Foo, to_dict(f))
