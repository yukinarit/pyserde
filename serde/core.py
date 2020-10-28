"""
pyserde core module.
"""
import dataclasses
import logging
from dataclasses import dataclass, field, is_dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional, Type, TypeVar

import stringcase

from .compat import T, assert_type, is_dict, is_list, is_opt, is_tuple, is_union, type_args

__all__: List = []

logger = logging.getLogger('serde')

JsonValue = TypeVar('JsonValue', str, int, float, bool, Dict, List)

SE_NAME = '__serde_serialize__'

FROM_ITER = '__serde_from_iter__'

FROM_DICT = '__serde_from_dict__'

TO_ITER = '__serde_to_iter__'

TO_DICT = '__serde_to_dict__'

HIDDEN_NAME = '__serde_hidden__'

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


def typecheck(cls: Type[T], obj: T) -> None:
    """
    type check type-annotated classes.

    >>> @dataclass
    ... class Foo:
    ...     s: str
    >>>
    >>> typecheck(Foo, Foo('foo'))
    >>>
    >>> # Type mismatch raises `ValueError`.
    >>> try:
    ...     typecheck(Foo, Foo(10))
    ... except:
    ...     pass
    >>>
    """
    if is_dataclass(obj):
        # If dataclass, type check recursively.
        for f in dataclasses.fields(obj):
            typecheck(f.type, getattr(obj, f.name, None))
    elif is_opt(cls):
        if obj is not None:
            typ = type_args(cls)[0]
            typecheck(typ, obj)
    elif is_union(cls):
        success = False
        for typ in type_args(cls):
            try:
                typecheck(typ, obj)
                success = True
                break
            except (SerdeError, ValueError):
                pass
        if not success:
            raise ValueError(f'{obj} is not instance of {cls}')
    elif is_list(cls):
        assert_type(list, obj)
        if isinstance(obj, list):
            typ = type_args(cls)[0]
            for e in obj:
                typecheck(typ, e)
    elif is_tuple(cls):
        assert_type(tuple, obj)
        if isinstance(obj, tuple):
            for i, typ in enumerate(type_args(cls)):
                typecheck(typ, obj[i])
    elif is_dict(cls):
        assert_type(dict, obj)
        if isinstance(obj, dict):
            ktyp = type_args(cls)[0]
            vtyp = type_args(cls)[1]
            for k, v in obj.items():
                typecheck(ktyp, k)
                typecheck(vtyp, v)
    else:
        if not isinstance(obj, cls):
            raise ValueError(f'{obj} is not instance of {cls}')


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
