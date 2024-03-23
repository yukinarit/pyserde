from datetime import datetime

from serde import field, serde
from serde.json import from_json, to_json


@serde
class Foo:
    a: datetime
    b: datetime = field(
        serializer=lambda x: x.strftime("%d/%m/%y"),
        deserializer=lambda x: datetime.strptime(x, "%d/%m/%y"),
    )


def main() -> None:
    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt)
    print(f"Into Json: {to_json(f)}")

    s = '{"a": "2021-01-01T00:00:00", "b": "01/01/21"}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
