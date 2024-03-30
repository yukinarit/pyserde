from plum import dispatch
from datetime import datetime
from serde import (
    serde,
    field,
)
from serde.json import from_json, to_json
from typing import Type, Any


class MySerializer:
    @dispatch
    def serialize(self, value: datetime) -> str:
        return value.strftime("%d/%m/%y")


class MyDeserializer:
    @dispatch
    def deserialize(self, cls: Type[datetime], value: Any) -> datetime:
        return datetime.strptime(value, "%d/%m/%y")


@serde(class_serializer=MySerializer(), class_deserializer=MyDeserializer())
class Foo:
    a: datetime
    b: datetime = field(
        serializer=lambda x: x.strftime("%y.%m.%d"),
        deserializer=lambda x: datetime.strptime(x, "%y.%m.%d"),
    )
    c: list[datetime] = field(default_factory=list)


def main() -> None:
    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt, [dt])
    print(f"Into Json: {to_json(f)}")

    s = '{"a": "01/01/21", "b": "01.01.21", "c": ["01/01/21"]}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
