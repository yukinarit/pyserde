from dataclasses import dataclass
from typing import Union

from serde import serde, Untagged, AdjacentTagging, InternalTagging
from serde.json import from_json, to_json


@serde
@dataclass
class Bar:
    b: int


@serde
@dataclass(unsafe_hash=True)
class Baz:
    b: int


def main() -> None:
    baz = Baz(10)

    print("# external tagging (default)")
    a = to_json(baz, cls=Union[Bar, Baz])
    print("IntoJSON", a)
    print("FromJSON", from_json(Union[Bar, Baz], a))

    print("# internal tagging")
    a = to_json(baz, cls=InternalTagging("type", Union[Bar, Baz]))
    print("IntoJSON", a)
    print("FromJSON", from_json(InternalTagging("type", Union[Bar, Baz]), a))

    print("# adjacent tagging")
    a = to_json(baz, cls=AdjacentTagging("type", "content", Union[Bar, Baz]))
    print("IntoJSON", a)
    print("FromJSON", from_json(AdjacentTagging("type", "content", Union[Bar, Baz]), a))

    print("# untagged")
    a = to_json(baz, cls=Untagged(Union[Bar, Baz]))
    print("IntoJSON", a)
    print("FromJSON", from_json(Untagged(Union[Bar, Baz]), a))


if __name__ == "__main__":
    main()
