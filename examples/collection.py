import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

from serde import serde
from serde.json import from_json, to_json

PY39 = sys.version_info[:3] >= (3, 9, 0)


@serde
@dataclass
class Foo:
    a: List[str]
    b: Tuple[str, bool]
    c: Dict[str, List[int]]


# For python >= 3.9, you can use [PEP585](https://www.python.org/dev/peps/pep-0585/)
# style type annotations for standard collections.
if PY39:

    @serde
    @dataclass
    class FooPy39:
        a: list[str]
        b: tuple[str, bool]
        c: dict[str, list[int]]


def main() -> None:
    cls = Foo if not PY39 else FooPy39

    h = cls(["1", "2"], ("foo", True), {"bar": [10, 20]})
    print(f"Into Json: {to_json(h)}")

    s = '{"a": ["1", "2"], "b": ["foo", true], "c": {"bar": [10, 20]}}'
    print(f"From Json: {from_json(cls, s)}")


if __name__ == "__main__":
    main()
