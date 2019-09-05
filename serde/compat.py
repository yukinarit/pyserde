from dataclasses import fields, is_dataclass
from itertools import zip_longest
from typing import Iterator, Optional, Tuple, Type, TypeVar, Union

from typing_inspect import get_args, get_origin, is_optional_type, is_union_type

T = TypeVar('T')


def typename(typ) -> str:
    """
    >>> from typing import List, Dict
    >>> typename(int)
    'int'
    >>> class Hoge: pass
    >>> typename(Hoge)
    'Hoge'
    >>> typename(List[Hoge])
    'List[Hoge]'
    >>> typename(Dict[str, Hoge])
    'Dict[str, Hoge]'
    >>> typename(Tuple[int, str, Hoge, List[int], Dict[str, Hoge]])
    'Tuple[int, str, Hoge, List[int], Dict[str, Hoge]]'
    >>> typename(Optional[List[Hoge]])
    'Optional[List[Hoge]]'
    >>> typename(Union[Optional[Hoge], List[Hoge], Union[str, int]])
    'Union[Optional[Hoge], List[Hoge], str, int]'
    """
    if is_opt(typ):
        return f'Optional[{typename(type_args(typ)[0])}]'
    elif is_union(typ):
        return f'Union[{", ".join([typename(e) for e in union_args(typ)])}]'
    elif is_list(typ):
        et = typename(type_args(typ)[0])
        return f'List[{et}]'
    elif is_dict(typ):
        kt = typename(type_args(typ)[0])
        vt = typename(type_args(typ)[1])
        return f'Dict[{kt}, {vt}]'
    elif is_tuple(typ):
        return f'Tuple[{", ".join([typename(e) for e in type_args(typ)])}]'
    else:
        return typ.__name__


def type_args(cls: Type):
    """
    Wrapepr to suppress type error for accessing private members.
    """
    return cls.__args__  # type: ignore


def union_args(typ: Union[T]) -> Tuple[T]:
    if not is_union(typ):
        return TypeError(f'{typ} is not Union')
    args = type_args(typ)
    if len(args) == 1:
        return args[0]
    it = iter(args)
    types = []
    for (i1, i2) in zip_longest(it, it):
        if not i2:
            types.append(i1)
        elif i2 is type(None):
            types.append(Optional[i1])
        else:
            types.extend((i1, i2))
    return tuple(types)


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
    elif is_union(cls):
        for arg in type_args(cls):
            yield from iter_types(arg)
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


def is_union(typ: Type) -> bool:
    """
    Test if the type is `typing.Union`.
    """
    return is_union_type(typ) and not is_opt(typ)


def is_opt(typ: Type) -> bool:
    """
    Test if the type is `typing.Optional`.
    """
    args = get_args(typ)
    return is_optional_type(typ) and len(args) == 2 and args[0] is not type(None) and args[1] is type(None)


def is_list(typ: Type) -> bool:
    """
    Test if the type is `typing.List`.
    """
    try:
        return issubclass(get_origin(typ), list)
    except TypeError:
        return isinstance(typ, list)


def is_tuple(typ: Type) -> bool:
    """
    Test if the type is `typing.Tuple`.
    """
    try:
        return issubclass(get_origin(typ), tuple)
    except TypeError:
        return isinstance(typ, tuple)


def is_dict(typ: Type) -> bool:
    """
    Test if the type is `typing.Dict`.
    """
    try:
        return issubclass(get_origin(typ), dict)
    except TypeError:
        return isinstance(typ, dict)


def is_none(typ: Type) -> bool:
    return typ is type(None)


def assert_type(typ: Type, obj, throw=False) -> None:
    if not isinstance(obj, typ):
        if throw:
            raise ValueError(f'{obj} is not instance of {typ}')
