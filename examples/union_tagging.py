from typing import Union

from serde import AdjacentTagging, InternalTagging, Untagged, serde
from serde.json import from_json, to_json


@serde
class Bar:
    b: int


@serde
class Baz:
    b: int


def external_tagging():
    @serde
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Baz(10))
    print(f"Into Json: {to_json(f)}")

    s = '{"a": {"Baz": {"b": 10}}}'
    print(f"From Json: {from_json(Foo, s)}")


def internal_tagging():
    @serde(tagging=InternalTagging("type"))
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Baz(10))
    print(f"Into Json: {to_json(f)}")

    s = '{"a": {"type": "Baz", "b": 10}}'
    print(f"From Json: {from_json(Foo, s)}")


def adjacent_tagging():
    @serde(tagging=AdjacentTagging(tag="type", content="content"))
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Baz(10))
    print(f"Into Json: {to_json(f)}")

    s = '{"a": {"type": "Baz", "content": {"b": 10}}}'
    print(f"From Json: {from_json(Foo, s)}")


def untagged():
    @serde(tagging=Untagged)
    class Foo:
        a: Union[Bar, Baz]

    f = Foo(Baz(10))
    print(f"Into Json: {to_json(f)}")

    # Untagged cannot correctly deserialize unions with the same fields.
    s = '{"a": {"b": 10}}'
    print(f"From Json: {from_json(Foo, s)}")


def main():
    print('# external tagging (default)')
    external_tagging()
    print('# internal tagging')
    internal_tagging()
    print('# adjacent tagging')
    adjacent_tagging()
    print('# untagged')
    untagged()


if __name__ == '__main__':
    main()
