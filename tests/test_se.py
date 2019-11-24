from serde import asdict, astuple

from . import data
from .data import (Bool, Float, Int, NestedInt, NestedPri, NestedPriDict, NestedPriList, NestedPriTuple, Pri, PriDict,
                   PriList, PriOpt, PriTuple, Str)


def test_asdict():
    p = Pri(10, 'foo', 100.0, True)
    assert {'b': True, 'f': 100.0, 'i': 10, 's': 'foo'} == asdict(p)


def test_astuple():
    assert data.PRI_TUPLE == astuple(data.PRI)
    assert data.PRILIST == astuple(PriList(*data.PRILIST))
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
    assert (
        (
            (10, 10, 10),
            ('10', '10', '10', '10'),
            (10.0, 10.0, 10.0, 10.0, 10.0),
            (False, False, False, False, False, False),
        )
        == PriTuple(
            (10, 10, 10),
            ("10", "10", "10", "10"),
            (10.0, 10.0, 10.0, 10.0, 10.0),
            (False, False, False, False, False, False),
        ).__serde_to_iter__()
    )
    assert (
        (
            ((10,), (10,), (10,)),
            (('10',), ('10',), ('10',), ('10',)),
            ((10.0,), (10.0,), (10.0,), (10.0,), (10.0,)),
            ((False,), (False,), (False,), (False,), (False,), (False,)),
        )
        == NestedPriTuple(
            (Int(10), Int(10), Int(10)),
            (Str("10"), Str("10"), Str("10"), Str("10")),
            (Float(10.0), Float(10.0), Float(10.0), Float(10.0), Float(10.0)),
            (Bool(False), Bool(False), Bool(False), Bool(False), Bool(False), Bool(False)),
        ).__serde_to_iter__()
    )

    # Optional
    assert (10, '10', 10.0, False) == PriOpt(10, "10", 10.0, False).__serde_to_iter__()
