from dataclasses import dataclass

from serde import InternalTagging, from_dict, serde, to_dict


@serde(tagging=InternalTagging("type"))
@dataclass
class Leaf:
    value: int


@dataclass
class Node:
    name: str
    children: list[Leaf | Node]


serde(Node, tagging=InternalTagging("type"))


def main() -> None:
    node1 = Node("node1", [Leaf(10)])
    node2 = Node("node2", [node1])
    d = to_dict(node2)
    print(f"Into dict: {d}")
    node = from_dict(Node, d)
    print(f"From dict: {node}")


if __name__ == "__main__":
    main()
