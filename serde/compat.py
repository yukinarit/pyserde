"""
Module for compatibility.
"""
import dataclasses
import enum
import itertools
import sys
import typing
from dataclasses import is_dataclass
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Type, TypeVar, Union

import typing_inspect

__all__: List = []

T = TypeVar('T')


class SerdeError(TypeError):
    """
    Serde error class.
    """


class SerdeSkip(Exception):
    """
    Skip a field in custom (de)serializer.
    """


def get_origin(typ):
    """
    Provide `get_origin` that works in all python versions.
    """
    try:
        return typing.get_origin(typ)  # python>=3.8 typing module has get_origin.
    except AttributeError:
        return typing_inspect.get_origin(typ)


def get_args(typ):
    """
    Provide `get_args` that works in all python versions.
    """
    try:
        return typing.get_args(typ)  # python>=3.8 typing module has get_args.
    except AttributeError:
        return typing_inspect.get_args(typ)


def typename(typ) -> str:
    """
    >>> from typing import List, Dict, Set, Any
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
    >>> typename(Set[Foo])
    'Set[Foo]'
    >>> typename(Any)
    'Any'
    """
    if is_opt(typ):
        args = type_args(typ)
        if args:
            return f'Optional[{typename(type_args(typ)[0])}]'
        else:
            return 'Optional'
    elif is_union(typ):
        args = union_args(typ)
        if args:
            return f'Union[{", ".join([typename(e) for e in args])}]'
        else:
            return 'Union'
    elif is_list(typ):
        args = type_args(typ)
        if args:
            et = typename(args[0])
            return f'List[{et}]'
        else:
            return 'List'
    elif is_set(typ):
        args = type_args(typ)
        if args:
            et = typename(args[0])
            return f'Set[{et}]'
        else:
            return 'Set'
    elif is_dict(typ):
        args = type_args(typ)
        if args and len(args) == 2:
            kt = typename(args[0])
            vt = typename(args[1])
            return f'Dict[{kt}, {vt}]'
        else:
            return 'Dict'
    elif is_tuple(typ):
        args = type_args(typ)
        if args:
            return f'Tuple[{", ".join([typename(e) for e in args])}]'
        else:
            return 'Tuple'
    elif typ is Any:
        return 'Any'
    else:
        name = getattr(typ, '_name', None)
        if name:
            return name
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
        return get_args(typ)


def union_args(typ: Union) -> Tuple:
    if not is_union(typ):
        raise TypeError(f'{typ} is not Union')
    args = type_args(typ)
    if len(args) == 1:
        return args[0]
    it = iter(args)
    types = []
    for (i1, i2) in itertools.zip_longest(it, it):
        if not i2:
            types.append(i1)
        elif is_none(i2):
            types.append(Optional[i1])
        else:
            types.extend((i1, i2))
    return tuple(types)


def dataclass_fields(cls: Type) -> Iterator:
    raw_fields = dataclasses.fields(cls)

    try:
        # this resolves types when string forward reference
        # or PEP 563: "from __future__ import annotations" are used
        resolved_hints = typing.get_type_hints(cls)
    except Exception as e:
        raise SerdeError(
            f"Failed to resolve type hints for {typename(cls)}:\n"
            f"{e.__class__.__name__}: {e}\n\n"
            f"If you are using forward references make sure you are calling deserialize & "
            "serialize after all classes are globally visible."
        )

    for f in raw_fields:
        real_type = resolved_hints.get(f.name)
        # python <= 3.6 has no typing.ForwardRef so we need to skip the check
        if sys.version_info[:2] != (3, 6) and isinstance(real_type, typing.ForwardRef):
            raise SerdeError(
                f"Failed to resolve {real_type} for {typename(cls)}.\n\n"
                f"Make sure you are calling deserialize & serialize after all classes are globally visible."
            )
        if real_type is not None:
            f.type = real_type

    return iter(raw_fields)


def iter_types(cls: Type) -> Iterator[Union[Type, typing.Any]]:
    """
    Iterate field types recursively.

    The correct return type is `Iterator[Union[Type, typing._specialform]],
    but `typing._specialform` doesn't exist for python 3.6. Use `Any` instead.
    """
    if is_dataclass(cls):
        yield cls
        for f in dataclass_fields(cls):
            yield from iter_types(f.type)
    elif isinstance(cls, str):
        yield cls
    elif is_opt(cls):
        yield Optional
        arg = type_args(cls)
        if arg:
            yield from iter_types(arg[0])
    elif is_union(cls):
        yield Union
        for arg in type_args(cls):
            yield from iter_types(arg)
    elif is_list(cls) or is_set(cls):
        yield List
        arg = type_args(cls)
        if arg:
            yield from iter_types(arg[0])
    elif is_set(cls):
        yield Set
        arg = type_args(cls)
        if arg:
            yield from iter_types(arg[0])
    elif is_tuple(cls):
        yield Tuple
        for arg in type_args(cls):
            yield from iter_types(arg)
    elif is_dict(cls):
        yield Dict
        arg = type_args(cls)
        if arg and len(arg) >= 2:
            yield from iter_types(arg[0])
            yield from iter_types(arg[1])
    else:
        yield cls


def iter_unions(cls: Type) -> Iterator[Type]:
    """
    Iterate over all unions that are used in the dataclass
    """
    if is_union(cls):
        yield cls
        for arg in type_args(cls):
            yield from iter_unions(arg)
    if is_dataclass(cls):
        for f in dataclass_fields(cls):
            yield from iter_unions(f.type)
    elif is_opt(cls):
        arg = type_args(cls)
        if arg:
            yield from iter_unions(arg[0])
    elif is_list(cls) or is_set(cls):
        arg = type_args(cls)
        if arg:
            yield from iter_unions(arg[0])
    elif is_tuple(cls):
        for arg in type_args(cls):
            yield from iter_unions(arg)
    elif is_dict(cls):
        arg = type_args(cls)
        if arg and len(arg) >= 2:
            yield from iter_unions(arg[0])
            yield from iter_unions(arg[1])


def is_union(typ) -> bool:
    """
    Test if the type is `typing.Union`.
    """
    return typing_inspect.is_union_type(typ) and not is_opt(typ)


def is_opt(typ) -> bool:
    """
    Test if the type is `typing.Optional`.

    >>> is_opt(Optional[int])
    True
    >>> is_opt(Optional)
    True
    >>> is_opt(None.__class__)
    False
    """
    args = type_args(typ)
    if args:
        return typing_inspect.is_optional_type(typ) and len(args) == 2 and not is_none(args[0]) and is_none(args[1])
    else:
        return typ is Optional


def is_bare_opt(typ) -> bool:
    """
    Test if the type is `typing.Optional` without type args.
    >>> is_bare_opt(Optional[int])
    False
    >>> is_bare_opt(Optional)
    True
    >>> is_bare_opt(None.__class__)
    False
    """
    return not type_args(typ) and typ is Optional


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
        return typ in (List, list)


def is_bare_list(typ) -> bool:
    """
    Test if the type is `typing.List` without type args.

    >>> from typing import List
    >>> is_bare_list(List[int])
    False
    >>> is_bare_list(List)
    True
    """
    return typ in (List, list)


def is_tuple(typ) -> bool:
    """
    Test if the type is `typing.Tuple`.
    """
    try:
        return issubclass(get_origin(typ), tuple)
    except TypeError:
        return typ in (Tuple, tuple)


def is_bare_tuple(typ) -> bool:
    """
    Test if the type is `typing.Tuple` without type args.

    >>> from typing import Tuple
    >>> is_bare_tuple(Tuple[int, str])
    False
    >>> is_bare_tuple(Tuple)
    True
    """
    return typ in (Tuple, tuple)


def is_set(typ) -> bool:
    """
    Test if the type is `typing.Set`.

    >>> from typing import Set
    >>> is_set(Set[int])
    True
    >>> is_set(Set)
    True
    """
    try:
        return issubclass(get_origin(typ), set)
    except TypeError:
        return typ in (Set, set)


def is_bare_set(typ) -> bool:
    """
    Test if the type is `typing.Set` without type args.

    >>> from typing import Set
    >>> is_bare_set(Set[int])
    False
    >>> is_bare_set(Set)
    True
    """
    return typ in (Set, set)


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
        return typ in (Dict, dict)


def is_bare_dict(typ) -> bool:
    """
    Test if the type is `typing.Dict` without type args.

    >>> from typing import Dict
    >>> is_bare_dict(Dict[int, str])
    False
    >>> is_bare_dict(Dict)
    True
    """
    return typ in (Dict, dict)


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
    >>> class CustomInt(int):
    ...     pass
    >>> is_primitive(CustomInt)
    True
    """
    try:
        return any(issubclass(typ, ty) for ty in PRIMITIVES)
    except TypeError:
        inner = getattr(typ, '__supertype__', None)
        if inner:
            return is_primitive(inner)
        else:
            return any(isinstance(typ, ty) for ty in PRIMITIVES)


def has_default(field) -> bool:
    """
    Test if the field has default value.

    >>> @dataclasses.dataclass
    ... class C:
    ...     a: int
    ...     d: int = 10
    >>> has_default(dataclasses.fields(C)[0])
    False
    >>> has_default(dataclasses.fields(C)[1])
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
    >>> has_default_factory(dataclasses.fields(C)[0])
    False
    >>> has_default_factory(dataclasses.fields(C)[1])
    True
    """
    return not isinstance(field.default_factory, dataclasses._MISSING_TYPE)
