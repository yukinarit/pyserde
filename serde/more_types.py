"""
Additional type support such as Decimal.
"""
from dataclasses import Field
from decimal import Decimal
from pathlib import Path
from typing import Any

from .core import SerdeError


def serialize(data: Any) -> Any:
    """
    Custom serializer for extended types such as Decimal.

    `data` shall be other than List, Dict, Tuple, Optional
    Union, dataclass or primitives.
    """
    if isinstance(data, Decimal):
        return str(data)
    elif isinstance(data, Path):
        return str(data)
    else:
        raise SerdeError(f'Unsupported type: {type(data)}')


def deserialize(field: Field, data: Any) -> Any:
    """
    Custom deserializer for extended types such as Decimal.

    `data` shall be other than List, Dict, Tuple, Optional
    Union, dataclass or primitives.
    """
    if issubclass(field.type, Decimal):
        return Decimal(data)
    elif issubclass(field.type, Path):
        return Path(data)
    else:
        raise SerdeError(f'Unsupported type: {type(data)}')
