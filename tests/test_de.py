from typing import Tuple, Union

from serde.de import from_obj


def test_from_obj():
    assert None == from_obj(int, None, False, True)
    assert "a" == from_obj(Union[int, str], "a", False, True)
    assert ("a", "b") == from_obj(Tuple[str, str], ("a", "b"), False, True)
