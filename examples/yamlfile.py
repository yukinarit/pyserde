"""
yamlfile.py

Read swagger echo example yaml.

Usage:
    $ poetry install
    $ poetry run python yamlfile.py
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from serde import Untagged, serde
from serde.yaml import from_yaml


@serde(rename_all='camelcase')
@dataclass
class Info:
    title: str
    description: str
    version: str


@serde(rename_all='camelcase')
@dataclass
class Parameter:
    name: str
    # not yet supported.
    # infield: str = field(rename='in')
    type: str
    required: bool


@serde(rename_all='camelcase')
@dataclass
class Response:
    description: str


@serde(rename_all='camelcase', tagging=Untagged)
@dataclass
class Path:
    description: str
    operation_id: str
    parameters: List[Union[str, Parameter]]
    responses: Dict[Union[str, int], Response]


@serde(rename_all='camelcase')
@dataclass
class Prop:
    type: str
    format: Optional[str]


@serde(rename_all='camelcase')
@dataclass
class Definition:
    required: Optional[List[str]]
    properties: Dict[str, Prop]


@serde(rename_all='camelcase')
@dataclass
class Swagger:
    swagger: int
    info: Info
    host: str
    schemes: List[str]
    base_path = str
    produces: List[str]
    paths: Dict[str, Dict[str, Path]]
    definitions: Dict[str, Definition]


def main():
    with open('swagger.yml') as f:
        yaml = f.read()
    swagger = from_yaml(Swagger, yaml)
    print(swagger)


if __name__ == '__main__':
    main()
