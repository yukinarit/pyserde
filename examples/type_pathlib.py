import pathlib

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    p: pathlib.Path


def main() -> None:
    foo = Foo(pathlib.Path("foo/bar/baz.txt"))
    print(f"Into Json: {to_json(foo)}")

    s = '{"p": "foo/bar/baz.txt"}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
