"""
Additional type support such as Decimal.
"""
from typing import Any

from .core import SerdeError


def serialize(data: Any) -> Any:
    """
    Custom serializer for extended types such as Decimal.

    `data` shall be other than List, Dict, Tuple, Optional
    Union, dataclass or primitives.
    """

    raise SerdeError(f'Unsupported type: {type(data)}')


def deserialize(typ: Any, data: Any) -> Any:
    """
    Custom deserializer for extended types such as Decimal.

    `data` shall be other than List, Dict, Tuple, Optional
    Union, dataclass or primitives.
    """

    raise SerdeError(f'Unsupported type: {type(data)}')
