from collections.abc import Sequence, MutableSequence

from serde import asdict, astuple, serialize, to_dict, to_tuple
from serde.json import to_json
from serde.msgpack import to_msgpack
from serde.se import SeField, Renderer
from serde.core import TO_ITER

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


def test_asdict() -> None:
    p = Pri(10, "foo", 100.0, True)
    assert {"b": True, "f": 100.0, "i": 10, "s": "foo"} == to_dict(p)
    assert {"b": True, "f": 100.0, "i": 10, "s": "foo"} == asdict(p)


def test_astuple() -> None:
    assert data.PRI_TUPLE == to_tuple(data.PRI)
    assert data.PRI_TUPLE == astuple(data.PRI)
    assert data.PRILIST == to_tuple(PriList(*data.PRILIST))
    assert data.PRILIST == astuple(PriList(*data.PRILIST))
    assert data.NESTED_PRILIST_TUPLE == to_tuple(NestedPriList(*data.NESTED_PRILIST))
    assert data.NESTED_PRILIST_TUPLE == astuple(NestedPriList(*data.NESTED_PRILIST))


def test_se_func_iter() -> None:
    # Primitives
    assert (10,) == to_tuple(Int(10))
    assert (10.0,) == to_tuple(Float(10.0))
    assert ("10",) == to_tuple(Str("10"))
    assert (False,) == to_tuple(Bool(False))

    assert (10, "10", 10.0, False) == to_tuple(Pri(10, "10", 10.0, False))
    assert ((10,),) == to_tuple(NestedInt(Int(10)))
    assert ((10,), ("10",), (10.0,), (True,)) == to_tuple(
        NestedPri(Int(10), Str("10"), Float(10.0), Bool(True))
    )

    # List
    assert ([10], ["10"], [10.0], [False]) == to_tuple(PriList([10], ["10"], [10.0], [False]))
    assert ([(10,)], [("10",)], [(10.0,)], [(False,)]) == to_tuple(
        NestedPriList([Int(10)], [Str("10")], [Float(10.0)], [Bool(False)])
    )

    # Dict
    assert ({"i": 10}, {"s": "10"}, {"f": 10.0}, {"b": False}) == to_tuple(
        PriDict({"i": 10}, {"s": "10"}, {"f": 10.0}, {"b": False})
    )
    assert ({"i": 10}, {"s": "10"}, {"f": 10.0}, {"b": False}) == to_tuple(
        PriDict({"i": 10}, {"s": "10"}, {"f": 10.0}, {"b": False})
    )
    assert ({("i",): (10,)}, {("i",): ("10",)}, {("i",): (10.0,)}, {("i",): (True,)}) == to_tuple(
        NestedPriDict(
            {Str("i"): Int(10)},  # pyright: ignore[reportUnhashable]
            {Str("i"): Str("10")},  # pyright: ignore[reportUnhashable]
            {Str("i"): Float(10.0)},  # pyright: ignore[reportUnhashable]
            {Str("i"): Bool(True)},  # pyright: ignore[reportUnhashable]
        )
    )

    # tuple
    exp = (
        (10, 10, 10),
        ("10", "10", "10", "10"),
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
        (("10",), ("10",), ("10",), ("10",)),
        ((10.0,), (10.0,), (10.0,), (10.0,), (10.0,)),
        ((False,), (False,), (False,), (False,), (False,), (False,)),
    )  # type: ignore
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
    assert (10, "10", 10.0, False) == to_tuple(PriOpt(10, "10", 10.0, False))


def test_convert_sets_option() -> None:
    @serialize
    class A:
        v: set[str]

    a = A({"a", "b"})

    a_json = to_json(a)
    # sets are unordered so the list order is not stable
    assert a_json == '{"v":["a","b"]}' or a_json == '{"v":["b","a"]}'

    a_msgpack = to_msgpack(a)
    # sets are unordered so the list order is not stable
    assert a_msgpack == b"\x81\xa1v\x92\xa1a\xa1b" or a_msgpack == b"\x81\xa1v\x92\xa1b\xa1a"

    a_dict = to_dict(a, convert_sets=True)
    # sets are unordered so the list order is not stable
    assert a_dict == {"v": ["a", "b"]} or a_dict == {"v": ["b", "a"]}

    assert {"v": {"a", "b"}} == to_dict(a, convert_sets=False)


@serialize
class Foo:
    val: int


kwargs = "reuse_instances=reuse_instances, convert_sets=convert_sets, skip_none=skip_none"


def test_render_primitives() -> None:
    rendered = Renderer(TO_ITER).render(SeField(int, "i"))
    assert rendered == 'coerce_object("None", "i", int, i)'


def test_render_list() -> None:

    rendered = Renderer(TO_ITER).render(SeField(list[int], "l"))
    assert rendered == '[coerce_object("None", "v", int, v) for v in l]'

    rendered = Renderer(TO_ITER).render(SeField(list[Foo], "foo"))
    assert rendered == f"[v.__serde__.funcs['to_iter'](v, {kwargs}) for v in foo]"

    rendered = Renderer(TO_ITER).render(SeField(Sequence[int], "l"))
    assert rendered == '[coerce_object("None", "v", int, v) for v in l]'

    rendered = Renderer(TO_ITER).render(SeField(Sequence, "l"))
    assert rendered == "list(l)"

    rendered = Renderer(TO_ITER).render(SeField(MutableSequence[int], "l"))
    assert rendered == '[coerce_object("None", "v", int, v) for v in l]'

    rendered = Renderer(TO_ITER).render(SeField(MutableSequence, "l"))
    assert rendered == "list(l)"


def test_render_dict() -> None:
    rendered = Renderer(TO_ITER).render(SeField(dict[str, Foo], "foo"))
    rendered_key = 'coerce_object("None", "k", str, k)'
    rendered_val = f"v.__serde__.funcs['to_iter'](v, {kwargs})"
    assert rendered == f"{{{rendered_key}: {rendered_val} for k, v in foo.items()}}"

    rendered = Renderer(TO_ITER).render(SeField(dict[Foo, Foo], "foo"))
    rendered_key = f"k.__serde__.funcs['to_iter'](k, {kwargs})"
    rendered_val = f"v.__serde__.funcs['to_iter'](v, {kwargs})"
    assert rendered == f"{{{rendered_key}: {rendered_val} for k, v in foo.items()}}"


def test_render_tuple() -> None:
    rendered = Renderer(TO_ITER).render(SeField(tuple[str, Foo, int], "foo"))
    rendered_str = 'coerce_object("None", "foo[0]", str, foo[0])'
    rendered_foo = f"foo[1].__serde__.funcs['to_iter'](foo[1], {kwargs})"
    rendered_int = 'coerce_object("None", "foo[2]", int, foo[2])'
    assert rendered == f"({rendered_str}, {rendered_foo}, {rendered_int},)"


def test_render_dataclass() -> None:
    rendered = Renderer(TO_ITER).render(SeField(Foo, "foo"))
    rendered_foo = f"foo.__serde__.funcs['to_iter'](foo, {kwargs})"
    assert rendered_foo == rendered
