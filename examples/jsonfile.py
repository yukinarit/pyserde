"""
jsonfile.py

Deserialize JSON into an object.

Usage:
    $ uv sync
    $ uv run python jsonfile.py
"""

from serde import serde
from serde.json import from_json


@serde
class Slide:
    title: str
    type: str
    items: list[str] | None


@serde
class Slideshow:
    author: str
    date: str
    slides: list[Slide]
    title: str


@serde
class Data:
    slideshow: Slideshow


def main() -> None:
    text = r"""{
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
"""
    data = from_json(Data, text)
    print(data)


if __name__ == "__main__":
    main()
