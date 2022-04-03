"""
skip.py

Example usage of skip and skip_if attributes.

Usage:
    $ poetry install
    $ poetry run python skip.py
"""

from dataclasses import dataclass
from typing import Dict, List

from serde import field, serde
from serde.json import to_json


@serde
@dataclass
class Resource:
    name: str
    hash: str
    metadata: Dict[str, str] = field(default_factory=dict, skip=True)


@serde
@dataclass
class World:
    player: str
    enemies: List[str] = field(default_factory=list, skip_if_false=True)
    buddy: str = field(default='', skip_if=lambda v: v == 'Pikachu')
    town: str = field(default='Masara Town', skip_if_default=True)


def main():
    resources = [
        Resource("Stack Overflow", "b6469c3f31653d281bbbfa6f94d60fea130abe38"),
        Resource("GitHub", "5cb7a0c47e53854cd00e1a968de5abce1c124601", metadata={"headquarters": "San Francisco"}),
    ]
    print(to_json(resources))

    # "buddy" and "town" field will be omitted
    world = World('satoshi', ['Rattata', 'Pidgey'], 'Pikachu')
    print(to_json(world))

    # "enemies" field will be omitted
    world = World('green', [], 'Charmander', 'Black City')
    print(to_json(world))


if __name__ == '__main__':
    main()
