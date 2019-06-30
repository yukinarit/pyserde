import logging
from dataclasses import dataclass, field, fields, is_dataclass, astuple as _astuple, asdict as _asdict
from typing import Dict, List, TypeVar, Iterator, Type, Tuple
from typing_inspect import get_origin

from .compat import is_opt, is_list, is_tuple, is_dict

logger = logging.getLogger('serde')

JsonValue = TypeVar('JsonValue', str, int, float, bool, Dict, List)

T = TypeVar('T')

SE_NAME = '__serde_serialize__'

FROM_TUPLE = '__serde_from_tuple__'

FROM_DICT = '__serde_from_dict__'

HIDDEN_NAME = '__serde_hidden__'

SETTINGS = dict(
    debug=False,
)


@dataclass
class Hidden:
    """
    Hidden infomation encoded in serde classes.
    """
    code: Dict[str, str] = field(default_factory=dict)


def init(debug: bool=False):
    SETTINGS['debug'] = debug


class SerdeError(TypeError):
    """
    Serde error class.
    """


def gen(code: str, globals: Dict = None, locals: Dict = None) -> str:
    """
    Customized `exec` function.
    """
    try:
        from black import format_str, FileMode
        code = format_str(code, mode=FileMode(line_length=100))
    except:
        pass
    logger.debug(f'Generating...\n{code}')
    exec(code, globals, locals)
    return code


def type_args(cls: Type):
    """
    Wrapepr to suppress type error for accessing private members.
    """
    return cls.__args__  # type: ignore


def iter_types(cls: Type) -> Iterator[Type]:
    """
    Iterate field types recursively.
    """
    if is_dataclass(cls):
        yield cls
        for f in fields(cls):
            yield from iter_types(f.type)
    elif isinstance(cls, str):
        yield cls
    elif is_opt(cls):
        yield from iter_types(type_args(cls)[0])
    elif is_list(cls):
        yield from iter_types(type_args(cls)[0])
    elif is_tuple(cls):
        for arg in type_args(cls):
            yield from iter_types(arg)
    elif is_dict(cls):
        yield from iter_types(type_args(cls)[0])
        yield from iter_types(type_args(cls)[1])
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


def asdict(v):
    return _asdict(v)


def typecheck(cls: Type[T], obj: T) -> None:
    """
    >>> @dataclass
    ... class Hoge:
    ...     s: str
    >>>
    >>> typecheck(Hoge, Hoge('hoge'))
    >>>
    >>> # Type mismatch raises `ValueError`.
    >>> try:
    ...     typecheck(Hoge, Hoge(10))
    ... except:
    ...     pass
    >>>
    """
    if is_dataclass(obj):
        # If dataclass, type check recursively.
        for f in fields(obj):
            typecheck(f.type, getattr(obj, f.name, None))
    elif is_opt(cls):
        if obj is not None:
            typ = type_args(cls)[0]
            typecheck(typ, obj)
    elif is_list(cls):
        typ = type_args(cls)[0]
        for e in obj:
            typecheck(typ, e)
    elif is_tuple(cls):
        for i, typ in enumerate(type_args(cls)):
            typecheck(typ, obj[i])
    elif is_dict(cls):
        ktyp = type_args(cls)[0]
        vtyp = type_args(cls)[1]
        for k, v in obj.items():
            typecheck(ktyp, k)
            typecheck(vtyp, v)
    else:
        if not isinstance(obj, cls):
            raise ValueError(f'arg is not instance of {cls}')
