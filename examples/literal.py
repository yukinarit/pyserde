from serde.compat import SerdeError
from typing import Literal

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    i: Literal[1, 2]
    s: Literal["a", "b"]


def main() -> None:
    f = Foo(1, "a")
    print(f"Into Json: {to_json(f)}")

    s = '{"i": 2, "s": "b"}'
    print(f"From Json: {from_json(Foo, s)}")

    t = '{"i": 3, "s": "a"}'
    try:
        from_json(Foo, t)
    except SerdeError as err:
        print(f"Cannot parse '{t}' as Foo: {err}")

    u = '{"i": 2, "s": "A"}'
    try:
        from_json(Foo, u)
    except SerdeError as err:
        print(f"Cannot parse '{u}' as Foo: {err}")


if __name__ == "__main__":
    main()
