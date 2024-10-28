from serde import serde, SerdeError
from serde.json import from_json


@serde(deny_unknown_fields=True)
class Foo:
    a: int
    b: str


def main() -> None:
    try:
        s = '{"a": 10, "b": "foo", "c": 100.0, "d": true}'
        print(f"From Json: {from_json(Foo, s)}")
    except SerdeError:
        pass


if __name__ == "__main__":
    main()
