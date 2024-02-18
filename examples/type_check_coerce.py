from dataclasses import dataclass
from typing import Dict, List, Optional

from serde import coerce, serde
from serde.json import from_json, to_json


@serde(type_check=coerce)
@dataclass
class Bar:
    e: int


@serde(type_check=coerce)
@dataclass
class Foo:
    a: int
    b: List[int]
    c: List[Dict[str, int]]
    d: Optional[Bar] = None


def main() -> None:
    f = Foo(a="1", b=[True], c=[{10: 1.0}])  # type: ignore
    print(f"Into Json: {to_json(f)}")

    s = '{"a": "1", "b": [false], "c": [{"10": 1.0}], "d": {"e": "100"}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
