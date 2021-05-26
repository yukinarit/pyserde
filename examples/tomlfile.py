"""
tomlfile.py

Read Pipenv Pipfile by pyserde.

Usage:
    $ pipenv install
    $ pipenv run tomlfile.py
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from serde import deserialize, serialize
from serde.toml import from_toml


@deserialize
@serialize
@dataclass
class Source:
    url: str
    verify_ssl: bool
    name: str


@deserialize
@serialize
@dataclass
class Requires:
    python_version: str


@deserialize
@serialize
@dataclass
class Package:
    path: Optional[str] = None
    version: Optional[str] = None
    editable: Optional[bool] = False


@deserialize
@serialize
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
