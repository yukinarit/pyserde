import sys
from typing import Type, List, Tuple, Dict
from typing_inspect import is_optional_type, get_origin


def is_opt(typ: Type) -> bool:
    """
    Test if the type is Optional.
    """
    return is_optional_type(typ)


def is_list(typ: Type) -> bool:
    """
    Test if the type is List.
    """
    if sys.version_info < (3, 7):
        return issubclass(typ, List)
    else:
        return get_origin(typ) is list


def is_tuple(typ: Type) -> bool:
    """
    Test if the type is Tuple.
    """
    if sys.version_info < (3, 7):
        return issubclass(typ, Tuple)
    else:
        return get_origin(typ) is tuple


def is_dict(typ: Type) -> bool:
    """
    Test if the type is Dict.
    """
    if sys.version_info < (3, 7):
        return issubclass(typ, Dict)
    else:
        return get_origin(typ) is dict
