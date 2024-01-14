"""
pyserde core module.
"""
from __future__ import annotations
import dataclasses
import enum
import functools
import logging
import sys
import re
from dataclasses import dataclass
from typing import (
    overload,
    Dict,
    Type,
    TypeVar,
    Generic,
    Optional,
    Any,
    Protocol,
    Mapping,
    Sequence,
)
from beartype.typing import (
    Callable,
    List,
    Union,
    Tuple,
)

import casefy
from typing_extensions import get_type_hints

from .compat import (
    DataclassField,
    T,
    SerdeError,
    dataclass_fields,
    get_origin,
    is_bare_dict,
    is_bare_list,
    is_bare_set,
    is_bare_tuple,
    is_class_var,
    is_dict,
    is_generic,
    is_list,
    is_literal,
    is_new_type_primitive,
    is_any,
    is_opt,
    is_set,
    is_tuple,
    is_union,
    is_variable_tuple,
    type_args,
    typename,
    _WithTagging,
)

__all__ = [
    "Scope",
    "gen",
    "add_func",
    "Func",
    "Field",
    "fields",
    "FlattenOpts",
    "conv",
    "union_func_name",
]

logger = logging.getLogger("serde")


# name of the serde context key
SERDE_SCOPE = "__serde__"

# main function keys
FROM_ITER = "from_iter"
FROM_DICT = "from_dict"
TO_ITER = "to_iter"
TO_DICT = "to_dict"
TYPE_CHECK = "typecheck"

# prefixes used to distinguish the direction of a union function
UNION_SE_PREFIX = "union_se"
UNION_DE_PREFIX = "union_de"

LITERAL_DE_PREFIX = "literal_de"

SETTINGS = {"debug": False}


def init(debug: bool = False) -> None:
    SETTINGS["debug"] = debug


@dataclass
class Cache:
    """
    Cache the generated code for non-dataclass classes.

    for example, a type not bound in a dataclass is passed in from_json

    ```
    from_json(Union[Foo, Bar], ...)
    ```

    It creates the following wrapper dataclass on the fly,

    ```
    @serde
    @dataclass
    class Union_Foo_bar:
        v: Union[Foo, Bar]
    ```

    Then store this class in this cache. Whenever the same type is passed,
    the class is retrieved from this cache. So the overhead of the codegen
    should be only once.
    """

    classes: Dict[str, Type[Any]] = dataclasses.field(default_factory=dict)

    def _get_class(self, cls: Type[Any]) -> Type[Any]:
        """
        Get a wrapper class from the the cache. If not found, it will generate
        the class and store it in the cache.
        """
        class_name = f"Wrapper{typename(cls)}"
        wrapper = self.classes.get(class_name)
        return wrapper or self._generate_class(cls)

    def _generate_class(self, cls: Type[Any]) -> Type[Any]:
        """
        Generate a wrapper dataclass then make the it (de)serializable using
        @serde decorator.
        """
        from . import serde

        class_name = f"Wrapper{typename(cls)}"
        logger.debug(f"Generating a wrapper class code for {class_name}")

        wrapper = dataclasses.make_dataclass(class_name, [("v", cls)])

        serde(wrapper)
        self.classes[class_name] = wrapper

        logger.debug(f"(de)serializing code for {class_name} was generated")
        return wrapper

    def serialize(self, cls: Type[Any], obj: Any) -> Any:
        """
        Serialize the specified type of object into dict or tuple.
        """
        wrapper = self._get_class(cls)
        scope: Scope = getattr(wrapper, SERDE_SCOPE)
        data = scope.funcs[TO_DICT](wrapper(obj), reuse_instances=False, convert_sets=True)

        logging.debug(f"Intermediate value: {data}")

        return data["v"]

    def deserialize(self, cls: Type[T], obj: Any) -> T:
        """
        Deserialize from dict or tuple into the specified type.
        """
        wrapper = self._get_class(cls)
        scope: Scope = getattr(wrapper, SERDE_SCOPE)
        return scope.funcs[FROM_DICT](data={"v": obj}).v  # type: ignore

    def _get_union_class(self, cls: Type[Any]) -> Optional[Type[Any]]:
        """
        Get a wrapper class from the the cache. If not found, it will generate
        the class and store it in the cache.
        """
        union_cls, tagging = _extract_from_with_tagging(cls)
        class_name = union_func_name(
            f"{tagging.produce_unique_class_name()}Union", list(type_args(union_cls))
        )
        wrapper = self.classes.get(class_name)
        return wrapper or self._generate_union_class(cls)

    def _generate_union_class(self, cls: Type[Any]) -> Type[Any]:
        """
        Generate a wrapper dataclass then make the it (de)serializable using
        @serde decorator.
        """
        import serde

        union_cls, tagging = _extract_from_with_tagging(cls)
        class_name = union_func_name(
            f"{tagging.produce_unique_class_name()}Union", list(type_args(union_cls))
        )
        wrapper = dataclasses.make_dataclass(class_name, [("v", union_cls)])
        serde.serde(wrapper, tagging=tagging)
        self.classes[class_name] = wrapper
        return wrapper

    def serialize_union(self, cls: Type[Any], obj: Any) -> Any:
        """
        Serialize the specified Union into dict or tuple.
        """
        union_cls, _ = _extract_from_with_tagging(cls)
        wrapper = self._get_union_class(cls)
        scope: Scope = getattr(wrapper, SERDE_SCOPE)
        func_name = union_func_name(UNION_SE_PREFIX, list(type_args(union_cls)))
        return scope.funcs[func_name](obj, False, False)

    def deserialize_union(self, cls: Type[T], data: Any) -> T:
        """
        Deserialize from dict or tuple into the specified Union.
        """
        union_cls, _ = _extract_from_with_tagging(cls)
        wrapper = self._get_union_class(cls)
        scope: Scope = getattr(wrapper, SERDE_SCOPE)
        func_name = union_func_name(UNION_DE_PREFIX, list(type_args(union_cls)))
        return scope.funcs[func_name](cls=union_cls, data=data)  # type: ignore


def _extract_from_with_tagging(maybe_with_tagging: Any) -> Tuple[Any, Tagging]:
    try:
        if isinstance(maybe_with_tagging, _WithTagging):
            union_cls = maybe_with_tagging.inner
            tagging = maybe_with_tagging.tagging
        else:
            raise Exception()
    except Exception:
        union_cls = maybe_with_tagging
        tagging = ExternalTagging

    return (union_cls, tagging)


CACHE = Cache()
""" Global cache variable for non-dataclass classes """


@dataclass
class Scope:
    """
    Container to store types and functions used in code generation context.
    """

    cls: Type[Any]
    """ The exact class this scope is for
    (needed to distinguish scopes between inherited classes) """

    funcs: Dict[str, Callable[..., Any]] = dataclasses.field(default_factory=dict)
    """ Generated serialize and deserialize functions """

    defaults: Dict[str, Union[Callable[..., Any], Any]] = dataclasses.field(default_factory=dict)
    """ Default values of the dataclass fields (factories & normal values) """

    code: Dict[str, str] = dataclasses.field(default_factory=dict)
    """ Generated source code (only filled when debug is True) """

    union_se_args: Dict[str, List[Type[Any]]] = dataclasses.field(default_factory=dict)
    """ The union serializing functions need references to their types """

    reuse_instances_default: bool = True
    """ Default values for to_dict & from_dict arguments """

    convert_sets_default: bool = False

    def __repr__(self) -> str:
        res: List[str] = []

        res.append("==================================================")
        res.append(self._justify(self.cls.__name__))
        res.append("==================================================")
        res.append("")

        if self.code:
            res.append("--------------------------------------------------")
            res.append(self._justify("Functions generated by pyserde"))
            res.append("--------------------------------------------------")
            res.extend(list(self.code.values()))
            res.append("")

        if self.funcs:
            res.append("--------------------------------------------------")
            res.append(self._justify("Function references in scope"))
            res.append("--------------------------------------------------")
            for k, v in self.funcs.items():
                res.append(f"{k}: {v}")
            res.append("")

        if self.defaults:
            res.append("--------------------------------------------------")
            res.append(self._justify("Default values for the dataclass fields"))
            res.append("--------------------------------------------------")
            for k, v in self.defaults.items():
                res.append(f"{k}: {v}")
            res.append("")

        if self.union_se_args:
            res.append("--------------------------------------------------")
            res.append(self._justify("Type list by used for union serialize functions"))
            res.append("--------------------------------------------------")
            for k, lst in self.union_se_args.items():
                res.append(f"{k}: {list(lst)}")
            res.append("")

        return "\n".join(res)

    def _justify(self, s: str, length: int = 50) -> str:
        white_spaces = int((50 - len(s)) / 2)
        return " " * (white_spaces if white_spaces > 0 else 0) + s


def raise_unsupported_type(obj: Any) -> None:
    # needed because we can not render a raise statement everywhere, e.g. as argument
    raise SerdeError(f"Unsupported type: {typename(type(obj))}")


def gen(
    code: str, globals: Optional[Dict[str, Any]] = None, locals: Optional[Dict[str, Any]] = None
) -> str:
    """
    A wrapper of builtin `exec` function.
    """
    if SETTINGS["debug"]:
        # black formatting is only important when debugging
        try:
            from black import FileMode, format_str

            code = format_str(code, mode=FileMode(line_length=100))
        except Exception:
            pass
    exec(code, globals, locals)
    return code


def add_func(serde_scope: Scope, func_name: str, func_code: str, globals: Dict[str, Any]) -> None:
    """
    Generate a function and add it to a Scope's `funcs` dictionary.

    * `serde_scope`: the Scope instance to modify
    * `func_name`: the name of the function
    * `func_code`: the source code of the function
    * `globals`: global variables that should be accessible to the generated function
    """

    code = gen(func_code, globals)
    serde_scope.funcs[func_name] = globals[func_name]

    if SETTINGS["debug"]:
        serde_scope.code[func_name] = code


def is_instance(obj: Any, typ: Any) -> bool:
    """
    Type check function that works like `isinstance` but it accepts
    Subscripted Generics e.g. `List[int]`.
    """
    if dataclasses.is_dataclass(typ):
        return isinstance(obj, typ)
    elif is_opt(typ):
        return is_opt_instance(obj, typ)
    elif is_union(typ):
        return is_union_instance(obj, typ)
    elif is_list(typ):
        return is_list_instance(obj, typ)
    elif is_set(typ):
        return is_set_instance(obj, typ)
    elif is_tuple(typ):
        return is_tuple_instance(obj, typ)
    elif is_dict(typ):
        return is_dict_instance(obj, typ)
    elif is_generic(typ):
        return is_generic_instance(obj, typ)
    elif is_literal(typ):
        return True
    elif is_new_type_primitive(typ):
        inner = getattr(typ, "__supertype__", None)
        if type(inner) is type:
            return isinstance(obj, inner)
        else:
            return False
    elif is_any(typ):
        return True
    elif typ is Ellipsis:
        return True
    else:
        return isinstance(obj, typ)


def is_opt_instance(obj: Any, typ: Type[Any]) -> bool:
    if obj is None:
        return True
    opt_arg = type_args(typ)[0]
    return is_instance(obj, opt_arg)


def is_union_instance(obj: Any, typ: Type[Any]) -> bool:
    for arg in type_args(typ):
        if is_instance(obj, arg):
            return True
    return False


def is_list_instance(obj: Any, typ: Type[Any]) -> bool:
    if not isinstance(obj, list):
        return False
    if len(obj) == 0 or is_bare_list(typ):
        return True
    list_arg = type_args(typ)[0]
    # for speed reasons we just check the type of the 1st element
    return is_instance(obj[0], list_arg)


def is_set_instance(obj: Any, typ: Type[Any]) -> bool:
    if not isinstance(obj, (set, frozenset)):
        return False
    if len(obj) == 0 or is_bare_set(typ):
        return True
    set_arg = type_args(typ)[0]
    # for speed reasons we just check the type of the 1st element
    return is_instance(next(iter(obj)), set_arg)


def is_tuple_instance(obj: Any, typ: Type[Any]) -> bool:
    if not isinstance(obj, tuple):
        return False
    if is_variable_tuple(typ):
        arg = type_args(typ)[0]
        for v in obj:
            if not is_instance(v, arg):
                return False
    if len(obj) == 0 or is_bare_tuple(typ):
        return True
    for i, arg in enumerate(type_args(typ)):
        if not is_instance(obj[i], arg):
            return False
    return True


def is_dict_instance(obj: Any, typ: Type[Any]) -> bool:
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


def is_generic_instance(obj: Any, typ: Type[Any]) -> bool:
    return is_instance(obj, get_origin(typ))


@dataclass
class Func:
    """
    Function wrapper that provides `mangled` optional field.

    pyserde copies every function reference into global scope
    for code generation. Mangling function names is needed in
    order to avoid name conflict in the global scope when
    multiple fields receives `skip_if` attribute.
    """

    inner: Callable[..., Any]
    """ Function to wrap in """

    mangeld: str = ""
    """ Mangled function name """

    def __call__(self, v: Any) -> None:
        return self.inner(v)  # type: ignore

    @property
    def name(self) -> str:
        """
        Mangled function name
        """
        return self.mangeld


def skip_if_false(v: Any) -> Any:
    return not bool(v)


def skip_if_default(v: Any, default: Optional[Any] = None) -> Any:
    return v == default  # Why return type is deduced to be Any?


@dataclass
class FlattenOpts:
    """
    Flatten options. Currently not used.
    """


def field(
    *args: Any,
    rename: Optional[str] = None,
    alias: Optional[List[str]] = None,
    skip: Optional[bool] = None,
    skip_if: Optional[Callable[[Any], Any]] = None,
    skip_if_false: Optional[bool] = None,
    skip_if_default: Optional[bool] = None,
    serializer: Optional[Callable[..., Any]] = None,
    deserializer: Optional[Callable[..., Any]] = None,
    flatten: Optional[Union[FlattenOpts, bool]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:
    """
    Declare a field with parameters.
    """
    if not metadata:
        metadata = {}

    if rename is not None:
        metadata["serde_rename"] = rename
    if alias is not None:
        metadata["serde_alias"] = alias
    if skip is not None:
        metadata["serde_skip"] = skip
    if skip_if is not None:
        metadata["serde_skip_if"] = skip_if
    if skip_if_false is not None:
        metadata["serde_skip_if_false"] = skip_if_false
    if skip_if_default is not None:
        metadata["serde_skip_if_default"] = skip_if_default
    if serializer:
        metadata["serde_serializer"] = serializer
    if deserializer:
        metadata["serde_deserializer"] = deserializer
    if flatten is True:
        metadata["serde_flatten"] = FlattenOpts()
    elif flatten:
        metadata["serde_flatten"] = flatten

    return dataclasses.field(*args, metadata=metadata, **kwargs)


@dataclass
class Field(Generic[T]):
    """
    Field class is similar to `dataclasses.Field`. It provides pyserde specific options.

    `type`, `name`, `default` and `default_factory` are the same members as `dataclasses.Field`.
    """

    type: Type[T]
    """ Type of Field """
    name: Optional[str]
    """ Name of Field """
    default: Any = field(default_factory=dataclasses._MISSING_TYPE)
    """ Default value of Field """
    default_factory: Any = field(default_factory=dataclasses._MISSING_TYPE)
    """ Default factory method of Field """
    init: bool = field(default_factory=dataclasses._MISSING_TYPE)
    repr: Any = field(default_factory=dataclasses._MISSING_TYPE)
    hash: Any = field(default_factory=dataclasses._MISSING_TYPE)
    compare: Any = field(default_factory=dataclasses._MISSING_TYPE)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    kw_only: bool = False
    case: Optional[str] = None
    alias: List[str] = field(default_factory=list)
    rename: Optional[str] = None
    skip: Optional[bool] = None
    skip_if: Optional[Func] = None
    skip_if_false: Optional[bool] = None
    skip_if_default: Optional[bool] = None
    serializer: Optional[Func] = None  # Custom field serializer.
    deserializer: Optional[Func] = None  # Custom field deserializer.
    flatten: Optional[FlattenOpts] = None
    parent: Optional[Type[Any]] = None
    type_args: Optional[List[str]] = None

    @classmethod
    def from_dataclass(cls, f: DataclassField, parent: Optional[Type[Any]] = None) -> Field[T]:
        """
        Create `Field` object from `dataclasses.Field`.
        """
        skip_if_false_func: Optional[Func] = None
        if f.metadata.get("serde_skip_if_false"):
            skip_if_false_func = Func(skip_if_false, cls.mangle(f, "skip_if_false"))

        skip_if_default_func: Optional[Func] = None
        if f.metadata.get("serde_skip_if_default"):
            skip_if_def = functools.partial(skip_if_default, default=f.default)
            skip_if_default_func = Func(skip_if_def, cls.mangle(f, "skip_if_default"))

        skip_if: Optional[Func] = None
        if f.metadata.get("serde_skip_if"):
            func = f.metadata.get("serde_skip_if")
            if callable(func):
                skip_if = Func(func, cls.mangle(f, "skip_if"))

        serializer: Optional[Func] = None
        func = f.metadata.get("serde_serializer")
        if func:
            serializer = Func(func, cls.mangle(f, "serializer"))

        deserializer: Optional[Func] = None
        func = f.metadata.get("serde_deserializer")
        if func:
            deserializer = Func(func, cls.mangle(f, "deserializer"))

        flatten = f.metadata.get("serde_flatten")
        if flatten is True:
            flatten = FlattenOpts()

        kw_only = bool(f.kw_only) if sys.version_info >= (3, 10) else False

        return cls(
            f.type,
            f.name,
            default=f.default,
            default_factory=f.default_factory,
            init=f.init,
            repr=f.repr,
            hash=f.hash,
            compare=f.compare,
            metadata=f.metadata,
            rename=f.metadata.get("serde_rename"),
            alias=f.metadata.get("serde_alias", []),
            skip=f.metadata.get("serde_skip"),
            skip_if=skip_if or skip_if_false_func or skip_if_default_func,
            serializer=serializer,
            deserializer=deserializer,
            flatten=flatten,
            parent=parent,
            kw_only=kw_only,
        )

    def to_dataclass(self) -> DataclassField:
        f = dataclasses.Field(
            default=self.default,
            default_factory=self.default_factory,
            init=self.init,
            repr=self.repr,
            hash=self.hash,
            compare=self.compare,
            metadata=self.metadata,
            kw_only=self.kw_only,
        )
        assert self.name
        f.name = self.name
        f.type = self.type
        return f

    def is_self_referencing(self) -> bool:
        if self.type is None:
            return False
        if self.parent is None:
            return False
        return self.type == self.parent

    @staticmethod
    def mangle(field: DataclassField, name: str) -> str:
        """
        Get mangled name based on field name.
        """
        return f"{field.name}_{name}"

    def conv_name(self, case: Optional[str] = None) -> str:
        """
        Get an actual field name which `rename` and `rename_all` conversions
        are made. Use `name` property to get a field name before conversion.
        """
        return conv(self, case or self.case)

    def supports_default(self) -> bool:
        return not getattr(self, "iterbased", False) and (
            has_default(self) or has_default_factory(self)
        )


F = TypeVar("F", bound=Field[Any])


def fields(field_cls: Type[F], cls: Type[Any], serialize_class_var: bool = False) -> List[F]:
    """
    Iterate fields of the dataclass and returns `serde.core.Field`.
    """
    fields = [field_cls.from_dataclass(f, parent=cls) for f in dataclass_fields(cls)]

    if serialize_class_var:
        for name, typ in get_type_hints(cls).items():
            if is_class_var(typ):
                fields.append(field_cls(typ, name, default=getattr(cls, name)))

    return fields  # type: ignore


def conv(f: Field[Any], case: Optional[str] = None) -> str:
    """
    Convert field name.
    """
    name = f.name
    if case:
        casef = getattr(casefy, case, None)
        if not casef:
            raise SerdeError(
                f"Unkown case type: {f.case}. Pass the name of case supported by 'casefy' package."
            )
        name = casef(name)
    if f.rename:
        name = f.rename
    if name is None:
        raise SerdeError("Field name is None.")
    return name


def union_func_name(prefix: str, union_args: Sequence[Any]) -> str:
    """
    Generate a function name that contains all union types

    * `prefix` prefix to distinguish between serializing and deserializing
    * `union_args`: type arguments of a Union

    >>> from ipaddress import IPv4Address
    >>> from typing import List
    >>> union_func_name("union_se", [int, List[str], IPv4Address])
    'union_se_int_List_str__IPv4Address'
    """
    return re.sub(r"[^A-Za-z0-9]", "_", f"{prefix}_{'_'.join([typename(e) for e in union_args])}")


def literal_func_name(literal_args: Sequence[Any]) -> str:
    """
    Generate a function name with all literals and corresponding types specified with Literal[...]


    * `literal_args`: arguments of a Literal

    >>> literal_func_name(["r", "w", "a", "x", "r+", "w+", "a+", "x+"])
    'literal_de_r_str_w_str_a_str_x_str_r__str_w__str_a__str_x__str'
    """
    return re.sub(
        r"[^A-Za-z0-9]",
        "_",
        f"{LITERAL_DE_PREFIX}_{'_'.join(f'{a}_{typename(type(a))}' for a in literal_args)}",
    )


@dataclass
class Tagging:
    """
    Controls how union is (de)serialized. This is the same concept as in
    https://serde.rs/enum-representations.html
    """

    class Kind(enum.Enum):
        External = enum.auto()
        Internal = enum.auto()
        Adjacent = enum.auto()
        Untagged = enum.auto()

    tag: Optional[str] = None
    content: Optional[str] = None
    kind: Kind = Kind.External

    def is_external(self) -> bool:
        return self.kind == self.Kind.External

    def is_internal(self) -> bool:
        return self.kind == self.Kind.Internal

    def is_adjacent(self) -> bool:
        return self.kind == self.Kind.Adjacent

    def is_untagged(self) -> bool:
        return self.kind == self.Kind.Untagged

    @classmethod
    def is_taggable(cls, typ: Type[Any]) -> bool:
        return dataclasses.is_dataclass(typ)

    def check(self) -> None:
        if self.is_internal() and self.tag is None:
            raise SerdeError('"tag" must be specified in InternalTagging')
        if self.is_adjacent() and (self.tag is None or self.content is None):
            raise SerdeError('"tag" and "content" must be specified in AdjacentTagging')

    def produce_unique_class_name(self) -> str:
        """
        Produce a unique class name for this tagging. The name is used for generated
        wrapper dataclass and stored in `Cache`.
        """
        if self.is_internal():
            tag = casefy.pascalcase(self.tag)  # type: ignore
            if not tag:
                raise SerdeError('"tag" must be specified in InternalTagging')
            return f"Internal{tag}"
        elif self.is_adjacent():
            tag = casefy.pascalcase(self.tag)  # type: ignore
            content = casefy.pascalcase(self.content)  # type: ignore
            if not tag:
                raise SerdeError('"tag" must be specified in AdjacentTagging')
            if not content:
                raise SerdeError('"content" must be specified in AdjacentTagging')
            return f"Adjacent{tag}{content}"
        else:
            return self.kind.name

    def __call__(self, cls: T) -> _WithTagging[T]:
        return _WithTagging(cls, self)


@overload
def InternalTagging(tag: str) -> Tagging:
    ...


@overload
def InternalTagging(tag: str, cls: T) -> _WithTagging[T]:
    ...


def InternalTagging(tag: str, cls: Optional[T] = None) -> Union[Tagging, _WithTagging[T]]:
    tagging = Tagging(tag, kind=Tagging.Kind.Internal)
    if cls:
        return tagging(cls)
    else:
        return tagging


@overload
def AdjacentTagging(tag: str, content: str) -> Tagging:
    ...


@overload
def AdjacentTagging(tag: str, content: str, cls: T) -> _WithTagging[T]:
    ...


def AdjacentTagging(
    tag: str, content: str, cls: Optional[T] = None
) -> Union[Tagging, _WithTagging[T]]:
    tagging = Tagging(tag, content, kind=Tagging.Kind.Adjacent)
    if cls:
        return tagging(cls)
    else:
        return tagging


ExternalTagging = Tagging()

Untagged = Tagging(kind=Tagging.Kind.Untagged)


DefaultTagging = ExternalTagging


def ensure(expr: Any, description: str) -> None:
    if not expr:
        raise Exception(description)


def should_impl_dataclass(cls: Type[Any]) -> bool:
    """
    Test if class doesn't have @dataclass.

    `dataclasses.is_dataclass` returns True even Derived class doesn't actually @dataclass.
    >>> @dataclasses.dataclass
    ... class Base:
    ...     a: int
    >>> class Derived(Base):
    ...     b: int
    >>> dataclasses.is_dataclass(Derived)
    True

    This function tells the class actually have @dataclass or not.
    >>> should_impl_dataclass(Base)
    False
    >>> should_impl_dataclass(Derived)
    True
    """
    if not dataclasses.is_dataclass(cls):
        return True

    annotations = getattr(cls, "__annotations__", {})
    if not annotations:
        return False

    field_names = [field.name for field in dataclass_fields(cls)]
    for field_name in annotations:
        if field_name not in field_names:
            return True

    return False


@dataclass
class TypeCheck:
    """
    Specify type check flavors.
    """

    class Kind(enum.Enum):
        Disabled = enum.auto()
        """ No check performed """

        Coerce = enum.auto()
        """ Value is coerced into the declared type """
        Strict = enum.auto()
        """ Value are strictly checked against the declared type """

    kind: Kind

    def is_strict(self) -> bool:
        return self.kind == self.Kind.Strict

    def is_coerce(self) -> bool:
        return self.kind == self.Kind.Coerce

    def __call__(self, **kwargs: Any) -> TypeCheck:
        # TODO
        return self


disabled = TypeCheck(kind=TypeCheck.Kind.Disabled)

coerce = TypeCheck(kind=TypeCheck.Kind.Coerce)

strict = TypeCheck(kind=TypeCheck.Kind.Strict)


def coerce_object(typ: Type[Any], obj: Any) -> Any:
    return typ(obj) if is_coercible(typ, obj) else obj


def is_coercible(typ: Type[Any], obj: Any) -> bool:
    if obj is None:
        return False
    return True


def has_default(field: Field[Any]) -> bool:
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


def has_default_factory(field: Field[Any]) -> bool:
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


class ClassSerializer(Protocol):
    """
    Interface for custom class serializer.

    This protocol is intended to be used for custom class serializer.

    >>> from datetime import datetime
    >>> from serde import serde
    >>> from plum import dispatch
    >>> class MySerializer(ClassSerializer):
    ...     @dispatch
    ...     def serialize(self, value: datetime) -> str:
    ...         return value.strftime("%d/%m/%y")
    """

    def serialize(self, value: Any) -> Any:
        pass


class ClassDeserializer(Protocol):
    """
    Interface for custom class deserializer.

    This protocol is intended to be used for custom class deserializer.

    >>> from datetime import datetime
    >>> from serde import serde
    >>> from plum import dispatch
    >>> class MyDeserializer(ClassDeserializer):
    ...     @dispatch
    ...     def deserialize(self, cls: Type[datetime], value: Any) -> datetime:
    ...         return datetime.strptime(value, "%d/%m/%y")
    """

    def deserialize(self, cls: Any, value: Any) -> Any:
        pass


GLOBAL_CLASS_SERIALIZER: List[ClassSerializer] = []

GLOBAL_CLASS_DESERIALIZER: List[ClassDeserializer] = []


def add_serializer(serializer: ClassSerializer) -> None:
    """
    Register custom global serializer.
    """
    GLOBAL_CLASS_SERIALIZER.append(serializer)


def add_deserializer(deserializer: ClassDeserializer) -> None:
    """
    Register custom global deserializer.
    """
    GLOBAL_CLASS_DESERIALIZER.append(deserializer)
