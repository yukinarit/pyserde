import uuid

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    v1: uuid.UUID
    v3: uuid.UUID
    v4: uuid.UUID
    v5: uuid.UUID


def main() -> None:
    foo = Foo(
        v1=uuid.uuid1(),
        v3=uuid.uuid3(uuid.NAMESPACE_DNS, "pyserde.org"),
        v4=uuid.uuid4(),
        v5=uuid.uuid5(uuid.NAMESPACE_DNS, "pyserde.org"),
    )
    print(f"Into Json: {to_json(foo)}")

    s = """{
        "v1": "a8098c1a-f86e-11da-bd1a-00112444be1e",
        "v3": "6fa459ea-ee8a-3ca4-894e-db77e160355e",
        "v4": "916b3609-0015-41be-be4c-53b74cab0d03",
        "v5": "886313e1-3b8a-5372-9b90-0c9aee199e5d"
    }"""
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
