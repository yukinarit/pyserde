from serde import serde, Untagged, AdjacentTagging, InternalTagging
from serde.json import from_json, to_json


@serde
class Bar:
    b: int


@serde
class Baz:
    b: int


def main() -> None:
    baz = Baz(10)

    print("# external tagging (default)")
    a = to_json(baz, cls=Bar | Baz)
    print("IntoJSON", a)
    print("FromJSON", from_json(Bar | Baz, a))

    print("# internal tagging")
    a = to_json(baz, cls=InternalTagging("type", Bar | Baz))
    print("IntoJSON", a)
    print("FromJSON", from_json(InternalTagging("type", Bar | Baz), a))

    print("# adjacent tagging")
    a = to_json(baz, cls=AdjacentTagging("type", "content", Bar | Baz))
    print("IntoJSON", a)
    print("FromJSON", from_json(AdjacentTagging("type", "content", Bar | Baz), a))

    print("# untagged")
    a = to_json(baz, cls=Untagged(Bar | Baz))
    print("IntoJSON", a)
    print("FromJSON", from_json(Untagged(Bar | Baz), a))


if __name__ == "__main__":
    main()
