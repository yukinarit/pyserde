"""
Module for compatibility.
"""
import dataclasses
import datetime
import decimal
import enum
import functools
import ipaddress
import itertools
import pathlib
import sys
import types
import typing
import uuid
from collections import defaultdict
from dataclasses import is_dataclass
from typing import (
    Any,
    ClassVar,
    DefaultDict,
    Dict,
    FrozenSet,
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import typing_extensions
import typing_inspect
from typing_extensions import Type

if sys.version_info[:2] == (3, 7):
    Literal = typing_extensions.Literal
else:
    Literal = typing.Literal

try:
    if sys.version_info[:2] <= (3, 8):
        import numpy as np

        def __is_nptype(tp):
            return getattr(tp, "__origin__", None) in (np.ndarray, np.dtype)

        # If the given type is NDArray or _DType, returns __origin__ or __args__.
        # This should work since the only GenericAliases that current NumPy (1.23)
        # exposes are 'NDArray' and '_DType'.
        # Note: these functions are only needed on Python 3.8 or earlier.
        # On Python >= 3.9, numpy.ndarray[...] and numpy.dtype[...] are instances of
        # the builtin genericalias class.
        def get_np_origin(tp):
            if __is_nptype(tp):
                return tp.__origin__
            else:
                return None

        def get_np_args(tp):
            if __is_nptype(tp):
                return tp.__args__
            else:
                return ()

    else:

        def get_np_origin(tp: Type[Any]) -> Optional[Any]:
            return None

        def get_np_args(tp: Any) -> Tuple[Any, ...]:
            return ()

except ImportError:

    def get_np_origin(tp: Type[Any]) -> Optional[Any]:
        return None

    def get_np_args(tp: Any) -> Tuple[Any, ...]:
        return ()


__all__: List[str] = []

T = TypeVar('T')


StrSerializableTypes = (
    decimal.Decimal,
    pathlib.Path,
    pathlib.PosixPath,
    pathlib.WindowsPath,
    pathlib.PurePath,
    pathlib.PurePosixPath,
    pathlib.PureWindowsPath,
    uuid.UUID,
    ipaddress.IPv4Address,
    ipaddress.IPv6Address,
    ipaddress.IPv4Network,
    ipaddress.IPv6Network,
    ipaddress.IPv4Interface,
    ipaddress.IPv6Interface,
)
""" List of standard types (de)serializable to str """

DateTimeTypes = (datetime.date, datetime.time, datetime.datetime)
""" List of datetime types """


class SerdeError(Exception):
    """
    Serde error class.
    """


@dataclasses.dataclass
class UserError(Exception):
    """
    Error from user code e.g. __post_init__.
    """

    inner: Exception


class SerdeSkip(Exception):
    """
    Skip a field in custom (de)serializer.
    """


def get_origin(typ: Type[Any]) -> Optional[Any]:
    """
    Provide `get_origin` that works in all python versions.
    """
    try:
        return typing.get_origin(typ) or get_np_origin(typ)  # python>=3.8 typing module has get_origin.
    except AttributeError:
        return typing_extensions.get_origin(typ) or get_np_origin(typ)


def get_args(typ: Any) -> Tuple[Any, ...]:
    """
    Provide `get_args` that works in all python versions.
    """
    try:
        return typing.get_args(typ) or get_np_args(typ)  # python>=3.8 typing module has get_args.
    except AttributeError:
        return typing_extensions.get_args(typ) or get_np_args(typ)


def typename(typ: Type[Any], with_typing_module: bool = False) -> str:
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
    mod = "typing." if with_typing_module else ""
    thisfunc = functools.partial(typename, with_typing_module=with_typing_module)
    if is_opt(typ):
        args = type_args(typ)
        if args:
            return f'{mod}Optional[{thisfunc(type_args(typ)[0])}]'
        else:
            return f'{mod}Optional'
    elif is_union(typ):
        args = union_args(typ)
        if args:
            return f'{mod}Union[{", ".join([thisfunc(e) for e in args])}]'
        else:
            return f'{mod}Union'
    elif is_list(typ):
        # Workaround for python 3.7.
        # get_args for the bare List returns parameter T.
        if typ is List:
            return f'{mod}List'

        args = type_args(typ)
        if args:
            et = thisfunc(args[0])
            return f'{mod}List[{et}]'
        else:
            return f'{mod}List'
    elif is_set(typ):
        # Workaround for python 3.7.
        # get_args for the bare Set returns parameter T.
        if typ is Set:
            return f'{mod}Set'

        args = type_args(typ)
        if args:
            et = thisfunc(args[0])
            return f'{mod}Set[{et}]'
        else:
            return f'{mod}Set'
    elif is_dict(typ):
        # Workaround for python 3.7.
        # get_args for the bare Dict returns parameter K, V.
        if typ is Dict:
            return f'{mod}Dict'

        args = type_args(typ)
        if args and len(args) == 2:
            kt = thisfunc(args[0])
            vt = thisfunc(args[1])
            return f'{mod}Dict[{kt}, {vt}]'
        else:
            return f'{mod}Dict'
    elif is_tuple(typ):
        args = type_args(typ)
        if args:
            return f'{mod}Tuple[{", ".join([thisfunc(e) for e in args])}]'
        else:
            return f'{mod}Tuple'
    elif is_generic(typ):
        origin = get_origin(typ)
        assert origin is not None
        return origin.__name__
    elif is_literal(typ):
        args = type_args(typ)
        if not args:
            raise TypeError("Literal type requires at least one literal argument")
        return f'Literal[{", ".join(str(e) for e in args)}]'
    elif typ is Any:
        return f'{mod}Any'
    elif is_ellipsis(typ):
        return '...'
    else:
        # Get super type for NewType
        inner = getattr(typ, '__supertype__', None)
        if inner:
            return typename(typ.__supertype__)

        name: Optional[str] = getattr(typ, '_name', None)
        if name:
            return name
        else:
            return typ.__name__


def type_args(typ: Any) -> Tuple[Type[Any], ...]:
    """
    Wrapper to suppress type error for accessing private members.
    """
    try:
        args: Tuple[Type[Any, ...]] = typ.__args__  # type: ignore
        if args is None:
            return ()
        else:
            return args
    except AttributeError:
        return get_args(typ)


def union_args(typ: Union) -> Tuple[Type[Any], ...]:
    if not is_union(typ):
        raise TypeError(f'{typ} is not Union')
    args = type_args(typ)
    if len(args) == 1:
        return (args[0],)
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


def dataclass_fields(cls: Type[Any]) -> Iterator[dataclasses.Field]:
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


TypeLike = Union[Type[Any], typing.Any]


def iter_types(cls: TypeLike) -> List[TypeLike]:
    """
    Iterate field types recursively.

    The correct return type is `Iterator[Union[Type, typing._specialform]],
    but `typing._specialform` doesn't exist for python 3.6. Use `Any` instead.
    """
    lst: Set[TypeLike] = set()

    def recursive(cls: TypeLike) -> None:
        if cls in lst:
            return

        if is_dataclass(cls):
            lst.add(cls)
            for f in dataclass_fields(cls):
                recursive(f.type)
        elif isinstance(cls, str):
            lst.add(cls)
        elif is_opt(cls):
            lst.add(Optional)
            arg = type_args(cls)
            if arg:
                recursive(arg[0])
        elif is_union(cls):
            lst.add(Union)
            for arg in type_args(cls):
                recursive(arg)
        elif is_list(cls) or is_set(cls):
            lst.add(List)
            arg = type_args(cls)
            if arg:
                recursive(arg[0])
        elif is_set(cls):
            lst.add(Set)
            arg = type_args(cls)
            if arg:
                recursive(arg[0])
        elif is_tuple(cls):
            lst.add(Tuple)
            for arg in type_args(cls):
                recursive(arg)
        elif is_dict(cls):
            lst.add(Dict)
            arg = type_args(cls)
            if arg and len(arg) >= 2:
                recursive(arg[0])
                recursive(arg[1])
        else:
            lst.add(cls)

    recursive(cls)
    return list(lst)


def iter_unions(cls: TypeLike) -> List[TypeLike]:
    """
    Iterate over all unions that are used in the dataclass
    """
    lst: Set[TypeLike] = set()

    def recursive(cls: TypeLike) -> None:
        if cls in lst:
            return

        if is_union(cls):
            lst.add(cls)
            for arg in type_args(cls):
                recursive(arg)
        if is_dataclass(cls):
            for f in dataclass_fields(cls):
                recursive(f.type)
        elif is_opt(cls):
            arg = type_args(cls)
            if arg:
                recursive(arg[0])
        elif is_list(cls) or is_set(cls):
            arg = type_args(cls)
            if arg:
                recursive(arg[0])
        elif is_tuple(cls):
            for arg in type_args(cls):
                recursive(arg)
        elif is_dict(cls):
            arg = type_args(cls)
            if arg and len(arg) >= 2:
                recursive(arg[0])
                recursive(arg[1])

    recursive(cls)
    return list(lst)


def iter_literals(cls: TypeLike) -> List[TypeLike]:
    """
    Iterate over all literals that are used in the dataclass
    """
    lst: Set[TypeLike] = set()

    def recursive(cls: TypeLike) -> None:
        if cls in lst:
            return

        if is_literal(cls):
            lst.add(cls)
        if is_union(cls):
            for arg in type_args(cls):
                recursive(arg)
        if is_dataclass(cls):
            lst.add(cls)
            for f in dataclass_fields(cls):
                recursive(f.type)
        elif is_opt(cls):
            arg = type_args(cls)
            if arg:
                recursive(arg[0])
        elif is_list(cls) or is_set(cls):
            arg = type_args(cls)
            if arg:
                recursive(arg[0])
        elif is_tuple(cls):
            for arg in type_args(cls):
                recursive(arg)
        elif is_dict(cls):
            arg = type_args(cls)
            if arg and len(arg) >= 2:
                recursive(arg[0])
                recursive(arg[1])

    recursive(cls)
    return list(lst)


def is_union(typ) -> bool:
    """
    Test if the type is `typing.Union`.

    >>> is_union(Union[int, str])
    True
    """

    # Python 3.10 Union operator e.g. str | int
    if sys.version_info[:2] >= (3, 10):
        try:
            if isinstance(typ, types.UnionType):
                return True
        except Exception:
            pass

    # typing.Union
    return typing_inspect.is_union_type(typ)


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

    # Python 3.10 Union operator e.g. str | None
    is_union_type = False
    if sys.version_info[:2] >= (3, 10):
        try:
            if isinstance(typ, types.UnionType):
                is_union_type = True
        except Exception:
            pass

    # typing.Optional
    is_typing_union = typing_inspect.is_optional_type(typ)

    args = type_args(typ)
    if args:
        return (is_union_type or is_typing_union) and len(args) == 2 and not is_none(args[0]) and is_none(args[1])
    else:
        return typ is Optional


def is_bare_opt(typ: Any) -> bool:
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


def is_list(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.List`.

    >>> from typing import List
    >>> is_list(List[int])
    True
    >>> is_list(List)
    True
    """
    try:
        return issubclass(get_origin(typ), list)  # type: ignore
    except TypeError:
        return typ in (List, list)


def is_bare_list(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.List` without type args.

    >>> from typing import List
    >>> is_bare_list(List[int])
    False
    >>> is_bare_list(List)
    True
    """
    return typ in (List, list)


def is_tuple(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.Tuple`.
    """
    try:
        return issubclass(get_origin(typ), tuple)  # type: ignore
    except TypeError:
        return typ in (Tuple, tuple)


def is_bare_tuple(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.Tuple` without type args.

    >>> from typing import Tuple
    >>> is_bare_tuple(Tuple[int, str])
    False
    >>> is_bare_tuple(Tuple)
    True
    """
    return typ in (Tuple, tuple)


def is_variable_tuple(typ: Type[Any]) -> bool:
    """
    Test if the type is a variable length of tuple `typing.Tuple[T, ...]`.

    >>> from typing import Tuple
    >>> is_variable_tuple(Tuple[int, ...])
    True
    >>> is_variable_tuple(Tuple[int, bool])
    False
    >>> is_variable_tuple(Tuple[()])
    False
    """
    istuple = is_tuple(typ) and not is_bare_tuple(typ)
    args = get_args(typ)
    return istuple and len(args) == 2 and is_ellipsis(args[1])


def is_set(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.Set` or `typing.FrozenSet`.

    >>> from typing import Set
    >>> is_set(Set[int])
    True
    >>> is_set(Set)
    True
    >>> is_set(FrozenSet[int])
    True
    """
    try:
        return issubclass(get_origin(typ), (set, frozenset))  # type: ignore
    except TypeError:
        return typ in (Set, set, FrozenSet, frozenset)


def is_bare_set(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.Set` without type args.

    >>> from typing import Set
    >>> is_bare_set(Set[int])
    False
    >>> is_bare_set(Set)
    True
    """
    return typ in (Set, set)


def is_frozen_set(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.FrozenSet`.

    >>> from typing import Set
    >>> is_frozen_set(FrozenSet[int])
    True
    >>> is_frozen_set(Set)
    False
    """
    try:
        return issubclass(get_origin(typ), frozenset)  # type: ignore
    except TypeError:
        return typ in (FrozenSet, frozenset)


def is_dict(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.Dict`.

    >>> from typing import Dict
    >>> is_dict(Dict[int, int])
    True
    >>> is_dict(Dict)
    True
    >>> is_dict(DefaultDict[int, int])
    True
    """
    try:
        return issubclass(get_origin(typ), (dict, defaultdict))  # type: ignore
    except TypeError:
        return typ in (Dict, dict, DefaultDict, defaultdict)


def is_bare_dict(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.Dict` without type args.

    >>> from typing import Dict
    >>> is_bare_dict(Dict[int, str])
    False
    >>> is_bare_dict(Dict)
    True
    """
    return typ in (Dict, dict)


def is_default_dict(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.DefaultDict`.

    >>> from typing import Dict
    >>> is_default_dict(DefaultDict[int, int])
    True
    >>> is_default_dict(Dict[int, int])
    False
    """
    try:
        return issubclass(get_origin(typ), defaultdict)  # type: ignore
    except TypeError:
        return typ in (DefaultDict, defaultdict)


def is_none(typ: Type[Any]) -> bool:
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


def is_enum(typ: Type[Any]) -> bool:
    """
    Test if the type is `enum.Enum`.
    """
    try:
        return issubclass(typ, enum.Enum)
    except TypeError:
        return isinstance(typ, enum.Enum)


def is_primitive(typ: Type[Any]) -> bool:
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
        return is_new_type_primitive(typ)


def is_new_type_primitive(typ: Type[Any]) -> bool:
    """
    Test if the type is a NewType of primitives.
    """
    inner = getattr(typ, '__supertype__', None)
    if inner:
        return is_primitive(inner)
    else:
        return any(isinstance(typ, ty) for ty in PRIMITIVES)


def is_generic(typ: Type[Any]) -> bool:
    """
    Test if the type is derived from `typing.Generic`.

    >>> T = typing.TypeVar('T')
    >>> class GenericFoo(typing.Generic[T]):
    ...     pass
    >>> is_generic(GenericFoo[int])
    True
    >>> is_generic(GenericFoo)
    False
    """
    origin = get_origin(typ)
    return origin is not None and Generic in getattr(origin, "__bases__", ())


def is_class_var(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.ClassVar`.

    >>> is_class_var(ClassVar[int])
    True
    >>> is_class_var(ClassVar)
    True
    """
    return get_origin(typ) is ClassVar or typ is ClassVar  # type: ignore


def is_literal(typ: Type[Any]) -> bool:
    """
    Test if the type is derived from `typing.Literal`.

    >>> T = typing.TypeVar('T')
    >>> class GenericFoo(typing.Generic[T]):
    ...     pass
    >>> is_generic(GenericFoo[int])
    True
    >>> is_generic(GenericFoo)
    False
    """
    origin = get_origin(typ)
    if sys.version_info[:2] == (3, 7):
        return origin is typing_extensions.Literal
    return origin is not None and origin is typing.Literal


def is_any(typ: Type[Any]) -> bool:
    """
    Test if the type is `typing.Any`.
    """
    return typ is Any


def is_str_serializable(typ: Type[Any]) -> bool:
    """
    Test if the type is serializable to `str`.
    """
    return typ in StrSerializableTypes


def is_datetime(typ: Type[Any]) -> bool:
    """
    Test if the type is any of the datetime types..
    """
    return typ in DateTimeTypes


def is_str_serializable_instance(obj: Any) -> bool:
    return isinstance(obj, StrSerializableTypes)


def is_datetime_instance(obj: Any) -> bool:
    return isinstance(obj, DateTimeTypes)


def is_ellipsis(typ: Any) -> bool:
    return typ is Ellipsis


def find_generic_arg(cls: Type[Any], field: TypeVar) -> int:
    """
    Find a type in generic parameters.

    >>> T = typing.TypeVar('T')
    >>> U = typing.TypeVar('U')
    >>> V = typing.TypeVar('V')
    >>> class GenericFoo(typing.Generic[T, U]):
    ...     pass
    >>> find_generic_arg(GenericFoo, T)
    0
    >>> find_generic_arg(GenericFoo, U)
    1
    >>> find_generic_arg(GenericFoo, V)
    -1
    """
    bases = getattr(cls, "__orig_bases__", ())
    if not bases:
        raise Exception(f"\"__orig_bases__\" property was not found: {cls}")

    for base in bases:
        for n, arg in enumerate(get_args(base)):
            if arg.__name__ == field.__name__:
                return n

    if not bases:
        raise Exception(f"Generic field not found in class: {bases}")

    return -1


def get_generic_arg(typ: Any, index: int) -> Any:
    """
    Get generic type argument by index.

    >>> T = typing.TypeVar('T')
    >>> U = typing.TypeVar('U')
    >>> class GenericFoo(typing.Generic[T, U]):
    ...     pass
    >>> get_generic_arg(GenericFoo[int, str], 0).__name__
    'int'
    >>> get_generic_arg(GenericFoo[int, str], 1).__name__
    'str'
    """
    if not is_generic(typ):
        return typing.Any
    else:
        args = get_args(typ)
        if index + 1 > len(args):
            return typing.Any
        return args[index]


def has_default(field: dataclasses.Field) -> bool:
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


def has_default_factory(field: dataclasses.Field) -> bool:
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
