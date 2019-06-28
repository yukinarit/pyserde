"""
Defines classess and functions for `serialize` decorator.

"""
import abc
import functools
from typing import Any, Type

from .core import SE_NAME, T, Hidden, HIDDEN_NAME


class Serializer(metaclass=abc.ABCMeta):
    """
    `Serializer` base class. Subclass this to custonize serialize bahaviour.

    See `serde.json.JsonSerializer` and `serde.msgpack.MsgPackSerializer` for example usage.
    """
    @abc.abstractclassmethod
    def serialize(self, obj):
        pass


def serialize(_cls: Type[T]) -> Type[T]:
    """
    `serialize` decorator. A dataclass with this decorator can be serialized
    into an object in various data format such as JSON and MsgPack.

    >>> from dataclasses import dataclass
    >>> from serde import serialize
    >>> from serde.json import to_json
    >>>
    >>> # Mark the class serializable.
    >>> @serialize
    ... @dataclass
    ... class Hoge:
    ...     i: int
    ...     s: str
    ...     f: float
    ...     b: bool
    >>>
    >>> to_json(Hoge(i=10, s='hoge', f=100.0, b=True))
    '{"i": 10, "s": "hoge", "f": 100.0, "b": true}'
    >>>
    """
    @functools.wraps(_cls)
    def wrap(cls: Type[T]) -> Type[T]:
        if not hasattr(cls, HIDDEN_NAME):
            setattr(cls, HIDDEN_NAME, Hidden())
        def serialize(self, ser, **opts) -> None:
            return ser().serialize(self, **opts)

        setattr(cls, SE_NAME, serialize)
        return cls

    return wrap(_cls)


def is_serializable(instance_or_class: Any) -> bool:
    """
    Test if arg can `serialize`. Arg must be either an instance of class.

    >>> from dataclasses import dataclass
    >>> from serde import serialize, is_serializable
    >>>
    >>> @serialize
    ... @dataclass
    ... class Hoge:
    ...     pass
    >>>
    >>> is_serializable(Hoge)
    True
    >>>
    """
    return hasattr(instance_or_class, '__serde_serialize__')
