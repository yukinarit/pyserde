"""
yamlfile.py

Read swagger echo example yaml.

Usage:
    $ pipenv install
    $ pipenv run yamlfile.py
"""
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from serde import deserialize
from serde.yaml import from_yaml


@deserialize(rename_all='camelcase')
@dataclass
class Info:
    title: str
    description: str
    version: str


@deserialize(rename_all='camelcase')
@dataclass
class Parameter:
    name: str
    # not yet supported.
    # infield: str = field(metadata={'serde_rename': 'in'})
    type: str
    required: bool


@deserialize(rename_all='camelcase')
@dataclass
class Response:
    description: str


@deserialize(rename_all='camelcase')
@dataclass
class Path:
    description: str
    operation_id: str
    parameters: List[Union[str, Parameter]]
    responses: Dict[Union[str, int], Response]


@deserialize(rename_all='camelcase')
@dataclass
class Prop:
    type: str
    format: Optional[str]


@deserialize(rename_all='camelcase')
@dataclass
class Definition:
    required: Optional[List[str]]
    properties: Dict[str, Prop]


@deserialize(rename_all='camelcase')
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
