import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

from serde import serde
from serde.json import from_json, to_json

PY39 = sys.version_info[:3] >= (3, 9, 0)


@serde
@dataclass
class Foo:
    l: List[str]
    t: Tuple[str, bool]
    d: Dict[str, List[str]]


# For python >= 3.9, you can use [PEP585](https://www.python.org/dev/peps/pep-0585/)
# style type annotations for standard collections.
if PY39:

    @serde
    @dataclass
    class FooPy39:
        l: list[str]
        t: tuple[str, bool]
        d: dict[str, list[int]]


def main():
    cls = Foo if not PY39 else FooPy39

    h = cls([1, 2], ('foo', True), {'bar': [10, 20]})
    print(f"Into Json: {to_json(h)}")

    s = '{"l": [1, 2], "t": ["foo", true], "d": {"bar": [10, 20]}}'
    print(f"From Json: {from_json(cls, s)}")


if __name__ == '__main__':
    main()
