"""
PEP 673 Self type example.
"""

from typing import Self

from serde import serde
from serde.json import from_json, to_json


@serde
class Point:
    x: float
    y: float

    def translate(self, dx: float, dy: float) -> Self:
        return type(self)(x=self.x + dx, y=self.y + dy)

    @classmethod
    def origin(cls) -> Self:
        return cls(x=0.0, y=0.0)


def main() -> None:
    p = Point.origin().translate(3.0, 4.0)
    print(f"Point: {p}")
    print(f"To JSON: {to_json(p)}")

    s = '{"x": 1.0, "y": 2.0}'
    print(f"From JSON: {from_json(Point, s)}")


if __name__ == "__main__":
    main()
