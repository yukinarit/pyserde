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
    >>> class Foo: pass
    >>> typename(Foo)
    'Foo'
    >>> typename(List[Foo])
    'List[Foo]'
    >>> typename(Dict[str, Foo])
    'Dict[str, Foo]'
    >>> typename(Tuple[int, str, Foo, List[int], Dict[str, Foo]])
    'Tuple[int, str, Foo, List[int], Dict[str, Foo]]'
    >>> typename(Optional[List[Foo]])
    'Optional[List[Foo]]'
    >>> typename(Union[Optional[Foo], List[Foo], Union[str, int]])
    'Union[Optional[Foo], List[Foo], str, int]'
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


def union_args(typ: Union) -> Tuple:
    if not is_union(typ):
        raise TypeError(f'{typ} is not Union')
    args = type_args(typ)
    if len(args) == 1:
        return args[0]
    it = iter(args)
    types = []
    for (i1, i2) in zip_longest(it, it):
        if not i2:
            types.append(i1)
        elif is_none(i2):
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
    return is_optional_type(typ) and len(args) == 2 and not is_none(args[0]) and is_none(args[1])


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
    """
    >>> is_none(int)
    False
    >>> is_none(type(None))
    True
    >>> is_none(None)
    False
    """
    return typ is type(None)  # noqa


PRIMITIVES = [int, float, bool, str]


def is_primitive(typ: Type) -> bool:
    """
    Test if the type is primitive.

    >>> is_primitive(int)
    True
    >>> is_primitive(float)
    True
    >>> class CustomInt(int):
    ...     pass
    >>> is_primitive(CustomInt)
    True
    """
    try:
        return any(issubclass(typ, ty) for ty in PRIMITIVES)
    except TypeError:
        return any(isinstance(typ, ty) for ty in PRIMITIVES)


def assert_type(typ: Type, obj, throw=False) -> None:
    if not isinstance(obj, typ):
        if throw:
            raise ValueError(f'{obj} is not instance of {typ}')
