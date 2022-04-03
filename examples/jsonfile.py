"""
jsonfile.py

Make an http request to JSON WebAPI.

Usage:
    $ poetry install
    $ poetry run python jsonfile.py
"""
from dataclasses import dataclass
from typing import List, Optional

import requests

from serde import serde
from serde.json import from_json


@serde
@dataclass
class Slide:
    title: str
    type: str
    items: Optional[List[str]]


@serde
@dataclass
class Slideshow:
    author: str
    date: str
    slides: List[Slide]
    title: str


@serde
@dataclass
class Data:
    slideshow: Slideshow


def main():
    text = requests.get('https://httpbin.org/json').text
    data = from_json(Data, text)
    print(data)


if __name__ == '__main__':
    main()
