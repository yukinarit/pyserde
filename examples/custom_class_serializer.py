from dataclasses import dataclass, field
from datetime import datetime

from serde import SerdeSkip, default_deserializer, default_serializer, deserialize, serialize
from serde.json import from_json, to_json


def serializer(cls, o):
    """
    Custom class level serializer.
    """

    # You can provide a custom serialize/deserialize logic for certain types.
    if cls is datetime:
        return o.strftime('%d/%m/%y')
    # Raise SerdeSkip to tell serde to use the default serializer/deserializer.
    else:
        raise SerdeSkip()


def deserializer(cls, o):
    """
    Custom class level deserializer.
    """
    if cls is datetime:
        return datetime.strptime(o, '%d/%m/%y')
    else:
        raise SerdeSkip()


@deserialize(deserializer=deserializer)
@serialize(serializer=serializer)
@dataclass
class Foo:
    i: int
    dt1: datetime
    # Override by field serializer/deserializer.
    dt2: datetime = field(
        metadata={
            'serde_serializer': lambda x: x.strftime('%y.%m.%d'),
            'serde_deserializer': lambda x: datetime.strptime(x, '%y.%m.%d'),
        }
    )
    # Override by the default serializer/deserializer.
    dt3: datetime = field(metadata={'serde_serializer': default_serializer, 'serde_deserializer': default_deserializer})


def main():
    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(10, dt, dt, dt)
    print(f"Into Json: {to_json(f)}")

    s = '{"i": 10, "dt1": "01/01/21", "dt2": "01.01.21", "dt3": "2021-01-01T00:00:00"}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
