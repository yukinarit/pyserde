from dataclasses import dataclass
from typing import Dict, List

from serde import SerdeError, Strict, serde
from serde.json import from_json, to_json


@serde
@dataclass
class Foo:
    a: int
    b: List[int]
    c: List[Dict[str, int]]


def main():
    f = Foo(a=1.0, b=[1.0], c=[{"k": 1.0}])
    try:
        print(f"Into Json: {to_json(f, type_check=Strict)}")
    except Exception as e:
        print(e)

    s = '{"a": 1, "b": [1], "c": [{"k": 1.0}]}'
    try:
        print(f"From Json: {from_json(Foo, s, type_check=Strict)}")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
