from collections import defaultdict

from serde import serde
from serde.json import from_json, to_json


@serde
class Bar:
    v: int | None = None


@serde
class Foo:
    a: defaultdict[str, list[int]]
    b: defaultdict[str, int]
    c: defaultdict[str, Bar]


def main() -> None:
    a: defaultdict[str, list[int]] = defaultdict(list)
    a["a"].append(1)
    b: defaultdict[str, int] = defaultdict(int)
    b["b"]
    c: defaultdict[str, Bar] = defaultdict(Bar)
    c["c"].v = 10

    f = Foo(a, b, c)
    print(f"Into Json: {to_json(f)}")

    s = '{"a": {"a": [1, 2]}, "b": {"b": 10}, "c": {"c": {}}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
