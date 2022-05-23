"""
tomlfile.py

Read Pipenv Pipfile by pyserde.

Usage:
    $ poetry install
    $ poetry run python tomlfile.py
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from serde import Untagged, serde
from serde.toml import from_toml


@serde
@dataclass
class Source:
    url: str
    verify_ssl: bool
    name: str


@serde
@dataclass
class Requires:
    python_version: str


@serde
@dataclass
class Package:
    path: Optional[str] = None
    version: Optional[str] = None
    editable: Optional[bool] = False


@serde(tagging=Untagged)
@dataclass
class Pipfile:
    source: List[Source]
    requires: Optional[Requires]
    packages: Dict[str, Union[str, Package]]


def main():
    with open('Pipfile') as f:
        toml = f.read()
    pip = from_toml(Pipfile, toml)
    print(pip)


if __name__ == '__main__':
    main()
