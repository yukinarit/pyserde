"""
rename_all.py


Usage:
    $ pipenv install
    $ pipenv run rename_all.py
"""
from dataclasses import dataclass
from typing import Optional

from serde import deserialize, serialize
from serde.json import from_json, to_json


@deserialize(rename_all='pascalcase')
@serialize(rename_all='pascalcase')
@dataclass()
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
