import logging
from typing import Dict, List, TypeVar, Iterator, Type, Tuple
from typing_inspect import is_optional_type
from dataclasses import fields, is_dataclass, astuple as _astuple

logger = logging.getLogger('serde')

JsonValue = TypeVar('JsonValue', str, int, float, bool, Dict, List)

T = TypeVar('T')

SE_NAME = '__serde_serialize__'

FROM_TUPLE = '__serde_from_tuple__'

FROM_DICT = '__serde_from_dict__'


class SerdeError(TypeError):
    """
    Serde error class.
    """


def gen(code: str, globals: Dict = None, locals: Dict = None):
    """
    Customized `exec` function.
    """
    logger.debug(code)
    exec(code, globals, locals)


def iter_types(cls: Type) -> Iterator[Type]:
    """
    Iterate field types recursively.
    """
    if is_dataclass(cls):
        yield cls
        for f in fields(cls):
            yield from iter_types(f.type)
    elif is_optional_type(cls):
        yield from iter_types(cls.__args__[0])
    elif issubclass(cls, List):
        yield from iter_types(cls.__args__[0])
    elif issubclass(cls, Tuple):
        for arg in cls.__args__:
            yield from iter_types(arg)
    elif issubclass(cls, Dict):
        yield from iter_types(cls.__args__[0])
        yield from iter_types(cls.__args__[1])
    else:
        yield cls


def astuple(v):
    """
    Convert decoded JSON `dict` to `tuple`.
    """
    if is_dataclass(v):
        return _astuple(v)
    elif isinstance(v, Dict):
        return tuple(astuple(e) for e in v.values())
    elif isinstance(v, (Tuple, List)):
        return tuple(astuple(e) for e in v)
    else:
        return v
