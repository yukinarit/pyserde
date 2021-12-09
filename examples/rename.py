"""
rename.py


Usage:
    $ poetry install
    $ poetry run python rename.py
"""

from serde import field, serde
from serde.json import to_json


@serde
class Foo:
    # Use 'class_name' because 'class' is a keyword.
    class_name: str = field(rename='class')


def main():
    print(to_json(Foo(class_name='Foo')))


if __name__ == '__main__':
    main()
