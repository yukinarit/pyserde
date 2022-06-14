from dataclasses import dataclass

from serde import serde
from serde.json import from_json


class MyException(Exception):
    pass


@serde
@dataclass
class Foo:
    v: int

    def __post_init__(self):
        if self.v == 10:
            raise MyException("Invalid value")


def main():
    try:
        s = '{"v": 10}'
        print(f"From Json: {from_json(Foo, s)}")

    except MyException as e:
        # Any exception from __post_init__ won't be wrapped by SerdeError.
        print(f"Got user exception: {e}")


if __name__ == '__main__':
    main()
