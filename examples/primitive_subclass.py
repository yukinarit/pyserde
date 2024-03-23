from serde.json import from_json, to_json
from serde import field, serde


class Id(str):
    def __str__(self) -> str:
        return "ID " + self


@serde
class Foo:
    a: Id = field(default_factory=Id)
    b: dict[Id, float] = field(default_factory=dict)
    c: list[Id] = field(default_factory=list)


def main() -> None:
    f = Foo(Id("a"), {Id("b"): 1.0}, [Id("c")])
    print(f)
    print(type(f.a))
    print(type(list(f.b.keys())[0]))
    print(type(f.c[0]))

    d = to_json(f)
    print(d)

    ff = from_json(Foo, d)
    print(ff)
    print(type(ff.a))
    print(type(list(ff.b.keys())[0]))
    print(type(ff.c[0]))


if __name__ == "__main__":
    main()
