from decimal import Decimal
from typing import Union
from serde.de import from_obj


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
