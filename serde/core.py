import logging
from dataclasses import asdict as _asdict
from dataclasses import astuple as _astuple
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Dict, List, Tuple, Type, TypeVar

from .compat import T, assert_type, is_dict, is_list, is_opt, is_tuple, is_union, type_args

logger = logging.getLogger('serde')

JsonValue = TypeVar('JsonValue', str, int, float, bool, Dict, List)

SE_NAME = '__serde_serialize__'

FROM_ITER = '__serde_from_iter__'

FROM_DICT = '__serde_from_dict__'

TO_ITER = '__serde_to_iter__'

TO_DICT = '__serde_to_iter__'

HIDDEN_NAME = '__serde_hidden__'

SETTINGS = dict(debug=False)


@dataclass
class Hidden:
    """
    Hidden infomation encoded in serde classes.
    """

    code: Dict[str, str] = field(default_factory=dict)


def init(debug: bool = False):
    SETTINGS['debug'] = debug


class SerdeError(TypeError):
    """
    Serde error class.
    """


def gen(code: str, globals: Dict = None, locals: Dict = None, cls: Type = None) -> str:
    """
    Customized `exec` function.
    """
    try:
        from black import format_str, FileMode

        code = format_str(code, mode=FileMode(line_length=100))
    except:
        pass
    for_class = 'for ' + cls.__name__ if cls else ''
    logger.debug(f'Generating {for_class} ...\n{code}')
    exec(code, globals, locals)
    return code


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
    type check type-annotated classes.

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
    elif is_union(cls):
        success = False
        for typ in type_args(cls):
            try:
                v = typecheck(typ, obj)
                success = True
                break
            except (SerdeError, ValueError):
                pass
        if not success:
            raise ValueError(f'{obj} is not instance of {cls}')
    elif is_list(cls):
        assert_type(list, obj)
        typ = type_args(cls)[0]
        for e in obj:
            typecheck(typ, e)
    elif is_tuple(cls):
        assert_type(tuple, obj)
        for i, typ in enumerate(type_args(cls)):
            typecheck(typ, obj[i])
    elif is_dict(cls):
        assert_type(dict, obj)
        ktyp = type_args(cls)[0]
        vtyp = type_args(cls)[1]
        for k, v in obj.items():
            typecheck(ktyp, k)
            typecheck(vtyp, v)
    else:
        if not isinstance(obj, cls):
            raise ValueError(f'{obj} is not instance of {cls}')
