from dataclasses import dataclass

from serde import serde


type Baz = tuple[float, float]
type Bar = tuple[Baz, ...]


@serde(rename_all="camelcase")
@dataclass(frozen=True)
class Foo:
    name: str
    bar: Bar


def main() -> None:
    fig = Foo("test", ((0.0, 0.0), (1.0, 1.73), (-1.0, 1.73)))
    print(fig)


if __name__ == "__main__":
    main()
