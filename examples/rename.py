"""
rename.py


Usage:
    $ pipenv install
    $ pipenv run rename.py
"""
from dataclasses import dataclass, field
from serde import serialize
from serde.json import to_json


@serialize
@dataclass
class Foo:
    # Use 'class_name' because 'class' is a keyword.
    class_name: str = field(metadata={'serde_rename': 'class'})


def main():
    print(to_json(Foo(class_name='Foge')))


if __name__ == '__main__':
    main()
