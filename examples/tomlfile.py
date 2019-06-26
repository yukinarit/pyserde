"""
tomlfile.py

Read Pipenv Pipfile by pyserde.

Usage:
    $ pipenv install
    $ pipenv run tomlfile.py
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from serde import serialize, deserialize
from serde.toml import from_toml


@deserialize
@dataclass
class Source:
    url: str
    verify_ssl: bool
    name: str


@deserialize
@dataclass
class Requires:
    python_version: str


@deserialize
@dataclass
class Package:
    path: Optional[str] = None
    version: Optional[str] = None
    editable: bool = False


@deserialize
@dataclass
class Pipfile:
    source: List[Source]
    requires: Requires
    packages: Dict[str, Package]


def main():
    with open('Pipfile') as f:
        toml = f.read()
    pip = from_toml(Pipfile, toml)
    print(pip)


if __name__ == '__main__':
    main()
