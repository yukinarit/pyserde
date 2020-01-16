from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import pytest

from serde import typecheck
from serde.compat import is_dict, is_list, is_opt, is_tuple, is_union, iter_types, type_args, union_args

from .data import Bool, Float, Int, Pri, PriOpt, Str


def test_types():
    assert is_list(List[int])
    assert is_tuple(Tuple[int, int, int])
    assert is_dict(Dict[str, int])
    assert is_opt(Optional[int])
    assert is_union(Union[int, str])
    assert is_union(Union[Optional[int], Optional[str]])
    assert is_opt(Optional[int])
    assert not is_union(Optional[int])
    assert not is_opt(Union[Optional[int], Optional[str]])
    assert is_union(Union[Optional[int], Optional[str]])


def test_iter_types():
    assert [Pri, int, str, float, bool] == list(iter_types(Pri))
    assert [str, Pri, int, str, float, bool] == list(iter_types(Dict[str, Pri]))
    assert [str] == list(iter_types(List[str]))
    assert [int, str, bool, float] == list(iter_types(Tuple[int, str, bool, float]))
    assert [PriOpt, int, str, float, bool] == list(iter_types(PriOpt))
    assert [Pri, int, str, float, bool, Pri, int, str, float, bool, Pri, int, str, float, bool] == list(
        iter_types(Tuple[List[Pri], Tuple[Pri, Pri]])
    )


def test_type_args():
    assert (int,) == type_args(List[int])
    assert (int, str) == type_args(Dict[int, str])
    assert (int, type(None)) == type_args(Optional[int])
    assert (Optional[int],) == type_args(List[Optional[int]])
    assert (List[int], type(None)) == type_args(Optional[List[int]])
    assert (List[int], Dict[str, int]) == type_args(Union[List[int], Dict[str, int]])
    assert (int, type(None), str) == type_args(Union[Optional[int], str])


def test_union_args():
    assert (int, str) == union_args(Union[int, str])
    assert (List[int], Dict[int, str]) == union_args(Union[List[int], Dict[int, str]])
    assert (Optional[int], str) == union_args(Union[Optional[int], str])


def test_typecheck():
    # Primitive
    typecheck(int, 10)
    with pytest.raises(ValueError):
        typecheck(int, 10.0)

    # Dataclass
    p = Pri(i=10, s='foo', f=100.0, b=True)
    typecheck(Pri, p)

    with pytest.raises(ValueError):
        p.i = 10.0
        typecheck(Pri, p)

    # Dataclass (Nested)
    @dataclass
    class Foo:
        p: Pri

    h = Foo(Pri(i=10, s='foo', f=100.0, b=True))
    typecheck(Foo, h)

    with pytest.raises(ValueError):
        h.p.i = 10.0
        typecheck(Foo, h)

    # List
    typecheck(List[int], [10])
    with pytest.raises(ValueError):
        typecheck(List[int], [10.0])

    # List of dataclasses
    typecheck(List[Int], [Int(n) for n in range(1, 10)])
    with pytest.raises(ValueError):
        typecheck(List[Pri], [Pri(i=10.0, s='foo', f=100.0, b=True)])

    # Tuple
    typecheck(Tuple[int, str, float, bool], (10, 'foo', 100.0, True))
    with pytest.raises(ValueError):
        typecheck(Tuple[int, str, float, bool], (10.0, 'foo', 100.0, True))

    # Tuple of dataclasses
    typecheck(Tuple[Int, Str, Float, Bool], (Int(10), Str('foo'), Float(100.0), Bool(True)))
    with pytest.raises(ValueError):
        typecheck(Tuple[Int, Str, Float, Bool], (Int(10.0), Str('foo'), Float(100.0), Bool(True)))

    # Dict
    typecheck(Dict[str, int], dict(foo=10, bar=20))
    with pytest.raises(ValueError):
        typecheck(Dict[str, int], dict(foo=10.0, bar=20))

    # Dict of dataclasses
    typecheck(Dict[Str, Int], {Str('foo'): Int(10), Str('bar'): Int(20)})
    with pytest.raises(ValueError):
        typecheck(Dict[Str, Int], {Str('foo'): Int(10.0), Str('bar'): Int(20)})

    # Optional
    typecheck(Optional[int], 10)
    typecheck(Optional[int], None)
    with pytest.raises(ValueError):
        typecheck(Optional[int], 10.0)

    # Optional of dataclass
    typecheck(Optional[Int], Int(10))
    typecheck(Optional[Int], None)
    with pytest.raises(ValueError):
        typecheck(Optional[Int], 10.0)
        typecheck(Optional[Int], Int(10.0))
