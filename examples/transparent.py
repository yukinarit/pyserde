from serde import field, serde
from serde.json import from_json, to_json


@serde(transparent=True)
class UserId:
    value: int


@serde
class Inner:
    i: int
    s: str


@serde(transparent=True)
class WrappedInner:
    inner: Inner


@serde(transparent=True)
class CachedId:
    value: int
    cache: int = field(default=0, init=False, skip=True)


def main() -> None:
    print(f"UserId -> JSON: {to_json(UserId(7))}")
    print(f"JSON -> UserId: {from_json(UserId, '7')}")

    wrapped = WrappedInner(Inner(1, "x"))
    data = '{"i":1,"s":"x"}'
    print(f"WrappedInner -> JSON: {to_json(wrapped)}")
    print(f"JSON -> WrappedInner: {from_json(WrappedInner, data)}")

    cached = CachedId(42)
    print(f"CachedId -> JSON: {to_json(cached)}")
    print(f"JSON -> CachedId: {from_json(CachedId, '42')}")


if __name__ == "__main__":
    main()
