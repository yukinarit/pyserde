from dataclasses import Field
from decimal import Decimal
from typing import Any

from .core import SerdeError


def serialize(data: Any) -> Any:
    if isinstance(data, Decimal):
        return str(data)
    else:
        raise SerdeError(f'Unsupported type: {type(data)}')


def deserialize(field: Field, data: Any) -> Any:
    if issubclass(field.type, Decimal):
        return Decimal(data)
    else:
        raise SerdeError(f'Unsupported type: {type(data)}')
