"""
pyserde core module.
"""
import dataclasses
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional, Type, Union

import stringcase

from .compat import (
    is_bare_dict,
    is_bare_list,
    is_bare_set,
    is_bare_tuple,
    is_dict,
    is_list,
    is_opt,
    is_set,
    is_tuple,
    is_union,
    type_args,
    typename,
)

__all__: List = []

logger = logging.getLogger('serde')


# name of the serde context key
SERDE_SCOPE = '__serde__'

# main function keys
FROM_ITER = 'from_iter'
FROM_DICT = 'from_dict'
TO_ITER = 'to_iter'
TO_DICT = 'to_dict'

# prefixes used to distinguish the direction of a union function
UNION_SE_PREFIX = "union_se"
UNION_DE_PREFIX = "union_de"

SETTINGS = dict(debug=False)


def init(debug: bool = False):
    SETTINGS['debug'] = debug


@dataclass
class SerdeScope:
    cls: Type  # the exact class this scope is for (needed to distinguish scopes between inherited classes)

    # generated serialize and deserialize functions
    funcs: Dict[str, callable] = field(default_factory=dict)
    # default values of the dataclass fields (factories & normal values)
    defaults: Dict[str, Union[callable, Any]] = field(default_factory=dict)
    # type references to all used types within the dataclass
    types: Dict[str, Type] = field(default_factory=dict)

    # generated source code (only filled when debug is True)
    code: Dict[str, str] = field(default_factory=dict)

    # the union serializing functions need references to their types
    union_se_args: Dict[str, List[Type]] = field(default_factory=dict)

    # default values for to_dict & from_dict arguments
    reuse_instances_default: bool = True
    convert_sets_default: bool = False


class SerdeError(TypeError):
    """
    Serde error class.
    """


def raise_unsupported_type(obj):
    # needed because we can not render a raise statement everywhere, e.g. as argument
    raise SerdeError(f"Unsupported type: {typename(type(obj))}")


def gen(code: str, globals: Dict = None, locals: Dict = None) -> str:
    """
    Customized `exec` function.
    """
    try:
        from black import FileMode, format_str

        code = format_str(code, mode=FileMode(line_length=100))
    except Exception:
        pass
    exec(code, globals, locals)
    return code


def add_func(serde_scope: SerdeScope, func_name: str, func_code: str, globals: Dict) -> None:
    """
    Generate a function and add it to a SerdeScope's `funcs` dictionary.
    :param serde_scope: the SerdeScope instance to modify
    :param func_name: the name of the function
    :param func_code: the source code of the function
    :param globals: global variables that should be accessible to the generated function
    """

    code = gen(func_code, globals)
    serde_scope.funcs[func_name] = globals[func_name]

    if SETTINGS['debug']:
        serde_scope.code[func_name] = code


def is_instance(obj: Any, typ: Type) -> bool:
    if is_opt(typ):
        if obj is None:
            return True
        opt_arg = type_args(typ)[0]
        return is_instance(obj, opt_arg)
    elif is_union(typ):
        for arg in type_args(typ):
            if is_instance(obj, arg):
                return True
        return False
    elif is_list(typ):
        if not isinstance(obj, list):
            return False
        if len(obj) == 0 or is_bare_list(typ):
            return True
        list_arg = type_args(typ)[0]
        # for speed reasons we just check the type of the 1st element
        return is_instance(obj[0], list_arg)
    elif is_set(typ):
        if not isinstance(obj, set):
            return False
        if len(obj) == 0 or is_bare_set(typ):
            return True
        set_arg = type_args(typ)[0]
        # for speed reasons we just check the type of the 1st element
        return is_instance(next(iter(obj)), set_arg)
    elif is_tuple(typ):
        if not isinstance(obj, tuple):
            return False
        if len(obj) == 0 or is_bare_tuple(typ):
            return True
        for i, arg in enumerate(type_args(typ)):
            if not is_instance(obj[i], arg):
                return False
        return True
    elif is_dict(typ):
        if not isinstance(obj, dict):
            return False
        if len(obj) == 0 or is_bare_dict(typ):
            return True
        ktyp = type_args(typ)[0]
        vtyp = type_args(typ)[1]
        for k, v in obj.items():
            # for speed reasons we just check the type of the 1st element
            return is_instance(k, ktyp) and is_instance(v, vtyp)
        return False
    else:
        return isinstance(obj, typ)


@dataclass
class Func:
    """
    Function wrapper that has `mangled` optional field.

    pyserde copies every function reference into global scope
    for code generation. Mangling function names is needed in
    order to avoid name conflict in the global scope when
    multiple fields receives `skip_if` attribute.
    """

    inner: Callable[[Any], bool]
    mangeld: str = ""

    def __call__(self, v) -> bool:
        return self.inner(v)  # type: ignore

    @property
    def name(self) -> str:
        return self.mangeld


def skip_if_false(v):
    return not bool(v)


@dataclass
class Field:
    """
    Field in pyserde class.
    """

    type: Type
    name: Optional[str]
    default: Any = field(default_factory=dataclasses._MISSING_TYPE)
    default_factory: Any = field(default_factory=dataclasses._MISSING_TYPE)
    case: Optional[str] = None
    rename: Optional[str] = None
    skip: Optional[bool] = None
    skip_if: Optional[Func] = None
    skip_if_false: Optional[bool] = None

    @classmethod
    def from_dataclass(cls, f: dataclasses.Field) -> 'Field':
        skip_if_false_func: Optional[Func] = None
        if f.metadata.get('serde_skip_if_false'):
            skip_if_false_func = Func(skip_if_false, cls.mangle(f, 'skip_if'))

        skip_if: Optional[Func] = None
        if f.metadata.get('serde_skip_if'):
            func = f.metadata.get('serde_skip_if')
            if callable(func):
                skip_if = Func(func, cls.mangle(f, 'skip_if'))

        return cls(
            f.type,
            f.name,
            default=f.default,
            default_factory=f.default_factory,  # type: ignore
            rename=f.metadata.get('serde_rename'),
            skip=f.metadata.get('serde_skip'),
            skip_if=skip_if or skip_if_false_func,
        )

    @staticmethod
    def mangle(field: dataclasses.Field, name: str) -> str:
        """
        Get mangled name based on field name.
        """
        return f'{field.name}_{name}'

    @property
    def conv_name(self) -> str:
        """
        Get an actual field name which `rename` and `rename_all` conversions
        are made. Use `name` property to get a field name before conversion.
        """
        return conv(self, self.case)


def fields(FieldCls: Type, cls: Type) -> Iterator[Field]:
    return iter(FieldCls.from_dataclass(f) for f in dataclasses.fields(cls))


def conv(f: Field, case: Optional[str] = None) -> str:
    """
    Convert field name.
    """
    name = f.name
    if case:
        casef = getattr(stringcase, case, None)
        if not casef:
            raise SerdeError(f"Unkown case type: {f.case}. Pass the name of case supported by 'stringcase' package.")
        name = casef(name)
    if f.rename:
        name = f.rename
    if name is None:
        raise SerdeError('Field name is None.')
    return name


def union_func_name(prefix: str, union_args: List[Type]) -> str:
    """
    Generate a function name that contains all union types
    :param prefix: prefix to distinguish between serializing and deserializing
    :param union_args: type arguments of a Union
    :return: union function name
    >>> from ipaddress import IPv4Address
    >>> from typing import List
    >>> union_func_name("union_se", [int, List[str], IPv4Address])
    'union_se_int_List_str__IPv4Address'
    """
    return re.sub(r"[ ,\[\]]+", "_", f"{prefix}_{'_'.join([typename(e) for e in union_args])}")
