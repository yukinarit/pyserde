from __future__ import annotations

from dataclasses import dataclass

from serde import serde
from serde.json import from_json, to_json
from typing import Type


@serde
@dataclass
class Foo:
    i: int
    s: str
    f: float
    b: bool

    def foo(self, cls: Type[Foo]) -> None:  # You can use "Foo" type before it's defined.
        print('foo')


def main() -> None:
    f = Foo(i=10, s='foo', f=100.0, b=True)
    print(f"Into Json: {to_json(f)}")

    s = '{"i": 10, "s": "foo", "f": 100.0, "b": true}'
    print(f"From Json: {from_json(Foo, s)}")

    f.foo(Foo)


if __name__ == '__main__':
    main()
