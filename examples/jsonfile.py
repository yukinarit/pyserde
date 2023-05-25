"""
jsonfile.py

Deserialize JSON into an object.

Usage:
    $ poetry install
    $ poetry run python jsonfile.py
"""
from dataclasses import dataclass
from typing import List, Optional

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
    text = r'''{
  "slideshow": {
    "author": "Yours Truly",
    "date": "date of publication",
    "slides": [
      {
        "title": "Wake up to WonderWidgets!",
        "type": "all"
      },
      {
        "items": [
          "Why <em>WonderWidgets</em> are great",
          "Who <em>buys</em> WonderWidgets"
        ],
        "title": "Overview",
        "type": "all"
      }
    ],
    "title": "Sample Slide Show"
  }
}
'''
    data = from_json(Data, text)
    print(data)


if __name__ == '__main__':
    main()
