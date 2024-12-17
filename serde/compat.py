"""
Compatibility layer which handles mostly differences of `typing` module between python versions.
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
import uuid
import typing
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import is_dataclass
from typing import TypeVar, Generic, Any, ClassVar, Optional, NewType, Union, Hashable, Callable

import typing_inspect
from typing_extensions import TypeGuard, ParamSpec, TypeAliasType

from .sqlalchemy import is_sqlalchemy_inspectable


def get_np_origin(tp: type[Any]) -> Optional[Any]:
    return None


def get_np_args(tp: type[Any]) -> tuple[Any, ...]:
    return ()


__all__: list[str] = []

T = TypeVar("T")


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


@dataclasses.dataclass(unsafe_hash=True)
class _WithTagging(Generic[T]):
    """
    Intermediate data structure for (de)serializaing Union without dataclass.
    """

    inner: T
    """ Union type .e.g Union[Foo,Bar] passed in from_obj. """
    tagging: Any
    """ Union Tagging """


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


def is_hashable(typ: Any) -> TypeGuard[Hashable]:
    """
    Test is an object hashable
    """
    try:
        hash(typ)
    except TypeError:
        return False
    return True


P = ParamSpec("P")


def cache(f: Callable[P, T]) -> Callable[P, T]:
    """
    Wrapper for `functools.cache` to avoid `Hashable` related type errors.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return f(*args, **kwargs)

    return functools.cache(wrapper)  # type: ignore


@cache
def get_origin(typ: Any) -> Optional[Any]:
    """
    Provide `get_origin` that works in all python versions.
    """
    return typing.get_origin(typ) or get_np_origin(typ)


@cache
def get_args(typ: type[Any]) -> tuple[Any, ...]:
    """
    Provide `get_args` that works in all python versions.
    """
    return typing.get_args(typ) or get_np_args(typ)


@cache
def typename(typ: Any, with_typing_module: bool = False) -> str:
    """
    >>> from typing import Any
    >>> typename(int)
    'int'
    >>> class Foo: pass
    >>> typename(Foo)
    'Foo'
    >>> typename(list[Foo])
    'list[Foo]'
    >>> typename(dict[str, Foo])
    'dict[str, Foo]'
    >>> typename(tuple[int, str, Foo, list[int], dict[str, Foo]])
    'tuple[int, str, Foo, list[int], dict[str, Foo]]'
    >>> typename(Optional[list[Foo]])
    'Optional[list[Foo]]'
    >>> typename(Union[Optional[Foo], list[Foo], Union[str, int]])
    'Union[Optional[Foo], list[Foo], str, int]'
    >>> typename(set[Foo])
    'set[Foo]'
    >>> typename(Any)
    'Any'
    """
    mod = "typing." if with_typing_module else ""
    thisfunc = functools.partial(typename, with_typing_module=with_typing_module)
    if is_opt(typ):
        args = type_args(typ)
        if args:
            return f"{mod}Optional[{thisfunc(type_args(typ)[0])}]"
        else:
            return f"{mod}Optional"
    elif is_union(typ):
        args = union_args(typ)
        if args:
            return f'{mod}Union[{", ".join([thisfunc(e) for e in args])}]'
        else:
            return f"{mod}Union"
    elif is_list(typ):
        args = type_args(typ)
        if args:
            et = thisfunc(args[0])
            return f"{mod}list[{et}]"
        else:
            return f"{mod}list"
    elif is_set(typ):
        args = type_args(typ)
        if args:
            et = thisfunc(args[0])
            return f"{mod}set[{et}]"
        else:
            return f"{mod}set"
    elif is_dict(typ):
        args = type_args(typ)
        if args and len(args) == 2:
            kt = thisfunc(args[0])
            vt = thisfunc(args[1])
            return f"{mod}dict[{kt}, {vt}]"
        else:
            return f"{mod}dict"
    elif is_tuple(typ):
        args = type_args(typ)
        if args:
            return f'{mod}tuple[{", ".join([thisfunc(e) for e in args])}]'
        else:
            return f"{mod}tuple"
    elif is_generic(typ):
        origin = get_origin(typ)
        if origin is None:
            raise SerdeError("Could not extract origin class from generic class")

        if not isinstance(origin.__name__, str):
            raise SerdeError("Name of generic class is not string")

        return origin.__name__

    elif is_literal(typ):
        args = type_args(typ)
        if not args:
            raise TypeError("Literal type requires at least one literal argument")
        return f'Literal[{", ".join(stringify_literal(e) for e in args)}]'
    elif typ is Any:
        return f"{mod}Any"
    elif is_ellipsis(typ):
        return "..."
    else:
        # Get super type for NewType
        inner = getattr(typ, "__supertype__", None)
        if inner:
            return typename(inner)

        name: Optional[str] = getattr(typ, "_name", None)
        if name:
            return name
        else:
            name = getattr(typ, "__name__", None)
            if isinstance(name, str):
                return name
            else:
                raise SerdeError(f"Could not get a type name from: {typ}")


def stringify_literal(v: Any) -> str:
    if isinstance(v, str):
        return f"'{v}'"
    else:
        return str(v)


def type_args(typ: Any) -> tuple[type[Any], ...]:
    """
    Wrapper to suppress type error for accessing private members.
    """
    try:
        args: tuple[type[Any, ...]] = typ.__args__  # type: ignore
        if args is None:
            return ()
        else:
            return args
    except AttributeError:
        return get_args(typ)


def union_args(typ: Any) -> tuple[type[Any], ...]:
    if not is_union(typ):
        raise TypeError(f"{typ} is not Union")
    args = type_args(typ)
    if len(args) == 1:
        return (args[0],)
    it = iter(args)
    types = []
    for i1, i2 in itertools.zip_longest(it, it):
        if not i2:
            types.append(i1)
        elif is_none(i2):
            types.append(Optional[i1])
        else:
            types.extend((i1, i2))
    return tuple(types)


def dataclass_fields(cls: type[Any]) -> Iterator[dataclasses.Field]:  # type: ignore
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
        ) from e

    for f in raw_fields:
        real_type = resolved_hints.get(f.name)
        if real_type is not None:
            f.type = real_type
            if is_generic(real_type) and is_sqlalchemy_inspectable(cls):
                f.type = get_args(real_type)[0]

    return iter(raw_fields)


TypeLike = Union[type[Any], typing.Any]


def iter_types(cls: type[Any]) -> list[type[Any]]:
    """
    Iterate field types recursively.

    The correct return type is `Iterator[Union[Type, typing._specialform]],
    but `typing._specialform` doesn't exist for python 3.6. Use `Any` instead.
    """
    lst: set[Union[type[Any], Any]] = set()

    def recursive(cls: Union[type[Any], Any]) -> None:
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
            args = type_args(cls)
            if args:
                recursive(args[0])
        elif is_union(cls):
            lst.add(Union)
            for arg in type_args(cls):
                recursive(arg)
        elif is_list(cls):
            lst.add(list)
            args = type_args(cls)
            if args:
                recursive(args[0])
        elif is_set(cls):
            lst.add(set)
            args = type_args(cls)
            if args:
                recursive(args[0])
        elif is_tuple(cls):
            lst.add(tuple)
            for arg in type_args(cls):
                recursive(arg)
        elif is_dict(cls):
            lst.add(dict)
            args = type_args(cls)
            if args and len(args) >= 2:
                recursive(args[0])
                recursive(args[1])
        elif is_pep695_type_alias(cls):
            recursive(cls.__value__)
        else:
            lst.add(cls)

    recursive(cls)
    return list(lst)


def iter_unions(cls: TypeLike) -> list[TypeLike]:
    """
    Iterate over all unions that are used in the dataclass
    """
    lst: list[TypeLike] = []
    stack: list[TypeLike] = []  # To prevent infinite recursion

    def recursive(cls: TypeLike) -> None:
        if cls in stack:
            return

        if is_union(cls):
            lst.append(cls)
            for arg in type_args(cls):
                recursive(arg)
        elif is_pep695_type_alias(cls):
            recursive(cls.__value__)
        if is_dataclass(cls):
            stack.append(cls)
            for f in dataclass_fields(cls):
                recursive(f.type)
            stack.pop()
        elif is_opt(cls):
            args = type_args(cls)
            if args:
                recursive(args[0])
        elif is_list(cls) or is_set(cls):
            args = type_args(cls)
            if args:
                recursive(args[0])
        elif is_tuple(cls):
            for arg in type_args(cls):
                recursive(arg)
        elif is_dict(cls):
            args = type_args(cls)
            if args and len(args) >= 2:
                recursive(args[0])
                recursive(args[1])

    recursive(cls)
    return lst


def iter_literals(cls: type[Any]) -> list[TypeLike]:
    """
    Iterate over all literals that are used in the dataclass
    """
    lst: set[Union[type[Any], Any]] = set()

    def recursive(cls: Union[type[Any], Any]) -> None:
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
            args = type_args(cls)
            if args:
                recursive(args[0])
        elif is_list(cls) or is_set(cls):
            args = type_args(cls)
            if args:
                recursive(args[0])
        elif is_tuple(cls):
            for arg in type_args(cls):
                recursive(arg)
        elif is_dict(cls):
            args = type_args(cls)
            if args and len(args) >= 2:
                recursive(args[0])
                recursive(args[1])

    recursive(cls)
    return list(lst)


@cache
def is_union(typ: Any) -> bool:
    """
    Test if the type is `typing.Union`.

    >>> is_union(Union[int, str])
    True
    """

    try:
        # When `_WithTagging` is received, it will check inner type.
        if isinstance(typ, _WithTagging):
            return is_union(typ.inner)
    except Exception:
        pass

    # Python 3.10 Union operator e.g. str | int
    if sys.version_info[:2] >= (3, 10):
        try:
            if isinstance(typ, types.UnionType):
                return True
        except Exception:
            pass

    # typing.Union
    return typing_inspect.is_union_type(typ)  # type: ignore


@cache
def is_opt(typ: Any) -> bool:
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
        return (
            (is_union_type or is_typing_union)
            and len(args) == 2
            and not is_none(args[0])
            and is_none(args[1])
        )
    else:
        return typ is Optional


@cache
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


@cache
def is_opt_dataclass(typ: Any) -> bool:
    """
    Test if the type is optional dataclass.

    >>> is_opt_dataclass(Optional[int])
    False
    >>> @dataclasses.dataclass
    ... class Foo:
    ...     pass
    >>> is_opt_dataclass(Foo)
    False
    >>> is_opt_dataclass(Optional[Foo])
    False
    """
    args = get_args(typ)
    return is_opt(typ) and len(args) > 0 and is_dataclass(args[0])


@cache
def is_list(typ: type[Any]) -> bool:
    """
    Test if the type is `list`.

    >>> is_list(list[int])
    True
    >>> is_list(list)
    True
    """
    try:
        return issubclass(get_origin(typ), list)  # type: ignore
    except TypeError:
        return typ is list


@cache
def is_bare_list(typ: type[Any]) -> bool:
    """
    Test if the type is `list` without type args.

    >>> is_bare_list(list[int])
    False
    >>> is_bare_list(list)
    True
    """
    return typ is list


@cache
def is_tuple(typ: Any) -> bool:
    """
    Test if the type is tuple.
    """
    try:
        return issubclass(get_origin(typ), tuple)  # type: ignore
    except TypeError:
        return typ is tuple


@cache
def is_bare_tuple(typ: type[Any]) -> bool:
    """
    Test if the type is tuple without type args.

    >>> is_bare_tuple(tuple[int, str])
    False
    >>> is_bare_tuple(tuple)
    True
    """
    return typ is tuple


@cache
def is_variable_tuple(typ: type[Any]) -> bool:
    """
    Test if the type is a variable length of tuple tuple[T, ...]`.

    >>> is_variable_tuple(tuple[int, ...])
    True
    >>> is_variable_tuple(tuple[int, bool])
    False
    >>> is_variable_tuple(tuple[()])
    False
    """
    istuple = is_tuple(typ) and not is_bare_tuple(typ)
    args = get_args(typ)
    return istuple and len(args) == 2 and is_ellipsis(args[1])


@cache
def is_set(typ: type[Any]) -> bool:
    """
    Test if the type is `set` or `frozenset`.

    >>> is_set(set[int])
    True
    >>> is_set(set)
    True
    >>> is_set(frozenset[int])
    True
    """
    try:
        return issubclass(get_origin(typ), (set, frozenset))  # type: ignore
    except TypeError:
        return typ in (set, frozenset)


@cache
def is_bare_set(typ: type[Any]) -> bool:
    """
    Test if the type is `set` without type args.

    >>> is_bare_set(set[int])
    False
    >>> is_bare_set(set)
    True
    """
    return typ in (set, frozenset)


@cache
def is_frozen_set(typ: type[Any]) -> bool:
    """
    Test if the type is `frozenset`.

    >>> is_frozen_set(frozenset[int])
    True
    >>> is_frozen_set(set)
    False
    """
    try:
        return issubclass(get_origin(typ), frozenset)  # type: ignore
    except TypeError:
        return typ is frozenset


@cache
def is_dict(typ: type[Any]) -> bool:
    """
    Test if the type is dict.

    >>> is_dict(dict[int, int])
    True
    >>> is_dict(dict)
    True
    >>> is_dict(defaultdict[int, int])
    True
    """
    try:
        return issubclass(get_origin(typ), (dict, defaultdict))  # type: ignore
    except TypeError:
        return typ in (dict, defaultdict)


@cache
def is_bare_dict(typ: type[Any]) -> bool:
    """
    Test if the type is `dict` without type args.

    >>> is_bare_dict(dict[int, str])
    False
    >>> is_bare_dict(dict)
    True
    """
    return typ is dict


@cache
def is_default_dict(typ: type[Any]) -> bool:
    """
    Test if the type is `defaultdict`.

    >>> is_default_dict(defaultdict[int, int])
    True
    >>> is_default_dict(dict[int, int])
    False
    """
    try:
        return issubclass(get_origin(typ), defaultdict)  # type: ignore
    except TypeError:
        return typ is defaultdict


@cache
def is_none(typ: type[Any]) -> bool:
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


@cache
def is_enum(typ: type[Any]) -> TypeGuard[enum.Enum]:
    """
    Test if the type is `enum.Enum`.
    """
    try:
        return issubclass(typ, enum.Enum)
    except TypeError:
        return isinstance(typ, enum.Enum)


@cache
def is_primitive_subclass(typ: type[Any]) -> bool:
    """
    Test if the type is a subclass of primitive type.

    >>> is_primitive_subclass(str)
    False
    >>> class Str(str):
    ...     pass
    >>> is_primitive_subclass(Str)
    True
    """
    return is_primitive(typ) and typ not in PRIMITIVES and not is_new_type_primitive(typ)


@cache
def is_primitive(typ: Union[type[Any], NewType]) -> bool:
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
        return any(issubclass(typ, ty) for ty in PRIMITIVES)  # type: ignore
    except TypeError:
        return is_new_type_primitive(typ)


@cache
def is_new_type_primitive(typ: Union[type[Any], NewType]) -> bool:
    """
    Test if the type is a NewType of primitives.
    """
    inner = getattr(typ, "__supertype__", None)
    if inner:
        return is_primitive(inner)
    else:
        return any(isinstance(typ, ty) for ty in PRIMITIVES)


@cache
def has_generic_base(typ: Any) -> bool:
    return Generic in getattr(typ, "__mro__", ()) or Generic in getattr(typ, "__bases__", ())


@cache
def is_generic(typ: Any) -> bool:
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
    return origin is not None and has_generic_base(origin)


@cache
def is_class_var(typ: type[Any]) -> bool:
    """
    Test if the type is `typing.ClassVar`.

    >>> is_class_var(ClassVar[int])
    True
    >>> is_class_var(ClassVar)
    True
    """
    return get_origin(typ) is ClassVar or typ is ClassVar  # type: ignore


@cache
def is_literal(typ: type[Any]) -> bool:
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
    return origin is not None and origin is typing.Literal


@cache
def is_any(typ: type[Any]) -> bool:
    """
    Test if the type is `typing.Any`.
    """
    return typ is Any  # type: ignore


@cache
def is_str_serializable(typ: type[Any]) -> bool:
    """
    Test if the type is serializable to `str`.
    """
    return typ in StrSerializableTypes or (
        type(typ) is type and issubclass(typ, StrSerializableTypes)
    )


def is_datetime(
    typ: type[Any],
) -> TypeGuard[Union[datetime.date, datetime.time, datetime.datetime]]:
    """
    Test if the type is any of the datetime types..
    """
    return typ in DateTimeTypes or (type(typ) is type and issubclass(typ, DateTimeTypes))


def is_str_serializable_instance(obj: Any) -> bool:
    return isinstance(obj, StrSerializableTypes)


def is_datetime_instance(obj: Any) -> bool:
    return isinstance(obj, DateTimeTypes)


def is_ellipsis(typ: Any) -> bool:
    return typ is Ellipsis


def is_pep695_type_alias(typ: Any) -> bool:
    """
    Test if the type is of PEP695 type alias.
    """
    return isinstance(typ, TypeAliasType)


@cache
def get_type_var_names(cls: type[Any]) -> Optional[list[str]]:
    """
    Get type argument names of a generic class.

    >>> T = typing.TypeVar('T')
    >>> class GenericFoo(typing.Generic[T]):
    ...     pass
    >>> get_type_var_names(GenericFoo)
    ['T']
    >>> get_type_var_names(int)
    """
    bases = getattr(cls, "__orig_bases__", ())
    if not bases:
        return None

    type_arg_names: list[str] = []
    for base in bases:
        type_arg_names.extend(arg.__name__ for arg in get_args(base) if hasattr(arg, "__name__"))

    return type_arg_names


def find_generic_arg(cls: type[Any], field: TypeVar) -> int:
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
        raise Exception(f'"__orig_bases__" property was not found: {cls}')

    for base in bases:
        for n, arg in enumerate(get_args(base)):
            if arg.__name__ == field.__name__:
                return n

    if not bases:
        raise Exception(f"Generic field not found in class: {bases}")

    return -1


def get_generic_arg(
    typ: Any,
    maybe_generic_type_vars: Optional[list[str]],
    variable_type_args: Optional[list[str]],
    index: int,
) -> Any:
    """
    Get generic type argument.

    >>> T = typing.TypeVar('T')
    >>> U = typing.TypeVar('U')
    >>> class GenericFoo(typing.Generic[T, U]):
    ...     pass
    >>> get_generic_arg(GenericFoo[int, str], ['T', 'U'], ['T', 'U'], 0).__name__
    'int'
    >>> get_generic_arg(GenericFoo[int, str], ['T', 'U'], ['T', 'U'], 1).__name__
    'str'
    >>> get_generic_arg(GenericFoo[int, str], ['T', 'U'], ['U'], 0).__name__
    'str'
    """
    if not is_generic(typ) or maybe_generic_type_vars is None or variable_type_args is None:
        return typing.Any

    args = get_args(typ)

    if len(args) != len(maybe_generic_type_vars):
        raise SerdeError(
            f"Number of type args for {typ} does not match number of generic type vars: "
            f"\n  type args: {args}\n  type_vars: {maybe_generic_type_vars}"
        )

    # Get the name of the type var used for this field in the parent class definition
    type_var_name = variable_type_args[index]

    try:
        # Find the slot of that type var in the original generic class definition
        orig_index = maybe_generic_type_vars.index(type_var_name)
    except ValueError:
        return typing.Any

    return args[orig_index]
