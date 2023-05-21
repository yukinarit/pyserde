from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, List, Optional

from serde import serde
from serde.json import from_json, to_json


@serde
@dataclass
class Bar:
    v: Optional[int] = None


@serde
@dataclass
class Foo:
    a: DefaultDict[str, List[int]]
    b: DefaultDict[str, int]
    c: DefaultDict[str, Bar]


def main() -> None:
    a: DefaultDict[str, List[int]] = defaultdict(list)
    a["a"].append(1)
    b: DefaultDict[str, int] = defaultdict(int)
    b["b"]
    c: DefaultDict[str, Bar] = defaultdict(Bar)
    c["c"].v = 10

    f = Foo(a, b, c)
    print(f"Into Json: {to_json(f)}")

    s = '{"a": {"a": [1, 2]}, "b": {"b": 10}, "c": {"c": {}}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
