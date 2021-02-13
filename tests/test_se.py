from dataclasses import dataclass
from typing import Set

from serde import asdict, astuple, serialize, to_dict, to_tuple
from serde.json import to_json
from serde.msgpack import to_msgpack

from . import data
from .data import (Bool, Float, Int, NestedInt, NestedPri, NestedPriDict, NestedPriList, NestedPriTuple, Pri, PriDict,
                   PriList, PriOpt, PriTuple, Str)


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
    assert (10,) == Int(10).__serde_to_iter__()
    assert (10.0,) == Float(10.0).__serde_to_iter__()
    assert ("10",) == Str("10").__serde_to_iter__()
    assert (False,) == Bool(False).__serde_to_iter__()

    assert (10, '10', 10.0, False) == Pri(10, "10", 10.0, False).__serde_to_iter__()
    assert ((10,),) == NestedInt(Int(10)).__serde_to_iter__()
    assert ((10,), ('10',), (10.0,), (True,)) == NestedPri(
        Int(10), Str("10"), Float(10.0), Bool(True)
    ).__serde_to_iter__()

    # List
    assert ([10], ['10'], [10.0], [False]) == PriList([10], ["10"], [10.0], [False]).__serde_to_iter__()
    assert ([(10,)], [('10',)], [(10.0,)], [(False,)]) == NestedPriList(
        [Int(10)], [Str("10")], [Float(10.0)], [Bool(False)]
    ).__serde_to_iter__()

    # Dict
    assert ({'i': 10}, {'s': '10'}, {'f': 10.0}, {'b': False}) == PriDict(
        {'i': 10}, {'s': "10"}, {'f': 10.0}, {'b': False}
    ).__serde_to_iter__()
    assert ({'i': 10}, {'s': '10'}, {'f': 10.0}, {'b': False}) == PriDict(
        {'i': 10}, {'s': "10"}, {'f': 10.0}, {'b': False}
    ).__serde_to_iter__()
    assert ({('i',): (10,)}, {('i',): ('10',)}, {('i',): (10.0,)}, {('i',): (True,)}) == NestedPriDict(
        {Str('i'): Int(10)}, {Str('i'): Str('10')}, {Str('i'): Float(10.0)}, {Str('i'): Bool(True)}
    ).__serde_to_iter__()

    # Tuple
    exp = (
        (10, 10, 10),
        ('10', '10', '10', '10'),
        (10.0, 10.0, 10.0, 10.0, 10.0),
        (False, False, False, False, False, False),
    )
    act = PriTuple(
        (10, 10, 10),
        ("10", "10", "10", "10"),
        (10.0, 10.0, 10.0, 10.0, 10.0),
        (False, False, False, False, False, False),
    ).__serde_to_iter__()
    assert act == act

    exp = (
        ((10,), (10,), (10,)),
        (('10',), ('10',), ('10',), ('10',)),
        ((10.0,), (10.0,), (10.0,), (10.0,), (10.0,)),
        ((False,), (False,), (False,), (False,), (False,), (False,)),
    )
    act = NestedPriTuple(
        (Int(10), Int(10), Int(10)),
        (Str("10"), Str("10"), Str("10"), Str("10")),
        (Float(10.0), Float(10.0), Float(10.0), Float(10.0), Float(10.0)),
        (Bool(False), Bool(False), Bool(False), Bool(False), Bool(False), Bool(False)),
    ).__serde_to_iter__()
    assert exp == act

    # Optional
    assert (10, '10', 10.0, False) == PriOpt(10, "10", 10.0, False).__serde_to_iter__()


def test_convert_sets_option():
    @serialize
    @dataclass
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
