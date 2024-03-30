from __future__ import annotations
from dataclasses import dataclass

from serde import serde
from serde.json import from_json, to_json


@dataclass
class Node:
    name: str
    children: list[Node]


serde(Node)


def main() -> None:
    n = Node("a", [Node("b", [Node("c", [])])])
    s = to_json(n)
    print(f"Into Json: {s}")
    print(f"From Json: {from_json(Node, s)}")


if __name__ == "__main__":
    main()
