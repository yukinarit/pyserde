from typing import Generic, TypeVar

from serde import from_dict, serde, to_dict


@serde
class EventData:
    pass


@serde
class A(EventData):
    a: str


# Additional subclasses of EventData exist

Data = TypeVar("Data", bound=EventData)


@serde
class Payload(Generic[Data]):
    id: int
    data: Data


@serde
class Event(Generic[Data]):
    name: str
    payload: Payload[Data]


def main() -> None:
    event_a = Event("a", Payload(1, A("a_str")))

    a_dict = to_dict(event_a)
    new_event_a = from_dict(Event[A], a_dict)

    print(event_a)
    print(new_event_a)

    # This has a bug, see https://github.com/yukinarit/pyserde/issues/464
    # payload = Payload(1, A("a_str"))
    # payload_dict = to_dict(payload)
    # new_payload = from_dict(Payload[A], payload_dict)
    # print(payload)
    # print(new_payload)


if __name__ == "__main__":
    main()
