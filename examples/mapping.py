from collections import UserDict
from collections.abc import Mapping, MutableMapping
from types import MappingProxyType

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    m: Mapping[str, int]
    mm: MutableMapping[str, int]


def main() -> None:
    proxy: Mapping[str, int] = MappingProxyType({"a": 1, "b": 2})
    userdict: MutableMapping[str, int] = UserDict({"c": 3, "d": 4})

    foo = Foo(m=proxy, mm=userdict)
    print(f"Into Json: {to_json(foo)}")  # -> {"m":{"a":1,"b":2},"mm":{"c":3,"d":4}}

    s = '{"m":{"a":1,"b":2},"mm":{"c":3,"d":4}}'
    print(f"From Json: {from_json(Foo, s)}")  # -> Foo(m={'a': 1, 'b': 2}, mm={'c': 3, 'd': 4})


if __name__ == "__main__":
    main()
