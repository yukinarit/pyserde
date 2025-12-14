import pytest
from collections.abc import Sequence, MutableSequence
from decimal import Decimal
from typing import Union, Optional
from serde import serde, SerdeError, field
from serde.json import from_json
from serde.de import deserialize, from_obj, from_dict, Renderer, DeField


def test_from_obj() -> None:
    # Primitive
    assert 10 == from_obj(int, 10, False, False)

    # Union
    assert "a" == from_obj(Union[int, str], "a", False, False)  # type: ignore

    # tuple
    assert ("a", "b") == from_obj(tuple[str, str], ("a", "b"), False, False)

    # pyserde converts to the specified type
    assert 10 == from_obj(int, "10", False, False)

    # pyserde can converts for container types e.g. tuple, List etc.
    assert (1, 2) == from_obj(tuple[int, int], ("1", "2"), False, False)

    # Decimal
    dec = from_obj(list[Decimal], ("0.1", 0.1), False, False)
    assert isinstance(dec[0], Decimal) and dec[0] == Decimal("0.1")
    assert isinstance(dec[1], Decimal) and dec[1] == Decimal(0.1)


kwargs = (
    "maybe_generic=maybe_generic, maybe_generic_type_vars=maybe_generic_type_vars, "
    "variable_type_args=None, reuse_instances=reuse_instances, "
    "deserialize_numbers=deserialize_numbers"
)


def test_deserialize_numbers_option() -> None:
    def coerce_numbers(val: Union[str, int]) -> float:
        if isinstance(val, bool):
            raise SerdeError("bool not allowed")
        return float(val)

    @serde
    class Foo:
        value: float
        values: list[float]

    foo = from_dict(
        Foo,
        {"value": "1.0", "values": ["1", 2]},
        deserialize_numbers=coerce_numbers,
    )
    assert foo.value == 1.0
    assert foo.values == [1.0, 2.0]

    with pytest.raises(SerdeError):
        from_dict(
            Foo,
            {"value": True, "values": []},
            deserialize_numbers=coerce_numbers,
        )


def test_render_primitives() -> None:

    rendered = Renderer("foo").render(DeField(int, "i", datavar="data"))
    assert rendered == 'coerce_object("None", "i", int, data["i"])'

    rendered = Renderer("foo").render(DeField(int, "int_field", datavar="data", case="camelcase"))
    assert rendered == 'coerce_object("None", "int_field", int, data["intField"])'

    rendered = Renderer("foo").render(DeField(int, "i", datavar="data", index=1, iterbased=True))
    assert rendered == 'coerce_object("None", "i", int, data[1])'


def test_render_list() -> None:
    rendered = Renderer("foo").render(DeField(list[int], "l", datavar="data"))
    assert rendered == '[coerce_object("None", "v", int, v) for v in data["l"]]'

    rendered = Renderer("foo").render(DeField(list[list[int]], "l", datavar="data"))
    assert rendered == '[[coerce_object("None", "v", int, v) for v in v] for v in data["l"]]'

    rendered = Renderer("foo").render(DeField(Sequence[int], "l", datavar="data"))
    assert rendered == '[coerce_object("None", "v", int, v) for v in data["l"]]'

    rendered = Renderer("foo").render(DeField(Sequence, "l", datavar="data"))
    assert rendered == 'list(data["l"])'

    rendered = Renderer("foo").render(DeField(MutableSequence[int], "l", datavar="data"))
    assert rendered == '[coerce_object("None", "v", int, v) for v in data["l"]]'

    rendered = Renderer("foo").render(DeField(MutableSequence, "l", datavar="data"))
    assert rendered == 'list(data["l"])'


def test_render_tuple() -> None:
    @deserialize
    class Foo:
        pass

    rendered = Renderer("foo").render(DeField(tuple[str, int, list[int], Foo], "d", datavar="data"))
    rendered_str = 'coerce_object("None", "data[\\"d\\"][0]", str, data["d"][0])'
    rendered_int = 'coerce_object("None", "data[\\"d\\"][1]", int, data["d"][1])'
    rendered_lst = '[coerce_object("None", "v", int, v) for v in data["d"][2]]'
    rendered_foo = f"Foo.__serde__.funcs['foo'](data=data[\"d\"][3], {kwargs})"
    assert rendered == f"({rendered_str}, {rendered_int}, {rendered_lst}, {rendered_foo},)"

    field = DeField(tuple[str, int, list[int], Foo], "d", datavar="data", index=0, iterbased=True)
    rendered = Renderer("foo").render(field)
    rendered_str = 'coerce_object("None", "data[0][0]", str, data[0][0])'
    rendered_int = 'coerce_object("None", "data[0][1]", int, data[0][1])'
    rendered_lst = '[coerce_object("None", "v", int, v) for v in data[0][2]]'
    rendered_foo = f"Foo.__serde__.funcs['foo'](data=data[0][3], {kwargs})"
    assert rendered == f"({rendered_str}, {rendered_int}, {rendered_lst}, {rendered_foo},)"


def test_render_dict() -> None:
    rendered = Renderer("foo").render(DeField(dict[str, int], "d", datavar="data"))
    rendered_key = 'coerce_object("None", "k", str, k)'
    rendered_val = 'coerce_object("None", "v", int, v)'
    rendered_dct = f'{{{rendered_key}: {rendered_val} for k, v in data["d"].items()}}'
    assert rendered == rendered_dct

    @deserialize
    class Foo:
        pass

    rendered = Renderer("foo").render(DeField(dict[Foo, list[Foo]], "f", datavar="data"))
    rendered_key = f"Foo.__serde__.funcs['foo'](data=k, {kwargs})"
    rendered_val = f"[Foo.__serde__.funcs['foo'](data=v, {kwargs}) for v in v]"

    assert rendered == f'{{{rendered_key}: {rendered_val} for k, v in data["f"].items()}}'


def test_render_set() -> None:
    from typing import Set

    rendered = Renderer("foo").render(DeField(Set[int], "l", datavar="data"))
    assert rendered == 'set(coerce_object("None", "v", int, v) for v in data["l"])'

    rendered = Renderer("foo").render(DeField(Set[Set[int]], "l", datavar="data"))
    assert rendered == 'set(set(coerce_object("None", "v", int, v) for v in v) for v in data["l"])'


def test_render_opt() -> None:
    rendered = Renderer("foo").render(DeField(Optional[int], "o", datavar="data"))  # type: ignore
    rendered_opt = (
        '(coerce_object("None", "o", int, data["o"])) if data.get("o") is not None else None'
    )
    assert rendered == rendered_opt

    rendered = Renderer("foo").render(DeField(Optional[list[int]], "o", datavar="data"))  # type: ignore
    rendered_lst = '[coerce_object("None", "v", int, v) for v in data["o"]]'
    rendered_opt = f'({rendered_lst}) if data.get("o") is not None else None'
    assert rendered == rendered_opt

    rendered = Renderer("foo").render(DeField(Optional[list[int]], "o", datavar="data"))  # type: ignore
    rendered_lst = '[coerce_object("None", "v", int, v) for v in data["o"]]'
    rendered_opt = f'({rendered_lst}) if data.get("o") is not None else None'
    assert rendered == rendered_opt

    @deserialize
    class Foo:
        a: Optional[list[int]]

    rendered = Renderer("foo").render(DeField(Optional[Foo], "f", datavar="data"))  # type: ignore
    rendered_foo = f"Foo.__serde__.funcs['foo'](data=data[\"f\"], {kwargs})"
    rendered_opt = f'({rendered_foo}) if data.get("f") is not None else None'
    assert rendered == rendered_opt


def test_deny_unknown_fields() -> None:
    @serde(deny_unknown_fields=True)
    class Foo:
        a: int
        b: str

    with pytest.raises(SerdeError):
        from_json(Foo, '{"a": 10, "b": "foo", "c": 100.0, "d": true}')

    f = from_json(Foo, '{"a": 10, "b": "foo"}')
    assert f.a == 10
    assert f.b == "foo"


def test_deny_renamed_unknown_fields() -> None:
    @serde(deny_unknown_fields=True)
    class Foo:
        a: int
        b: str = field(rename="B")

    with pytest.raises(SerdeError):
        from_json(Foo, '{"a": 10, "b": "foo"}')

    f = from_json(Foo, '{"a": 10, "B": "foo"}')
    assert f.a == 10
    assert f.b == "foo"

    @serde(rename_all="constcase", deny_unknown_fields=True)
    class Bar:
        a: int
        b: str

    with pytest.raises(SerdeError):
        from_json(Bar, '{"a": 10, "b": "foo"}')

    b = from_json(Bar, '{"A": 10, "B": "foo"}')
    assert b.a == 10
    assert b.b == "foo"


def test_deny_aliased_unknown_fields() -> None:
    @serde(deny_unknown_fields=True)
    class Foo:
        a: int
        b: str = field(alias=["B"])  # type: ignore

    with pytest.raises(SerdeError):
        from_json(Foo, '{"a": 10, "b": "foo", "c": 100.0, "d": true}')

    f = from_json(Foo, '{"a": 10, "b": "foo"}')
    assert f.a == 10
    assert f.b == "foo"

    f = from_json(Foo, '{"a": 10, "B": "foo"}')
    assert f.a == 10
    assert f.b == "foo"
