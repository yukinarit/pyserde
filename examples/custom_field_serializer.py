from dataclasses import dataclass, field
from datetime import datetime

from serde import deserialize, serialize
from serde.json import from_json, to_json


@deserialize
@serialize
@dataclass
class Foo:
    dt1: datetime
    dt2: datetime = field(
        metadata={
            'serde_serializer': lambda x: x.strftime('%d/%m/%y'),
            'serde_deserializer': lambda x: datetime.strptime(x, '%d/%m/%y'),
        }
    )


def main():
    dt = datetime(2021, 1, 1, 0, 0, 0)
    f = Foo(dt, dt)
    print(f"Into Json: {to_json(f)}")

    s = '{"dt1": "2021-01-01T00:00:00", "dt2": "01/01/21"}'
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == '__main__':
    main()
