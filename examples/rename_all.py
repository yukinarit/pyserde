"""
rename_all.py


Usage:
    $ uv sync
    $ uv run python rename_all.py
"""

from serde import serde
from serde.json import from_json, to_json


@serde(rename_all="pascalcase")
class Foo:
    name: str
    no: int | None = None


def main() -> None:
    f = Foo("Pikachu")
    print(f"Into Json: {to_json(f)}")

    s = '{"Name": "Pikachu", "No": 25}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
