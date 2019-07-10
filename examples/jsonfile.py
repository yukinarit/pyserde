"""
jsonfile.py

Make an http request to JSON WebAPI.

Usage:
    $ pipenv install
    $ pipenv run jsonfile.py
"""
import requests

from typing import List, Optional
from dataclasses import dataclass
from serde import deserialize
from serde.json import from_json


@deserialize
@dataclass
class Slide:
    title: str
    type: str
    items: Optional[List[str]]


@deserialize
@dataclass
class Slideshow:
    author: str
    date: str
    slides: List[Slide]
    title: str


@deserialize
@dataclass
class Data:
    slideshow: Slideshow


def main():
    text = requests.get('https://httpbin.org/json').text
    data = from_json(Data, text)
    print(data)


if __name__ == '__main__':
    main()
