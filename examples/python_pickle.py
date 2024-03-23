from serde import serde
from serde.pickle import from_pickle, to_pickle


@serde
class Foo:
    i: int
    s: str
    f: float
    b: bool


def main() -> None:
    f = Foo(i=10, s="foo", f=100.0, b=True)
    bin = to_pickle(f)
    print("Into Pickle: ", bin)
    print(f"From Pickle: {from_pickle(Foo, bin)}")


if __name__ == "__main__":
    main()
