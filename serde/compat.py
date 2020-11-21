"""
Module for compatibility.
"""
import dataclasses
import enum
import typing
from dataclasses import fields, is_dataclass
from itertools import zip_longest
from typing import Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union

import typing_inspect

__all__: List = []

T = TypeVar('T')


def get_origin(typ):
    """
    Provide `get_origin` that works in python >= 3.6.
    """
    try:
        return typing.get_origin(typ)  # python>=3.8 typing module has get_args.
    except AttributeError:
        return typing_inspect.get_origin(typ)


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


def type_args(typ):
    """
    Wrapper to suppress type error for accessing private members.
    """
    try:
        args = typ.__args__  # type: ignore
        if args is None:
            return []
        else:
            return args
    except AttributeError:
        return typing.get_args(typ)  # python>=3.8 typing module has get_args.


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
        arg = type_args(cls)
        if arg:
            yield from iter_types(arg[0])
    elif is_union(cls):
        for arg in type_args(cls):
            yield from iter_types(arg)
    elif is_list(cls):
        arg = type_args(cls)
        if arg:
            yield from iter_types(arg[0])
    elif is_tuple(cls):
        for arg in type_args(cls):
            yield from iter_types(arg)
    elif is_dict(cls):
        arg = type_args(cls)
        if arg and len(arg) >= 2:
            yield from iter_types(arg[0])
            yield from iter_types(arg[1])
    else:
        yield cls


def is_union(typ) -> bool:
    """
    Test if the type is `typing.Union`.
    """
    return typing_inspect.is_union_type(typ) and not is_opt(typ)


def is_opt(typ) -> bool:
    """
    Test if the type is `typing.Optional`.
    """
    args = typing_inspect.get_args(typ)
    return typing_inspect.is_optional_type(typ) and len(args) == 2 and not is_none(args[0]) and is_none(args[1])


def is_list(typ) -> bool:
    """
    Test if the type is `typing.List`.

    >>> from typing import List
    >>> is_list(List[int])
    True
    >>> is_list(List)
    True
    """
    try:
        return issubclass(get_origin(typ), list)
    except TypeError:
        return isinstance(typ, list)


def is_bare_list(typ) -> bool:
    """
    Test if the type is `typing.List` without type args.

    >>> from typing import List
    >>> is_bare_list(List[int])
    False
    >>> is_bare_list(List)
    True
    """
    return is_list(typ) and typ is List


def is_tuple(typ) -> bool:
    """
    Test if the type is `typing.Tuple`.
    """
    try:
        return issubclass(get_origin(typ), tuple)
    except TypeError:
        return isinstance(typ, tuple)


def is_bare_tuple(typ) -> bool:
    """
    Test if the type is `typing.Tuple` without type args.

    >>> from typing import Tuple
    >>> is_bare_tuple(Tuple[int, str])
    False
    >>> is_bare_tuple(Tuple)
    True
    """
    return is_tuple(typ) and typ is Tuple


def is_dict(typ) -> bool:
    """
    Test if the type is `typing.Dict`.

    >>> from typing import Dict
    >>> is_dict(Dict[int, int])
    True
    >>> is_dict(Dict)
    True
    """
    try:
        return issubclass(get_origin(typ), dict)
    except TypeError:
        return isinstance(typ, dict)


def is_bare_dict(typ) -> bool:
    """
    Test if the type is `typing.Dict` without type args.

    >>> from typing import Dict
    >>> is_bare_dict(Dict[int, str])
    False
    >>> is_bare_dict(Dict)
    True
    """
    return is_dict(typ) and typ is Dict


def is_none(typ) -> bool:
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


def is_enum(typ) -> bool:
    """
    Test if the type is `enum.Enum`.
    """
    try:
        return issubclass(typ, enum.Enum)
    except TypeError:
        return isinstance(typ, enum.Enum)


def is_primitive(typ) -> bool:
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


def has_default(field) -> bool:
    """
    Test if the field has default value.

    >>> @dataclasses.dataclass
    ... class C:
    ...     a: int
    ...     d: int = 10
    >>> has_default(fields(C)[0])
    False
    >>> has_default(fields(C)[1])
    True
    """
    return not isinstance(field.default, dataclasses._MISSING_TYPE)


def has_default_factory(field) -> bool:
    """
    Test if the field has default factory.

    >>> from typing import Dict
    >>> @dataclasses.dataclass
    ... class C:
    ...     a: int
    ...     d: Dict = dataclasses.field(default_factory=dict)
    >>> has_default_factory(fields(C)[0])
    False
    >>> has_default_factory(fields(C)[1])
    True
    """
    return not isinstance(field.default_factory, dataclasses._MISSING_TYPE)


def assert_type(typ: Type, obj, throw=False) -> None:
    if not isinstance(obj, typ):
        if throw:
            raise ValueError(f'{obj} is not instance of {typ}')
