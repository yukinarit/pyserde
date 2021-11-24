from typing import Set

from serde import asdict, astuple, serialize, to_dict, to_tuple
from serde.json import to_json
from serde.msgpack import to_msgpack

from . import data
from .data import (
    Bool,
    Float,
    Int,
    NestedInt,
    NestedPri,
    NestedPriDict,
    NestedPriList,
    NestedPriTuple,
    Pri,
    PriDict,
    PriList,
    PriOpt,
    PriTuple,
    Str,
)


def test_asdict():
    p = Pri(10, 'foo', 100.0, True)
    assert {'b': True, 'f': 100.0, 'i': 10, 's': 'foo'} == to_dict(p)
    assert {'b': True, 'f': 100.0, 'i': 10, 's': 'foo'} == asdict(p)


def test_astuple():
    assert data.PRI_TUPLE == to_tuple(data.PRI)
    assert data.PRI_TUPLE == astuple(data.PRI)
    assert data.PRILIST == to_tuple(PriList(*data.PRILIST))
    assert data.PRILIST == astuple(PriList(*data.PRILIST))
    assert data.NESTED_PRILIST_TUPLE == to_tuple(NestedPriList(*data.NESTED_PRILIST))
    assert data.NESTED_PRILIST_TUPLE == astuple(NestedPriList(*data.NESTED_PRILIST))


def test_se_func_iter():
    # Primitives
    assert (10,) == to_tuple(Int(10))
    assert (10.0,) == to_tuple(Float(10.0))
    assert ("10",) == to_tuple(Str("10"))
    assert (False,) == to_tuple(Bool(False))

    assert (10, '10', 10.0, False) == to_tuple(Pri(10, "10", 10.0, False))
    assert ((10,),) == to_tuple(NestedInt(Int(10)))
    assert ((10,), ('10',), (10.0,), (True,)) == to_tuple(NestedPri(Int(10), Str("10"), Float(10.0), Bool(True)))

    # List
    assert ([10], ['10'], [10.0], [False]) == to_tuple(PriList([10], ["10"], [10.0], [False]))
    assert ([(10,)], [('10',)], [(10.0,)], [(False,)]) == to_tuple(
        NestedPriList([Int(10)], [Str("10")], [Float(10.0)], [Bool(False)])
    )

    # Dict
    assert ({'i': 10}, {'s': '10'}, {'f': 10.0}, {'b': False}) == to_tuple(
        PriDict({'i': 10}, {'s': "10"}, {'f': 10.0}, {'b': False})
    )
    assert ({'i': 10}, {'s': '10'}, {'f': 10.0}, {'b': False}) == to_tuple(
        PriDict({'i': 10}, {'s': "10"}, {'f': 10.0}, {'b': False})
    )
    assert ({('i',): (10,)}, {('i',): ('10',)}, {('i',): (10.0,)}, {('i',): (True,)}) == to_tuple(
        NestedPriDict({Str('i'): Int(10)}, {Str('i'): Str('10')}, {Str('i'): Float(10.0)}, {Str('i'): Bool(True)})
    )

    # Tuple
    exp = (
        (10, 10, 10),
        ('10', '10', '10', '10'),
        (10.0, 10.0, 10.0, 10.0, 10.0),
        (False, False, False, False, False, False),
    )
    act = to_tuple(
        PriTuple(
            (10, 10, 10),
            ("10", "10", "10", "10"),
            (10.0, 10.0, 10.0, 10.0, 10.0),
            (False, False, False, False, False, False),
        )
    )
    assert exp == act

    exp = (
        ((10,), (10,), (10,)),
        (('10',), ('10',), ('10',), ('10',)),
        ((10.0,), (10.0,), (10.0,), (10.0,), (10.0,)),
        ((False,), (False,), (False,), (False,), (False,), (False,)),
    )
    act = to_tuple(
        NestedPriTuple(
            (Int(10), Int(10), Int(10)),
            (Str("10"), Str("10"), Str("10"), Str("10")),
            (Float(10.0), Float(10.0), Float(10.0), Float(10.0), Float(10.0)),
            (Bool(False), Bool(False), Bool(False), Bool(False), Bool(False), Bool(False)),
        )
    )
    assert exp == act

    # Optional
    assert (10, '10', 10.0, False) == to_tuple(PriOpt(10, "10", 10.0, False))


def test_convert_sets_option():
    @serialize
    class A:
        v: Set[str]

    a = A({"a", "b"})

    a_json = to_json(a)
    # sets are unordered so the list order is not stable
    assert a_json == '{"v": ["a", "b"]}' or a_json == '{"v": ["b", "a"]}'

    a_msgpack = to_msgpack(a)
    # sets are unordered so the list order is not stable
    assert a_msgpack == b'\x81\xa1v\x92\xa1a\xa1b' or a_msgpack == b'\x81\xa1v\x92\xa1b\xa1a'

    a_dict = to_dict(a, convert_sets=True)
    # sets are unordered so the list order is not stable
    assert a_dict == {"v": ["a", "b"]} or a_dict == {"v": ["b", "a"]}

    assert {"v": {"a", "b"}} == to_dict(a, convert_sets=False)
