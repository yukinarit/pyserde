"""
Defines classess and functions for `serialize` decorator.

"""
import abc
import functools
from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple, Type

from .core import HIDDEN_NAME, SE_NAME, Hidden, T


class Serializer(metaclass=abc.ABCMeta):
    """
    `Serializer` base class. Subclass this to custonize serialize bahaviour.

    See `serde.json.JsonSerializer` and `serde.msgpack.MsgPackSerializer` for example usage.
    """

    @abc.abstractclassmethod
    def serialize(self, obj):
        pass


def serialize(_cls=None) -> Type[T]:
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

    if _cls is None:
        return wrap

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


def to_dict(o) -> Dict:
    """
    Convert object into dictionary.

    >>> @serialize
    ... @dataclass
    ... class Hoge:
    ...     i: int
    >>>
    >>> to_dict(Hoge(10))
    {'i': 10}
    >>>
    >>> to_dict([Hoge(10), Hoge(20)])
    [{'i': 10}, {'i': 20}]
    >>>
    >>> to_dict({'a': Hoge(10), 'b': Hoge(20)})
    {'a': {'i': 10}, 'b': {'i': 20}}
    >>>
    >>> to_dict((Hoge(10), Hoge(20)))
    ({'i': 10}, {'i': 20})
    """
    if o is None:
        v = None
    if is_serializable(o):
        v = asdict(o)
    elif isinstance(o, list):
        v = [to_dict(e) for e in o]
    elif isinstance(o, tuple):
        v = tuple(to_dict(e) for e in o)
    elif isinstance(o, dict):
        v = {k: to_dict(v) for k, v in o.items()}
    else:
        v = o

    return v


def to_iter(obj) -> Tuple:
    pass


def se_func(cls: Type[T], funcname: str, params: str) -> Type[T]:
    """
    Generate function to serialize into an object.
    """
    body = f'def {funcname}({params}):\n' f'  return cls({params})'

    # Generate deserialize function.  code = gen(body, globals)
    setattr(cls, funcname, staticmethod(globals[funcname]))
    if SETTINGS['debug']:
        hidden = getattr(cls, HIDDEN_NAME)
        hidden.code[funcname] = code

    return cls
