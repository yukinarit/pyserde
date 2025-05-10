import numpy

from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    bo: numpy.bool_
    by: numpy.byte
    in_: numpy.int_
    inc: numpy.intc
    ui: numpy.uint
    fl: numpy.float64
    st: numpy.str_
    nd: numpy.typing.NDArray[numpy.int_]
    ha: numpy.half
    da: numpy.datetime64


def main() -> None:
    foo = Foo(
        bo=numpy.bool_(True),
        by=numpy.byte(38),
        in_=numpy.int_(42),
        inc=numpy.intc(42),
        ui=numpy.uint(42),
        fl=numpy.float64(3.14),
        st=numpy.str_("numpy str"),
        nd=numpy.array([1, 2, 3]),
        ha=numpy.half(3.14),
        da=numpy.datetime64("2020-01-01T03:30:00.162"),
    )
    print(f"Into Json: {to_json(foo)}")

    s = """{
        "bo": true,
        "by": 38,
        "in_": 42,
        "inc": 42,
        "ui": 42,
        "fl": 3.14,
        "st": "numpy str",
        "nd": [1, 2, 3],
        "ha": 3.14,
        "da": "2020-01-01T03:30:00.162"
    }"""
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
