"""
pyserde core module.
"""
import dataclasses
import logging
from dataclasses import dataclass, field, is_dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional, Type, TypeVar, _GenericAlias

import stringcase

from .compat import T, is_dict, is_list, is_opt, is_tuple, is_union, type_args, is_bare_list, is_bare_dict, \
    is_bare_tuple

__all__: List = []

logger = logging.getLogger('serde')

JsonValue = TypeVar('JsonValue', str, int, float, bool, Dict, List)

FROM_ITER = '__serde_from_iter__'

FROM_DICT = '__serde_from_dict__'

TO_ITER = '__serde_to_iter__'

TO_DICT = '__serde_to_dict__'

HIDDEN_NAME = '__serde_hidden__'

UNION_SE_PREFIX = '__serde_union_se_'

UNION_DE_PREFIX = '__serde_union_de_'

UNION_ARGS = '__union_args__'

SETTINGS = dict(debug=False)


@dataclass
class Hidden:
    """
    Hidden information encoded in serde classes.
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
    except Exception:
        pass
    for_class = 'for ' + cls.__name__ if cls else ''
    logger.debug(f'Generating {for_class} ...\n{code}')
    exec(code, globals, locals)
    return code


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
    elif is_set(cls):
        assert_type(set, obj)
        if isinstance(obj, set):
            typ = type_args(cls)[0]
            for e in obj:
                typecheck(typ, e)
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


def fields(FieldCls: Type, cls: Type) -> Iterator[Field]:
    return iter(FieldCls.from_dataclass(f) for f in dataclasses.fields(cls))


def conv(f: Field, case: Optional[str] = None) -> str:
    """
    Convert field name.
    """
    name = f.name
    if case:
        casef = getattr(stringcase, case or '', None)
        if not casef:
            raise SerdeError(
                (f"Unkown case type: {f.case}." f"Pass the name of case supported by 'stringcase' package.")
            )
        name = casef(f.name)
    if f.rename:
        name = f.rename
    if name is None:
        raise SerdeError('Field name is None.')
    return name


def union_func_suffix(union_args: List[Type]) -> str:
    """
    Generates a function name suffix which contains all types of the union in its name.
    Use this together with UNION_SE_PREFIX or UNION_DE_PREFIX.
    :param union_args: type arguments of a Union annotation
    :return: function name suffix

    >>> from typing import List, Dict
    >>> from ipaddress import IPv4Network
    >>> union_func_suffix([str, List[int], Dict[str, IPv4Network]])
    'str_List_int___Dict_str_IPv4Network____'
    """
    name = ""
    for arg in union_args:
        # handles container types like List,Tuple & Dict
        if isinstance(arg, _GenericAlias):
            name += f"{arg._name}_{union_func_suffix(type_args(arg))}"
        else:
            name += arg.__name__
        name += "_"
    return name + "_"
