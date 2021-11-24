from typing import Dict, List, Union

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    v: Union[int, str]
    c: Union[Dict[str, int], List[int]]


def main():
    f = Foo(10, [1, 2, 3])
    print(f"Into Json: {to_json(f)}")

    s = '{"v": 10, "c": [1, 2, 3]}'
    print(f"From Json: {from_json(Foo, s)}")

    f = Foo('foo', {'bar': 1, 'baz': 2})
    print(f"Into Json: {to_json(f)}")

    s = '{"v": "foo", "c": {"bar": 1, "baz": 2}}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
