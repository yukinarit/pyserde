from dataclasses import dataclass

from serde import serde
from serde.json import from_json, to_json


# Suppose this is a dataclass defined in an external library
# To (de)serialize this dataclass with a class attribute,
# create a new class `Wrapper` to extend `External` then add the
# class attribute to `Wrapper`.
@dataclass
class External:
    some_value: int


@serde(rename_all="kebabcase")
@dataclass
class Wrapper(External):
    pass


def main() -> None:
    f = Wrapper(some_value=10)
    print(f"Into Json: {to_json(f)}")

    s = '{"some-value": 10}'
    print(f"From Json: {from_json(Wrapper, s)}")


if __name__ == "__main__":
    main()
