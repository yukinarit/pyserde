import logging
from dataclasses import fields
from beartype.typing import List

import numpy as np
import numpy.typing as npt
import pytest

import serde
from serde.compat import get_origin

from .common import all_formats, format_json, format_msgpack, opt_case, opt_case_ids

log = logging.getLogger("test")

serde.init(True)


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_numpy_simple(se, de, opt):
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    @serde.serde(**opt)
    class NPFoo:
        i: np.int32
        j: np.int64
        f: np.float32
        g: np.float64
        h: np.bool_
        u: np.ndarray
        v: npt.NDArray
        w: npt.NDArray[np.int32]
        x: npt.NDArray[np.int64]
        y: npt.NDArray[np.float32]
        z: npt.NDArray[np.float64]

        def __eq__(self, other):
            return (
                self.i == other.i
                and self.j == other.j
                and self.f == other.f
                and self.g == other.g
                and self.h == other.h
                and (self.u == other.u).all()
                and (self.v == other.v).all()
                and (self.w == other.w).all()
                and (self.x == other.x).all()
                and (self.y == other.y).all()
                and (self.z == other.z).all()
            )

    npfoo = NPFoo(
        np.int32(1),
        np.int64(2),
        np.float32(3.0),
        np.float64(4.0),
        np.bool_(False),
        np.array([1, 2]),
        np.array([3, 4]),
        np.array([np.int32(i) for i in [1, 2]]),
        np.array([np.int64(i) for i in [3, 4]]),
        np.array([np.float32(i) for i in [5.0, 6.0]]),
        np.array([np.float64(i) for i in [7.0, 8.0]]),
    )

    de_npfoo = de(NPFoo, se(npfoo))

    assert npfoo == de_npfoo

    for field in fields(NPFoo):
        value = getattr(npfoo, field.name)
        de_value = getattr(de_npfoo, field.name)

        assert type(value) == type(de_value)

        typ = field.type
        orig_type = get_origin(typ)
        if orig_type is not None:
            typ = orig_type

        assert type(de_value) == typ
        assert type(de_value).dtype == field.type.dtype

    @serde.serde(**opt)
    class NumpyDate:
        d: np.datetime64

    date_test = NumpyDate(np.datetime64(10, "Y"))

    assert de(NumpyDate, se(date_test)) == date_test


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", format_json + format_msgpack)
def test_encode_numpy(se, de, opt):
    log.info(f"Running test with se={se.__name__} de={de.__name__} opts={opt}")

    de_int = de(int, se(np.int32(1)))
    assert de_int == 1
    assert isinstance(de_int, int)

    de_arr = de(list, se(np.array([1, 2, 3])))
    assert isinstance(de_arr, list)
    assert de_arr == [1, 2, 3]

    @serde.serde(**opt)
    class MisTyped:
        a: int
        b: float
        h: bool
        c: List[int]
        d: List[float]
        e: List[bool]

    def unchecked_new(
        a: np.int32,
        b: np.float32,
        h: np.bool_,
        c: npt.NDArray[np.int32],
        d: npt.NDArray[np.float32],
        e: npt.NDArray[np.bool_],
    ) -> MisTyped:
        obj = MisTyped(
            0,
            0.0,
            True,
            [],
            [],
            [],
        )
        obj.a = a  # type: ignore
        obj.b = b  # type: ignore
        obj.h = h  # type: ignore
        obj.c = c  # type: ignore
        obj.d = d  # type: ignore
        obj.e = e  # type: ignore
        return obj

    expected = MisTyped(1, 3.0, False, [1, 2], [5.0, 6.0], [True, False])

    test1 = unchecked_new(
        np.int32(1),
        np.float32(3.0),
        np.bool_(False),
        np.array([np.int32(i) for i in [1, 2]]),
        np.array([np.float32(i) for i in [5.0, 6.0]]),
        np.array([np.bool_(i) for i in [True, False]]),
    )

    assert de(MisTyped, se(test1)) == expected

    test2 = unchecked_new(
        np.int64(1),
        np.float64(3.0),
        np.bool_(False),
        np.array([np.int64(i) for i in [1, 2]]),
        np.array([np.float64(i) for i in [5.0, 6.0]]),
        np.array([np.bool_(i) for i in [True, False]]),
    )

    assert de(MisTyped, se(test2)) == expected

    test3 = unchecked_new(
        np.int64(1),
        np.float64(3.0),
        np.bool_(False),
        np.array([np.int64(i) for i in [1, 2]]),
        np.array([np.float64(i) for i in [5.0, 6.0]]),
        np.array([np.bool_(i) for i in [True, False]]),
    )

    assert de(MisTyped, se(test3)) == expected

    np_datetime = np.datetime64("2022-04-27")
    assert de(np.datetime64, se(np_datetime)) == np_datetime

    for value in [np.int32(1), np.int64(1), np.bool_(False), np.bool_(True), int(1), False, True]:
        typ = type(value)
        de_value = de(typ, se(value))
        assert de_value == value
        assert type(de_value) == typ

        # test bare numpy array deserialization
        arr = np.array([0, 1, 2], dtype=typ)
        de_arr = de(np.ndarray, se(arr))
        assert (de_arr == arr).all()

        # test arrays with dtype=type(value)
        arr_typ = npt.NDArray[typ]

        de_arr = de(arr_typ, se(arr))
        assert (de_arr == arr).all()
        assert de_arr.dtype == arr.dtype == typ

    class BadClass:
        def __init__(self, x):
            self.x = x

    b = BadClass(1)

    with pytest.raises(TypeError):
        se(b)


@pytest.mark.parametrize("se,de", format_json + format_msgpack)
def test_encode_numpy_with_no_default_encoder(se, de):
    log.info(f"Running test with se={se.__name__} de={de.__name__} with no default encoder")

    with pytest.raises(TypeError):
        se(np.int32(1), default=None, option=None)

    with pytest.raises(TypeError):
        se(np.array([1, 2, 3]), default=None, option=None)

    @serde.serde
    class MisTypedNoDefaultEncoder:
        a: int
        b: float
        h: bool
        c: List[int]
        d: List[float]
        e: List[bool]

    def unchecked_new(
        a: np.int32,
        b: np.float32,
        h: np.bool_,
        c: npt.NDArray[np.int32],
        d: npt.NDArray[np.float32],
        e: npt.NDArray[np.bool_],
    ) -> MisTypedNoDefaultEncoder:
        obj = MisTypedNoDefaultEncoder(
            0,
            0.0,
            True,
            [],
            [],
            [],
        )
        obj.a = a  # type: ignore
        obj.b = b  # type: ignore
        obj.h = h  # type: ignore
        obj.c = c  # type: ignore
        obj.d = d  # type: ignore
        obj.e = e  # type: ignore
        return obj

    test1 = unchecked_new(
        np.int32(1),
        np.float32(3.0),
        np.bool_(False),
        np.array([np.int32(i) for i in [1, 2]]),
        np.array([np.float32(i) for i in [5.0, 6.0]]),
        np.array([np.bool_(i) for i in [True, False]]),
    )

    with pytest.raises(TypeError):
        se(test1, default=None, option=None)

    test2 = unchecked_new(
        np.int64(1),
        np.float64(3.0),
        np.bool_(False),
        np.array([np.int64(i) for i in [1, 2]]),
        np.array([np.float64(i) for i in [5.0, 6.0]]),
        np.array([np.bool_(i) for i in [True, False]]),
    )

    with pytest.raises(TypeError):
        se(test2, default=None, option=None)


def test_numpy_misc():
    assert serde.numpy.fullname(str) == "str"
