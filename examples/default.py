from serde import serde, field
from serde.json import from_json, to_json


@serde
class Foo:
    i: int = 10
    s: str = "foo"
    f: float = field(default=100.0)  # Use dataclass field.
    b: bool = field(default=True)
    d: dict[str, int] = field(default_factory=dict)


def main() -> None:
    h = Foo()
    print(f"Into Json: {to_json(h)}")

    s = "{}"
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
