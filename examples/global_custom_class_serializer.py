from plum import dispatch
from datetime import datetime
from serde import serde, add_serializer, add_deserializer
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


class MySerializer2:
    @dispatch
    def serialize(self, value: int) -> str:
        return str(value)


class MyDeserializer2:
    @dispatch
    def deserialize(self, cls: Type[int], value: Any) -> int:
        return int(value)


class MySerializer3:
    @dispatch
    def serialize(self, value: float) -> str:
        return str(value)


class MyDeserializer3:
    @dispatch
    def deserialize(self, cls: Type[float], value: Any) -> float:
        return float(value)


add_serializer(MySerializer())
add_serializer(MySerializer2())
add_deserializer(MyDeserializer())
add_deserializer(MyDeserializer2())


@serde(class_serializer=MySerializer3(), class_deserializer=MyDeserializer3())
class Foo:
    a: datetime
    b: int
    c: float


def main() -> None:
    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, 10, 100.0)
    print(f"Into Json: {to_json(f)}")

    s = '{"a": "01/01/21", "b": "10", "c": "100.0"}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
