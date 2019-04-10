import functools
from typing import Any, Type

from .core import SE_NAME, T


class Serializer:
    def serialize(self, obj: Any) -> Any:
        pass


def serialize(_cls: Type[T]) -> Type[T]:
    """
    `serialize` decorator.
    """

    @functools.wraps(_cls)
    def wrap(cls: Type[T]) -> Type[T]:
        def serialize(self, ser, **opts) -> None:
            return ser().serialize(self, **opts)

        setattr(cls, SE_NAME, serialize)
        return cls

    return wrap(_cls)


def is_serializable(instance_or_class: Any) -> bool:
    """
    Test if `instance_or_class` is serializable.
    """
    return hasattr(instance_or_class, '__serde_serialize__')
