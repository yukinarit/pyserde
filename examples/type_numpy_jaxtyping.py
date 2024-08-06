import numpy
from jaxtyping import (
    Float,
    Float16,
    Float32,
    Float64,
    Inexact,
    Int,
    Int8,
    Int16,
    Int32,
    Int64,
    Integer,
    UInt,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
)
from serde import serde
from serde.json import from_json, to_json


@serde
class Foo:
    float_: Float[numpy.ndarray, "3 3"]
    float16: Float16[numpy.ndarray, "3 3"]
    float32: Float32[numpy.ndarray, "3 3"]
    float64: Float64[numpy.ndarray, "3 3"]
    inexact: Inexact[numpy.ndarray, "3 3"]
    int_: Int[numpy.ndarray, "3 3"]
    int8: Int8[numpy.ndarray, "3 3"]
    int16: Int16[numpy.ndarray, "3 3"]
    int32: Int32[numpy.ndarray, "3 3"]
    int64: Int64[numpy.ndarray, "3 3"]
    integer: Integer[numpy.ndarray, "3 3"]
    uint: UInt[numpy.ndarray, "3 3"]
    uint8: UInt8[numpy.ndarray, "3 3"]
    uint16: UInt16[numpy.ndarray, "3 3"]
    uint32: UInt32[numpy.ndarray, "3 3"]
    uint64: UInt64[numpy.ndarray, "3 3"]


def main() -> None:
    foo = Foo(
        float_=numpy.zeros((3, 3), dtype=float),
        float16=numpy.zeros((3, 3), dtype=numpy.float16),
        float32=numpy.zeros((3, 3), dtype=numpy.float32),
        float64=numpy.zeros((3, 3), dtype=numpy.float64),
        inexact=numpy.zeros((3, 3), dtype=numpy.inexact),
        int_=numpy.zeros((3, 3), dtype=int),
        int8=numpy.zeros((3, 3), dtype=numpy.int8),
        int16=numpy.zeros((3, 3), dtype=numpy.int16),
        int32=numpy.zeros((3, 3), dtype=numpy.int32),
        int64=numpy.zeros((3, 3), dtype=numpy.int64),
        integer=numpy.zeros((3, 3), dtype=numpy.integer),
        uint=numpy.zeros((3, 3), dtype=numpy.uint),
        uint8=numpy.zeros((3, 3), dtype=numpy.uint8),
        uint16=numpy.zeros((3, 3), dtype=numpy.uint16),
        uint32=numpy.zeros((3, 3), dtype=numpy.uint32),
        uint64=numpy.zeros((3, 3), dtype=numpy.uint64),
    )

    print(f"Into Json: {to_json(foo)}")

    s = """
    {
        "float_": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        "float16": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        "float32": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        "float64": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        "inexact": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        "int_": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "int8": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "int16": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "int32": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "int64": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "integer": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "uint": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "uint8": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "uint16": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "uint32": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "uint64": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    }
    """
    print(f"From Json: {from_json(Foo, s)}")


if __name__ == "__main__":
    main()
