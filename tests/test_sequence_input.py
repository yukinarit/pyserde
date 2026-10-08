import json
from collections.abc import MutableSequence, Sequence
from typing import Any, Generic, TypeVar

import pytest
from plum import dispatch

try:
    from typing import TypeAliasType
except ImportError:
    from typing_extensions import TypeAliasType

import serde
from serde.json import from_json

SEQUENCE_TYPES = [
    list,
    list[str],
    Sequence,
    Sequence[str],
    MutableSequence,
    MutableSequence[str],
    tuple,
    tuple[str, ...],
    tuple[str, str],
]
BAD_INPUTS = [{"first": "discarded", "second": "discarded"}, "ab", {}, ""]
Strings = TypeAliasType("Strings", list[str])
T = TypeVar("T")


@pytest.mark.parametrize("type_check", [None, serde.strict])
@pytest.mark.parametrize("typ", SEQUENCE_TYPES)
@pytest.mark.parametrize("value", BAD_INPUTS)
def test_strict_sequences_reject_objects_and_strings(type_check: Any, typ: Any, value: Any) -> None:
    options = {} if type_check is None else {"type_check": type_check}

    @serde.serde(**options)
    class Config:
        values: typ  # pyright: ignore[reportInvalidTypeForm]

    with pytest.raises(serde.SerdeError):
        from_json(Config, json.dumps({"values": value}))


@pytest.mark.parametrize("typ", SEQUENCE_TYPES)
def test_strict_sequences_accept_arrays(typ: Any) -> None:
    @serde.serde
    class Config:
        values: typ  # pyright: ignore[reportInvalidTypeForm]

    restored = from_json(Config, '{"values":["a","b"]}')
    assert list(restored.values) == ["a", "b"]
    assert isinstance(
        restored.values, tuple if typ in (tuple, tuple[str, ...], tuple[str, str]) else list
    )


@pytest.mark.parametrize("typ", SEQUENCE_TYPES[:-1])
def test_strict_sequences_accept_empty_arrays(typ: Any) -> None:
    @serde.serde
    class Config:
        values: typ  # pyright: ignore[reportInvalidTypeForm]

    assert list(from_json(Config, '{"values":[]}').values) == []


@pytest.mark.parametrize("type_check", [serde.coerce, serde.disabled])
@pytest.mark.parametrize("typ", [list[str], Sequence[str], tuple[str, ...]])
@pytest.mark.parametrize("value", BAD_INPUTS)
def test_non_strict_sequences_keep_iterable_conversion(
    type_check: Any, typ: Any, value: Any
) -> None:
    @serde.serde(type_check=type_check)
    class Config:
        values: typ  # pyright: ignore[reportInvalidTypeForm]

    assert list(from_json(Config, json.dumps({"values": value})).values) == list(value)


@pytest.mark.parametrize(
    "typ,value",
    [
        (list[list[str]], [{"first": "discarded"}]),
        (dict[str, list[str]], {"group": "ab"}),
        (tuple[list[str], int], [{"first": "discarded"}, 1]),
        (list[str] | None, "ab"),
    ],
)
def test_nested_sequences_check_input_before_conversion(typ: Any, value: Any) -> None:
    @serde.serde
    class Config:
        values: typ  # pyright: ignore[reportInvalidTypeForm]

    with pytest.raises(serde.SerdeError):
        from_json(Config, json.dumps({"values": value}))


def test_optional_nested_sequences_keep_valid_values() -> None:
    @serde.serde
    class Config:
        values: list[list[str]] | None

    assert from_json(Config, '{"values":[["a","b"],[]]}').values == [["a", "b"], []]
    assert from_json(Config, '{"values":null}').values is None


@pytest.mark.parametrize("type_check", [serde.strict, serde.coerce, serde.disabled])
def test_sequence_union_preserves_non_sequence_branch(type_check: Any) -> None:
    @serde.serde(type_check=type_check)
    class Text:
        value: list[str] | str

    @serde.serde(type_check=type_check)
    class Object:
        value: list[str] | dict[str, str]

    text = from_json(Text, '{"value":"ab"}').value
    obj = from_json(Object, '{"value":{"first":"retained"}}').value
    if type_check is serde.strict:
        assert text == "ab"
        assert obj == {"first": "retained"}
    else:
        assert text == ["a", "b"]
        assert obj == ["first"]


@pytest.mark.parametrize("first_strict", [True, False])
def test_generic_union_cache_does_not_share_sequence_check_mode(first_strict: bool) -> None:
    modes = [serde.strict, serde.disabled]
    if not first_strict:
        modes.reverse()
    classes = []
    for mode in modes:

        @serde.serde(type_check=mode)
        class Config(Generic[T]):
            value: T

        classes.append((mode, Config))

    for _ in range(2):
        for mode, cls in classes:
            value = from_json(cls[list[str] | str], '{"value":"ab"}').value
            assert value == ("ab" if mode is serde.strict else ["a", "b"])


@pytest.mark.parametrize("type_check", [serde.strict, serde.coerce, serde.disabled])
def test_generic_sequence_input_respects_class_mode(type_check: Any) -> None:
    @serde.serde(type_check=type_check)
    class Config(Generic[T]):
        values: T

    if type_check is serde.strict:
        with pytest.raises(serde.SerdeError):
            from_json(Config[list[str]], '{"values":{"first":"discarded"}}')
    else:
        assert from_json(Config[list[str]], '{"values":{"first":"discarded"}}').values == ["first"]
    assert from_json(Config[list[str]], '{"values":["a","b"]}').values == ["a", "b"]


def test_sequence_type_alias_checks_input() -> None:
    @serde.serde
    class Config:
        values: Strings

    with pytest.raises(serde.SerdeError):
        from_json(Config, '{"values":{"first":"discarded"}}')
    assert from_json(Config, '{"values":["a","b"]}').values == ["a", "b"]


def test_custom_sequence_deserializer_can_accept_a_string() -> None:
    @serde.serde
    class Config:
        values: list[str] = serde.field(deserializer=lambda value: value.split(","))

    assert from_json(Config, '{"values":"a,b"}').values == ["a", "b"]


def test_custom_sequence_class_deserializer_can_accept_an_object() -> None:
    class Deserializer(serde.ClassDeserializer):
        @dispatch
        def deserialize(self, cls: type[list], value: Any) -> list:
            return list(value.values())

    @serde.serde(class_deserializer=Deserializer())
    class Config:
        values: list

    assert from_json(Config, '{"values":{"first":"retained"}}').values == ["retained"]


def test_legacy_deserializer_fallback_checks_sequence_input() -> None:
    def fallback(_cls: Any, _value: Any) -> Any:
        raise serde.SerdeSkip()

    @serde.serde(deserializer=fallback)
    class Config:
        values: list[str]

    with pytest.raises(serde.SerdeError):
        from_json(Config, '{"values":"ab"}')
    assert from_json(Config, '{"values":["a","b"]}').values == ["a", "b"]


def test_strict_sequences_keep_other_iterable_inputs() -> None:
    @serde.serde
    class Config:
        values: list[int]

    assert serde.from_dict(Config, {"values": range(3)}).values == [0, 1, 2]
    assert serde.from_dict(Config, {"values": iter([0, 1, 2])}).values == [0, 1, 2]


@pytest.mark.parametrize("type_check", [serde.strict, serde.coerce, serde.disabled])
@pytest.mark.parametrize("typ", [list[int], tuple[int, ...]])
@pytest.mark.parametrize("value", [b"ab", bytearray(b"ab")])
def test_byte_sequences_respect_check_mode(type_check: Any, typ: Any, value: Any) -> None:
    @serde.serde(type_check=type_check)
    class Config:
        values: typ  # pyright: ignore[reportInvalidTypeForm]

    if type_check is serde.strict:
        with pytest.raises(serde.SerdeError):
            serde.from_dict(Config, {"values": value})
    else:
        assert list(serde.from_dict(Config, {"values": value}).values) == [97, 98]


@pytest.mark.parametrize("type_check", [serde.strict, serde.coerce, serde.disabled])
def test_iter_based_sequence_input_respects_check_mode(type_check: Any) -> None:
    @serde.serde(type_check=type_check)
    class Config:
        values: list[str]

    if type_check is serde.strict:
        with pytest.raises(serde.SerdeError):
            serde.from_tuple(Config, ("ab",))
    else:
        assert serde.from_tuple(Config, ("ab",)).values == ["a", "b"]
    assert serde.from_tuple(Config, (["a", "b"],)).values == ["a", "b"]


def test_aliased_optional_sequence_checks_input() -> None:
    @serde.serde
    class Config:
        values: list[str] | None = serde.field(alias=["input"])

    with pytest.raises(serde.SerdeError):
        from_json(Config, '{"input":"ab"}')
    assert from_json(Config, '{"input":["a","b"]}').values == ["a", "b"]
    assert from_json(Config, '{"input":null}').values is None
