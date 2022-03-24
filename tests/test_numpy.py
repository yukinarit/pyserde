import logging
from dataclasses import fields

import numpy as np
import numpy.typing as npt
import pytest

import serde
from serde.compat import get_origin

from .common import all_formats, opt_case, opt_case_ids

log = logging.getLogger("test")

serde.init(True)


@pytest.mark.parametrize("opt", opt_case, ids=opt_case_ids())
@pytest.mark.parametrize("se,de", all_formats)
def test_simple(se, de, opt):
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
