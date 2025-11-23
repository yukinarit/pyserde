"""
tomlfile.py

Read Pipenv Pipfile by pyserde.

Usage:
    $ uv sync
    $ uv run python tomlfile.py
"""

from pathlib import Path

from serde import Untagged, serde
from serde.toml import from_toml

basedir = Path(__file__).parent


@serde
class Source:
    url: str
    verify_ssl: bool
    name: str


@serde
class Requires:
    python_version: str


@serde
class Package:
    path: str | None = None
    version: str | None = None
    editable: bool | None = False


@serde(tagging=Untagged)
class Pipfile:
    source: list[Source]
    requires: Requires | None
    packages: dict[str, str | Package]


def main() -> None:
    with open(basedir / "Pipfile") as f:
        toml = f.read()
    pip = from_toml(Pipfile, toml)
    print(pip)


if __name__ == "__main__":
    main()
