"""
rename_all.py


Usage:
    $ poetry install
    $ poetry run python rename_all.py
"""
from dataclasses import dataclass
from typing import Optional

from serde import serde
from serde.json import from_json, to_json


@serde(rename_all='pascalcase')
@dataclass
class Foo:
    name: str
    no: Optional[int] = None


def main():
    f = Foo('Pikachu')
    print(f"Into Json: {to_json(f)}")

    s = '{"Name": "Pikachu", "No": 25}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
