"""
This module provides `deserialize`, `is_deserializable` `from_dict`, `from_tuple` and classes
and functions associated with deserialization.
"""

from __future__ import annotations
import abc
import itertools
import collections
import dataclasses
import functools
import typing
import jinja2
from collections.abc import Callable, Sequence, Iterable
from beartype import beartype, BeartypeConf
from beartype.door import is_bearable
from beartype.roar import BeartypeCallHintParamViolation
from dataclasses import dataclass, is_dataclass
from typing import overload, TypeVar, Generic, Any, Optional, Union, Literal, Iterator
from typing_extensions import dataclass_transform

from .compat import (
    SerdeError,
    SerdeSkip,
    T,
    UserError,
    find_generic_arg,
    get_args,
    get_generic_arg,
    get_origin,
    get_type_var_names,
    is_any,
    is_bare_dict,
    is_bare_list,
    is_bare_set,
    is_bare_tuple,
    is_datetime,
    is_default_dict,
    is_dict,
    is_ellipsis,
    is_enum,
    is_frozen_set,
    is_generic,
    is_list,
    is_literal,
    is_none,
    is_opt,
    is_primitive,
    is_primitive_subclass,
    is_set,
    is_str_serializable,
    is_tuple,
    is_union,
    is_variable_tuple,
    is_pep695_type_alias,
    iter_literals,
    iter_types,
    iter_unions,
    type_args,
    typename,
)
from .core import (
    GLOBAL_CLASS_DESERIALIZER,
    ClassDeserializer,
    FROM_DICT,
    FROM_ITER,
    SERDE_SCOPE,
    CACHE,
    UNION_DE_PREFIX,
    DefaultTagging,
    Field,
    disabled,
    Scope,
    Tagging,
    TypeCheck,
    add_func,
    coerce_object,
    strict,
    has_default,
    has_default_factory,
    ensure,
    fields,
    is_instance,
    literal_func_name,
    logger,
    raise_unsupported_type,
    union_func_name,
)
from .numpy import (
    deserialize_numpy_array,
    deserialize_numpy_scalar,
    deserialize_numpy_array_direct,
    deserialize_numpy_jaxtyping_array,
    is_numpy_array,
    is_numpy_jaxtyping,
    is_numpy_scalar,
)

__all__ = ["deserialize", "is_deserializable", "from_dict", "from_tuple"]


DeserializeFunc = Callable[[type[Any], Any], Any]
""" Interface of Custom deserialize function. """


def serde_legacy_custom_class_deserializer(
    cls: type[Any], datavar: Any, value: Any, custom: DeserializeFunc, default: Callable[[], Any]
) -> Any:
    """
    Handle custom deserialization. Use default deserialization logic if it receives `SerdeSkip`
    exception.

    :param cls: Type of the field.
    :param datavar: The whole variable to deserialize from. e.g. "data"
    :param value: The value for the field. e.g. "data['i']"
    :param custom: Custom deserialize function.
    :param default: Default deserialize function.
    """
    try:
        return custom(cls, value)
    except SerdeSkip:
        return default()


def default_deserializer(_cls: type[Any], obj: Any) -> Any:
    """
    Marker function to tell serde to use the default deserializer. It's used when custom
    deserializer is specified at the class but you want to override a field with the default
    deserializer.
    """


def _get_by_aliases(
    d: dict[str, str], aliases: list[str], raise_error: bool = True
) -> Optional[str]:
    if not aliases:
        if raise_error:
            raise KeyError("Tried all aliases, but key not found")
        else:
            return None
    if aliases[0] in d:
        return d[aliases[0]]
    else:
        return _get_by_aliases(d, aliases[1:], raise_error=raise_error)


def _exists_by_aliases(d: dict[str, str], aliases: list[str]) -> bool:
    for alias in aliases:
        if alias in d:
            return True
    return False


def _make_deserialize(
    cls_name: str,
    fields: list[Any],
    *args: Any,
    rename_all: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    deserializer: Optional[DeserializeFunc] = None,
    type_check: TypeCheck = strict,
    class_deserializer: Optional[ClassDeserializer] = None,
    **kwargs: Any,
) -> type[Any]:
    """
    Create a deserializable class programatically.
    """
    C: type[Any] = dataclasses.make_dataclass(cls_name, fields, *args, **kwargs)
    C = deserialize(
        C,
        rename_all=rename_all,
        reuse_instances_default=reuse_instances_default,
        convert_sets_default=convert_sets_default,
        **kwargs,
    )
    return C


# The `deserialize` function can call itself recursively when it needs to generate code for
# unmarked dataclasses. To avoid infinite recursion, this array remembers types for which code is
# currently being generated.
GENERATION_STACK = []


@dataclass_transform()
def deserialize(
    _cls: Optional[type[T]] = None,
    rename_all: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    deserializer: Optional[DeserializeFunc] = None,
    tagging: Tagging = DefaultTagging,
    type_check: TypeCheck = strict,
    class_deserializer: Optional[ClassDeserializer] = None,
    deny_unknown_fields: bool = False,
    **kwargs: Any,
) -> type[T]:
    """
    A dataclass with this decorator is deserializable from any of the data formats supported
    by pyserde.

    >>> from serde import deserialize
    >>> from serde.json import from_json
    >>>
    >>> @deserialize
    ... class Foo:
    ...     i: int
    ...     s: str
    ...     f: float
    ...     b: bool
    >>>
    >>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
    Foo(i=10, s='foo', f=100.0, b=True)
    """

    stack = []

    def wrap(cls: type[T]) -> type[T]:
        if cls in stack:
            return cls
        stack.append(cls)

        tagging.check()

        # If no `dataclass` found in the class, dataclassify it automatically.
        if not is_dataclass(cls):
            dataclass(cls)

        if type_check.is_strict():
            serde_beartype = beartype(conf=BeartypeConf(violation_type=SerdeError))
            serde_beartype(cls)

        g: dict[str, Any] = {}

        # Create a scope storage used by serde.
        # Each class should get own scope. Child classes can not share scope with parent class.
        # That's why we need the "scope.cls is not cls" check.
        scope: Optional[Scope] = getattr(cls, SERDE_SCOPE, None)
        if scope is None or scope.cls is not cls:
            scope = Scope(cls, reuse_instances_default=reuse_instances_default)
            setattr(cls, SERDE_SCOPE, scope)

        class_deserializers: list[ClassDeserializer] = list(
            itertools.chain(
                GLOBAL_CLASS_DESERIALIZER, [class_deserializer] if class_deserializer else []
            )
        )

        # Set some globals for all generated functions
        g["cls"] = cls
        g["serde_scope"] = scope
        g["SerdeError"] = SerdeError
        g["UserError"] = UserError
        g["raise_unsupported_type"] = raise_unsupported_type
        g["typename"] = typename
        g["ensure"] = ensure
        g["typing"] = typing
        g["collections"] = collections
        g["Literal"] = Literal
        g["from_obj"] = from_obj
        g["get_generic_arg"] = get_generic_arg
        g["is_instance"] = is_instance
        g["TypeCheck"] = TypeCheck
        g["disabled"] = disabled
        g["coerce_object"] = coerce_object
        g["_exists_by_aliases"] = _exists_by_aliases
        g["_get_by_aliases"] = _get_by_aliases
        g["class_deserializers"] = class_deserializers
        g["BeartypeCallHintParamViolation"] = BeartypeCallHintParamViolation
        g["is_bearable"] = is_bearable
        if deserializer:
            g["serde_legacy_custom_class_deserializer"] = functools.partial(
                serde_legacy_custom_class_deserializer, custom=deserializer
            )

        # Collect types used in the generated code.
        for typ in iter_types(cls):
            # When we encounter a dataclass not marked with deserialize, then also generate
            # deserialize functions for it.
            if is_dataclass_without_de(typ) and typ is not cls:
                # We call deserialize and not wrap to make sure that we will use the default serde
                # configuration for generating the deserialization function.
                deserialize(typ)

            # We don't want to add primitive class e.g "str" into the scope, but primitive
            # compatible types such as IntEnum and a subclass of primitives are added,
            # so that generated code can use those types.
            if is_primitive(typ) and not is_enum(typ) and not is_primitive_subclass(typ):
                continue

            if is_generic(typ):
                g[typename(typ)] = get_origin(typ)
            else:
                g[typename(typ)] = typ

        # render all union functions
        for union in iter_unions(cls):
            union_args = type_args(union)
            add_func(
                scope,
                union_func_name(UNION_DE_PREFIX, union_args),
                render_union_func(cls, union_args, tagging),
                g,
            )

        # render literal functions
        for literal in iter_literals(cls):
            literal_args = type_args(literal)
            add_func(
                scope, literal_func_name(literal_args), render_literal_func(cls, literal_args), g
            )

        # Collect default values and default factories used in the generated code.
        for f in defields(cls):
            assert f.name
            if has_default(f):
                scope.defaults[f.name] = f.default
            elif has_default_factory(f):
                scope.defaults[f.name] = f.default_factory
            if f.deserializer:
                g[f.deserializer.name] = f.deserializer

        add_func(
            scope,
            FROM_ITER,
            render_from_iter(cls, deserializer, type_check, class_deserializer=class_deserializer),
            g,
        )
        add_func(
            scope,
            FROM_DICT,
            render_from_dict(
                cls,
                rename_all,
                deserializer,
                type_check,
                class_deserializer=class_deserializer,
                deny_unknown_fields=deny_unknown_fields,
            ),
            g,
        )

        logger.debug(f"{typename(cls)}: {SERDE_SCOPE} {scope}")

        stack.pop()
        return cls

    if _cls is None:
        return wrap  # type: ignore

    if _cls in GENERATION_STACK:
        return _cls

    GENERATION_STACK.append(_cls)
    try:
        return wrap(_cls)
    finally:
        GENERATION_STACK.pop()


def is_deserializable(instance_or_class: Any) -> bool:
    """
    Test if an instance or class is deserializable.

    >>> @deserialize
    ... class Foo:
    ...     pass
    >>>
    >>> is_deserializable(Foo)
    True
    """
    return hasattr(instance_or_class, SERDE_SCOPE)


def is_dataclass_without_de(cls: type[Any]) -> bool:
    if not dataclasses.is_dataclass(cls):
        return False
    if not hasattr(cls, SERDE_SCOPE):
        return True
    scope: Optional[Scope] = getattr(cls, SERDE_SCOPE)
    if not scope:
        return True
    return FROM_DICT not in scope.funcs


class Deserializer(Generic[T], metaclass=abc.ABCMeta):
    """
    `Deserializer` base class. Subclass this to customize deserialize behaviour.

    See `serde.json.JsonDeserializer` and `serde.msgpack.MsgPackDeserializer` for example usage.
    """

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, data: T, **opts: Any) -> Any:
        """
        deserialize `data` into an object typically `dict`, `list` or `tuple`.

        For example, `serde.json.JsonDeserializer` takes json string and deserialize
        into an object. `serde.msgpack.MsgPackDeserializer` takes msgpack bytes and
        deserialize into an object.
        """
        raise NotImplementedError


def from_obj(c: type[T], o: Any, named: bool, reuse_instances: Optional[bool]) -> T:
    """
    Deserialize from an object into an instance of the type specified as arg `c`.
    `c` can be either primitive type, `list`, `tuple`, `dict` or `deserialize` class.
    """

    res: Any

    # It is possible that the parser already generates the correct data type requested
    # by the caller. Hence, it should be checked early to avoid doing anymore work.
    if type(o) is c:
        return o

    def deserializable_to_obj(cls: type[T]) -> T:
        serde_scope: Scope = getattr(cls, SERDE_SCOPE)
        func_name = FROM_DICT if named else FROM_ITER
        res = serde_scope.funcs[func_name](
            cls, maybe_generic=maybe_generic, data=o, reuse_instances=reuse_instances
        )
        return res  # type: ignore

    if is_union(c) and not is_opt(c):
        # If a class in the argument is a non-dataclass class e.g. Union[Foo, Bar],
        # pyserde generates a wrapper (de)serializable dataclass on the fly,
        # and use it to deserialize into the object.
        return CACHE.deserialize_union(c, o)

    if is_generic(c):
        # Store subscripted generic type such as Foo[Bar] in "maybe_generic",
        # and store origin type such as Foo in "c". Since subscripted generics
        # are not a subclass of "type", use "c" for type inspection, and pass
        # "maybe_generic" in deserialize functions.
        maybe_generic = c
        c = get_origin(c)  # type: ignore
    else:
        maybe_generic = c
    try:
        thisfunc = functools.partial(from_obj, named=named, reuse_instances=reuse_instances)
        if is_dataclass_without_de(c):
            # Do not automatically implement beartype if dataclass without serde decorator
            # is passed, because it is surprising for users
            # See https://github.com/yukinarit/pyserde/issues/480
            deserialize(c, type_check=disabled)
            res = deserializable_to_obj(c)
        elif is_deserializable(c):
            res = deserializable_to_obj(c)
        elif is_opt(c):
            if o is None:
                res = None
            else:
                res = thisfunc(type_args(c)[0], o)
        elif is_list(c):
            if is_bare_list(c):
                res = list(o)
            else:
                res = [thisfunc(type_args(c)[0], e) for e in o]
        elif is_set(c):
            if is_bare_set(c):
                res = set(o)
            elif is_frozen_set(c):
                res = frozenset(thisfunc(type_args(c)[0], e) for e in o)
            else:
                res = {thisfunc(type_args(c)[0], e) for e in o}
        elif is_tuple(c):
            if is_bare_tuple(c) or is_variable_tuple(c):
                res = tuple(e for e in o)
            else:
                res = tuple(thisfunc(type_args(c)[i], e) for i, e in enumerate(o))
        elif is_dict(c):
            if is_bare_dict(c):
                res = o
            elif is_default_dict(c):
                f = DeField(c, "")
                v = f.value_field()
                origin = get_origin(v.type)
                res = collections.defaultdict(
                    origin if origin else v.type,
                    {
                        thisfunc(type_args(c)[0], k): thisfunc(type_args(c)[1], v)
                        for k, v in o.items()
                    },
                )
            else:
                res = {
                    thisfunc(type_args(c)[0], k): thisfunc(type_args(c)[1], v) for k, v in o.items()
                }
        elif is_numpy_array(c):
            res = deserialize_numpy_array_direct(c, o)
        elif is_datetime(c):
            res = c.fromisoformat(o)
        elif is_any(c) or is_ellipsis(c):
            res = o
        else:
            res = c(o)  # type: ignore

        return res  # type: ignore

    except UserError as e:
        raise e.inner from None

    except Exception as e:
        raise SerdeError(e) from None


@overload
def from_dict(cls: type[T], o: dict[str, Any], reuse_instances: Optional[bool] = None) -> T: ...


@overload
def from_dict(cls: Any, o: dict[str, Any], reuse_instances: Optional[bool] = None) -> Any: ...


def from_dict(cls: Any, o: dict[str, Any], reuse_instances: Optional[bool] = None) -> Any:
    """
    Deserialize dictionary into object.

    >>> @deserialize
    ... class Foo:
    ...     i: int
    ...     s: str = 'foo'
    ...     f: float = 100.0
    ...     b: bool = True
    >>>
    >>> from_dict(Foo, {'i': 10, 's': 'foo', 'f': 100.0, 'b': True})
    Foo(i=10, s='foo', f=100.0, b=True)

    You can pass any type supported by pyserde. For example,

    >>> lst = [{'i': 10, 's': 'foo', 'f': 100.0, 'b': True},
    ...        {'i': 20, 's': 'foo', 'f': 100.0, 'b': True}]
    >>> from_dict(list[Foo], lst)
    [Foo(i=10, s='foo', f=100.0, b=True), Foo(i=20, s='foo', f=100.0, b=True)]
    """
    return from_obj(cls, o, named=True, reuse_instances=reuse_instances)


@overload
def from_tuple(cls: type[T], o: Any, reuse_instances: Optional[bool] = None) -> T: ...


@overload
def from_tuple(cls: Any, o: Any, reuse_instances: Optional[bool] = None) -> Any: ...


def from_tuple(cls: Any, o: Any, reuse_instances: Optional[bool] = None) -> Any:
    """
    Deserialize tuple into object.

    >>> @deserialize
    ... class Foo:
    ...     i: int
    ...     s: str = 'foo'
    ...     f: float = 100.0
    ...     b: bool = True
    >>>
    >>> from_tuple(Foo, (10, 'foo', 100.0, True))
    Foo(i=10, s='foo', f=100.0, b=True)

    You can pass any type supported by pyserde. For example,

    >>> lst = [(10, 'foo', 100.0, True), (20, 'foo', 100.0, True)]
    >>> from_tuple(list[Foo], lst)
    [Foo(i=10, s='foo', f=100.0, b=True), Foo(i=20, s='foo', f=100.0, b=True)]
    """
    return from_obj(cls, o, named=False, reuse_instances=reuse_instances)


@dataclass
class DeField(Field[T]):
    """
    Represents a field of dataclass.
    """

    datavar: Optional[str] = None
    """ Name of variable which is passed in the deserialize API """

    index: int = 0
    """ Field index """

    iterbased: bool = False
    """ Iterater based deserializer or not """

    def __getitem__(self, n: int) -> Union[DeField[Any], InnerField[Any]]:
        """
        Get inner `Field` from current `Field`.

        `InnerField` is returned if self is of any standard collection e.g. list.
        `DeField` is returned if self is Optional.
        """
        typ = type_args(self.type)[n]
        opts: dict[str, Any] = {
            "kw_only": self.kw_only,
            "case": self.case,
            "alias": self.alias,
            "rename": self.rename,
            "skip": self.skip,
            "skip_if": self.skip_if,
            "skip_if_false": self.skip_if_false,
            "skip_if_default": self.skip_if_default,
            "serializer": self.serializer,
            "deserializer": self.deserializer,
            "flatten": self.flatten,
            "parent": self.parent,
        }
        if is_list(self.type) or is_dict(self.type) or is_set(self.type):
            return InnerField(typ, "v", datavar="v", **opts)
        elif is_tuple(self.type):
            return InnerField(typ, f"{self.data}[{n}]", datavar=f"{self.data}[{n}]", **opts)
        else:
            # For Optional etc.
            return DeField(
                typ,
                self.name,
                datavar=self.datavar,
                index=self.index,
                iterbased=self.iterbased,
                **opts,
            )

    def key_field(self) -> DeField[Any]:
        """
        Get inner key field for dict like class.
        """
        k = self[0]
        k.name = "k"
        k.datavar = "k"
        return k

    def value_field(self) -> DeField[Any]:
        """
        Get inner value field for dict like class.
        """
        return self[1]

    @property
    def data(self) -> str:
        """
        Renders the variable name that possesses the data.

        e.g. tuple
            * datavar property returns "data"
            * data property returns "data[0]".
        e.g. Optional
            * datavar property returns "data"
            * data property returns "data.get("field_name")".
        For other types
            * datavar property returns "data"
            * data property returns "data["field_name"]".
        """

        if self.iterbased:
            return f"{self.datavar}[{self.index}]"
        elif is_union(self.type) and type(None) in get_args(self.type):
            return f'{self.datavar}.get("{self.conv_name()}")'
        else:
            return f'{self.datavar}["{self.conv_name()}"]'

    @data.setter
    def data(self, d: str) -> None:
        self.datavar = d

    def data_or(self) -> str:
        if self.iterbased:
            return self.data
        else:
            return f'{self.datavar}.get("{self.conv_name()}")'


@dataclass
class InnerField(DeField[T]):
    """
    Field of Inner type. The purpose of this class is to override "data" method
    for inner type codegen.

    e.g.
      T of list[T]
      V of dict[K, V]
      T of Optional[T]
    """

    @property
    def data(self) -> str:
        return self.datavar or ""

    @data.setter
    def data(self, d: str) -> None:
        self.datavar = d


def defields(cls: type[Any]) -> list[DeField[Any]]:
    return fields(DeField, cls)


@dataclass
class Renderer:
    """
    Render rvalue for code generation.
    """

    func: str
    cls: Optional[type[Any]] = None
    legacy_class_deserializer: Optional[DeserializeFunc] = None
    import_numpy: bool = False
    suppress_coerce: bool = False
    """ Disable type coercing in codegen """
    class_deserializer: Optional[ClassDeserializer] = None
    class_name: Optional[str] = None

    def render(self, arg: DeField[Any]) -> str:
        """
        Render rvalue
        """
        implemented_methods: dict[type[Any], int] = {}
        class_deserializers: Iterable[ClassDeserializer] = itertools.chain(
            GLOBAL_CLASS_DESERIALIZER, [self.class_deserializer] if self.class_deserializer else []
        )
        for n, class_deserializer in enumerate(class_deserializers):
            for method in class_deserializer.__class__.deserialize.methods:  # type: ignore
                implemented_methods[get_args(method.signature.types[1])[0]] = n

        custom_deserializer_available = arg.type in implemented_methods
        if custom_deserializer_available and not arg.deserializer:
            res = (
                f"class_deserializers[{implemented_methods[arg.type]}].deserialize("
                f"{typename(arg.type)}, {arg.data})"
            )
        elif arg.deserializer and arg.deserializer.inner is not default_deserializer:
            res = self.custom_field_deserializer(arg)
        elif is_generic(arg.type):
            arg.type_args = list(get_args(arg.type))
            origin = get_origin(arg.type)
            assert origin
            arg.type = origin
            res = self.render(arg)
        elif is_dataclass(arg.type):
            res = self.dataclass(arg)
        elif is_opt(arg.type):
            res = self.opt(arg)
        elif is_list(arg.type):
            res = self.list(arg)
        elif is_set(arg.type):
            res = self.set(arg)
        elif is_dict(arg.type):
            res = self.dict(arg)
        elif is_tuple(arg.type):
            res = self.tuple(arg)
        elif is_enum(arg.type):
            res = self.enum(arg)
        elif is_numpy_scalar(arg.type):
            self.import_numpy = True
            res = deserialize_numpy_scalar(arg)
        elif is_numpy_array(arg.type):
            self.import_numpy = True
            res = deserialize_numpy_array(arg)
        elif is_numpy_jaxtyping(arg.type):
            self.import_numpy = True
            res = deserialize_numpy_jaxtyping_array(arg)
        elif is_union(arg.type):
            res = self.union_func(arg)
        elif is_str_serializable(arg.type):
            res = f"({self.c_tor_with_check(arg)}) if reuse_instances else {self.c_tor(arg)}"
        elif is_datetime(arg.type):
            from_iso = f"{typename(arg.type)}.fromisoformat({arg.data})"
            res = f"({arg.data} if isinstance({arg.data}, {typename(arg.type)}) else {from_iso}) \
                    if reuse_instances else {from_iso}"
        elif is_none(arg.type):
            res = "None"
        elif is_any(arg.type) or is_ellipsis(arg.type):
            res = arg.data
        elif is_pep695_type_alias(arg.type):
            res = self.render(DeField(name=arg.name, type=arg.type.__value__, datavar=arg.datavar))
        elif is_primitive(arg.type):
            # For subclasses for primitives e.g. class FooStr(str), coercing is always enabled
            res = self.primitive(arg, not is_primitive_subclass(arg.type))
        elif isinstance(arg.type, TypeVar):
            if not self.cls:
                raise SerdeError("Missing cls")
            index = find_generic_arg(self.cls, arg.type)
            res = (
                f"from_obj(get_generic_arg(maybe_generic, maybe_generic_type_vars, "
                f"variable_type_args, {index}), {arg.data}, named={not arg.iterbased}, "
                "reuse_instances=reuse_instances)"
            )
        elif is_literal(arg.type):
            res = self.literal(arg)
        else:
            return f"raise_unsupported_type({arg.data})"

        if arg.supports_default():
            res = self.default(arg, res)

        if (
            self.legacy_class_deserializer
            and not arg.deserializer
            and not custom_deserializer_available
        ):
            # Rerender the code for default deserializer.
            default = Renderer(
                self.func, self.cls, None, suppress_coerce=self.suppress_coerce
            ).render(arg)
            return self.custom_class_deserializer(arg, default)
        else:
            return res

    def custom_field_deserializer(self, arg: DeField[Any]) -> str:
        """
        Render rvalue for the field with custom deserializer.
        """
        if not arg.deserializer:
            raise SerdeError("Missing custom field deserializer")
        return f"{arg.deserializer.name}({arg.data})"

    def custom_class_deserializer(self, arg: DeField[Any], code: str) -> str:
        """
        Render custom class deserializer.
        """
        # The function takes a closure in order to execute the default value lazily.
        return (
            "serde_legacy_custom_class_deserializer("
            f"{typename(arg.type)}, "
            f"{arg.datavar}, "
            f"{arg.data_or()}, "
            f"default=lambda: {code})"
        )

    def dataclass(self, arg: DeField[Any]) -> str:
        if not arg.flatten:
            # e.g. "data['field']" will be used as variable name.
            var = arg.data
        else:
            # Because the field is flattened
            # e.g. "data" will be used as variable name.
            assert arg.datavar
            if arg.iterbased:
                var = f"{arg.datavar}[{arg.index}:]"
            else:
                var = arg.datavar

        type_args_str = [str(t).lstrip("~") for t in arg.type_args] if arg.type_args else None

        opts = (
            "maybe_generic=maybe_generic, maybe_generic_type_vars=maybe_generic_type_vars, "
            f"variable_type_args={type_args_str}, reuse_instances=reuse_instances"
        )

        if arg.is_self_referencing():
            class_name = "cls"
        else:
            class_name = typename(arg.type)

        return f"{class_name}.{SERDE_SCOPE}.funcs['{self.func}'](data={var}, {opts})"

    def opt(self, arg: DeField[Any]) -> str:
        """
        Render rvalue for Optional.
        """
        inner = arg[0]
        if arg.iterbased:
            exists = f"{arg.data} is not None"
        elif arg.flatten:
            # Check nullabilities of all nested fields.
            exists = " and ".join(
                [
                    f'{arg.datavar}.get("{f.name}") is not None'
                    for f in dataclasses.fields(inner.type)
                ]
            )
        else:
            name = arg.conv_name()
            if arg.alias:
                aliases = (f'"{s}"' for s in [name, *arg.alias])
                get = f"_get_by_aliases(data, [{','.join(aliases)}], raise_error=False)"
            else:
                get = f'{arg.datavar}.get("{name}")'
            exists = f"{get} is not None"
        return f"({self.render(inner)}) if {exists} else None"

    def list(self, arg: DeField[Any]) -> str:
        """
        Render rvalue for list.
        """
        if is_bare_list(arg.type):
            return f"list({arg.data})"
        else:
            return f"[{self.render(arg[0])} for v in {arg.data}]"

    def set(self, arg: DeField[Any]) -> str:
        """
        Render rvalue for set.
        """
        if is_bare_set(arg.type):
            return f"set({arg.data})"
        elif is_frozen_set(arg.type):
            return f"frozenset({self.render(arg[0])} for v in {arg.data})"
        else:
            return f"set({self.render(arg[0])} for v in {arg.data})"

    def tuple(self, arg: DeField[Any]) -> str:
        """
        Render rvalue for tuple.
        """
        if is_bare_tuple(arg.type):
            return f"tuple({arg.data})"
        elif is_variable_tuple(arg.type):
            earg = arg[0]
            earg.datavar = "v"
            return f"tuple({self.render(earg)} for v in {arg.data})"
        else:
            values = []
            for i, _typ in enumerate(type_args(arg.type)):
                inner = arg[i]
                values.append(self.render(inner))
            return f'({", ".join(values)},)'  # trailing , is required for single element tuples

    def dict(self, arg: DeField[Any]) -> str:
        """
        Render rvalue for dict.
        """
        if is_bare_dict(arg.type):
            return arg.data
        elif is_default_dict(arg.type):
            k = arg.key_field()
            v = arg.value_field()
            origin = get_origin(v.type)
            if origin:
                # When the callable type is of generic type e.g list.
                # Get origin type "list" from "list[X]".
                callable = origin.__name__
            else:
                # When the callable type is non generic type e.g int, Foo.
                callable = v.type.__name__
            return f"collections.defaultdict({callable}, \
                    {{{self.render(k)}: {self.render(v)} for k, v in {arg.data}.items()}})"
        else:
            k = arg.key_field()
            v = arg.value_field()
            return f"{{{self.render(k)}: {self.render(v)} for k, v in {arg.data}.items()}}"

    def enum(self, arg: DeField[Any]) -> str:
        return f"{typename(arg.type)}({self.primitive(arg)})"

    def primitive(self, arg: DeField[Any], suppress_coerce: bool = False) -> str:
        """
        Render rvalue for primitives.

        * `suppress_coerce`: Overrides "suppress_coerce" in the Renderer's field
        """
        typ = typename(arg.type)
        dat = arg.data
        if arg.alias:
            aliases = (f'"{s}"' for s in [arg.name, *arg.alias])
            dat = f"_get_by_aliases(data, [{','.join(aliases)}])"
        if self.suppress_coerce and suppress_coerce:
            return dat
        else:
            assert arg.name
            escaped_arg_name = arg.name.replace('"', '\\"')
            return f'coerce_object("{self.class_name}", "{escaped_arg_name}", {typ}, {dat})'

    def c_tor(self, arg: DeField[Any]) -> str:
        return f"{typename(arg.type)}({arg.data})"

    def c_tor_with_check(self, arg: DeField[Any], ctor: Optional[str] = None) -> str:
        if ctor is None:
            ctor = self.c_tor(arg)
        return f"{arg.data} if isinstance({arg.data}, {typename(arg.type)}) else {ctor}"

    def union_func(self, arg: DeField[Any]) -> str:
        func_name = union_func_name(UNION_DE_PREFIX, type_args(arg.type))
        return (
            f"serde_scope.funcs['{func_name}']("
            "cls=cls, "
            f"data={arg.data}, "
            "reuse_instances=reuse_instances)"
        )

    def literal(self, arg: DeField[Any]) -> str:
        func_name = literal_func_name(type_args(arg.type))
        return (
            f"serde_scope.funcs['{func_name}']("
            "cls=cls, "
            f"data={arg.data}, "
            "reuse_instances=reuse_instances)"
        )

    def default(self, arg: DeField[Any], code: str) -> str:
        """
        Renders supplying default value during deserialization.
        """

        def get_aliased_fields(arg: Field[Any]) -> Iterator[str]:
            return (f'"{s}"' for s in [arg.name, *arg.alias])

        if arg.flatten:
            # When a field has the `flatten` attribute, iterate over its dataclass fields.
            # This ensures that the code checks keys in the data while considering aliases.
            flattened = []
            for subarg in defields(arg.type):
                if subarg.alias:
                    aliases = get_aliased_fields(subarg)
                    flattened.append(f'_exists_by_aliases({arg.datavar}, [{",".join(aliases)}])')
                else:
                    flattened.append(f'"{subarg.name}" in {arg.datavar}')
            exists = " and ".join(flattened)
        else:
            if arg.alias:
                aliases = get_aliased_fields(arg)
                exists = f'_exists_by_aliases({arg.datavar}, [{",".join(aliases)}])'
            else:
                exists = f'"{arg.conv_name()}" in {arg.datavar}'

        if has_default(arg):
            return f'({code}) if {exists} else serde_scope.defaults["{arg.name}"]'
        elif has_default_factory(arg):
            return f'({code}) if {exists} else serde_scope.defaults["{arg.name}"]()'
        else:
            return code


def to_arg(f: DeField[T], index: int, rename_all: Optional[str] = None) -> DeField[T]:
    f.index = index
    f.data = "data"
    f.case = f.case or rename_all
    return f


def to_iter_arg(f: DeField[T], *args: Any, **kwargs: Any) -> DeField[T]:
    f = to_arg(f, *args, **kwargs)
    f.iterbased = True
    return f


def renderable(f: DeField[Any]) -> bool:
    return f.init


jinja2_env = jinja2.Environment(
    loader=jinja2.DictLoader(
        {
            "iter": """
def {{func}}(cls=cls, maybe_generic=None, maybe_generic_type_vars=None, data=None,
             variable_type_args=None, reuse_instances=None):
  if reuse_instances is None:
    reuse_instances = {{serde_scope.reuse_instances_default}}

  maybe_generic_type_vars = maybe_generic_type_vars or {{cls_type_vars}}

  {% for f in fields %}
  __{{f.name}} = {{rvalue(arg(f,loop.index-1))}}
  {% endfor %}

  try:
    return cls(
      {% for f in fields %}
      __{{f.name}},
      {% endfor %}
    )
  except BeartypeCallHintParamViolation as e:
    raise SerdeError(e)
  except Exception as e:
    raise UserError(e)
""",
            "dict": """
def {{func}}(cls=cls, maybe_generic=None, maybe_generic_type_vars=None, data=None,
             variable_type_args=None, reuse_instances=None):
  if reuse_instances is None:
    reuse_instances = {{serde_scope.reuse_instances_default}}

  {% if deny_unknown_fields %}
  known_fields = {{ known_fields }}
  unknown_fields = set((data or {}).keys()) - known_fields
  if unknown_fields:
    raise SerdeError(f'unknown fields: {unknown_fields}, expected one of {known_fields}')
  {% endif %}

  maybe_generic_type_vars = maybe_generic_type_vars or {{cls_type_vars}}

  {% for f in fields %}
  __{{f.name}} = {{rvalue(arg(f,loop.index-1))}}
  {% endfor %}

  try:
    return cls(
    {% for f in fields %}
    {% if f.kw_only %}
    {{f.name}}=__{{f.name}},
    {% else %}
    __{{f.name}},
    {% endif %}
    {% endfor %}
    )
  except BeartypeCallHintParamViolation as e:
    raise SerdeError(e)
  except Exception as e:
    raise UserError(e)
""",
            "union": """
def {{func}}(cls=cls, maybe_generic=None, maybe_generic_type_vars=None, data=None,
             variable_type_args=None, reuse_instances = {{serde_scope.reuse_instances_default}}):
  errors = []
  {% for t in union_args %}
  try:
    # create fake dict so we can reuse the normal render function
    {% if tagging.is_external() and is_taggable(t)  %}
    ensure("{{typename(t)}}" in data , "'{{typename(t)}}' key is not present")
    fake_dict = {"fake_key": data["{{typename(t)}}"]}

    {% elif tagging.is_internal() and is_taggable(t) %}
    ensure("{{tagging.tag}}" in data , "'{{tagging.tag}}' key is not present")
    ensure("{{typename(t)}}" == data["{{tagging.tag}}"], "tag '{{typename(t)}}' isn't found")
    fake_dict = {"fake_key": data}

    {% elif tagging.is_adjacent() and is_taggable(t) %}
    ensure("{{tagging.tag}}" in data , "'{{tagging.tag}}' key is not present")
    ensure("{{tagging.content}}" in data , "'{{tagging.content}}' key is not present")
    ensure("{{typename(t)}}" == data["{{tagging.tag}}"], "tag '{{typename(t)}}' isn't found")
    fake_dict = {"fake_key": data["{{tagging.content}}"]}

    {% else %}
    fake_dict = {"fake_key": data}
    {% endif %}

    {% if is_primitive(t) or is_none(t) %}
    if not isinstance(fake_dict["fake_key"], {{typename(t)}}):
        raise Exception("Not a type of {{typename(t)}}")
    {% endif %}
    res = {{rvalue(arg(t))}}
    ensure(is_bearable(res, {{typename(t)}}), "object is not of type '{{typename(t)}}'")
    return res
  except Exception as e:
    errors.append(f" Failed to deserialize into {{typename(t)}}: {e}")
  {% endfor %}
  raise SerdeError("Can not deserialize " + repr(data) + " of type " + \
          typename(type(data)) + " into {{union_name}}.\\nReasons:\\n" + "\\n".join(errors))
""",
            "literal": """
def {{func}}(cls=cls, maybe_generic=None, maybe_generic_type_vars=None, data=None,
             variable_type_args=None, reuse_instances = {{serde_scope.reuse_instances_default}}):
  if data in ({%- for v in literal_args -%}{{repr(v)}},{%- endfor -%}):
    return data
  raise SerdeError("Can not deserialize " + repr(data) + " as {{literal_name}}.")
  """,
        }
    )
)


def render_from_iter(
    cls: type[Any],
    legacy_class_deserializer: Optional[DeserializeFunc] = None,
    type_check: TypeCheck = strict,
    class_deserializer: Optional[ClassDeserializer] = None,
) -> str:
    renderer = Renderer(
        FROM_ITER,
        cls=cls,
        legacy_class_deserializer=legacy_class_deserializer,
        suppress_coerce=(not type_check.is_coerce()),
        class_deserializer=class_deserializer,
        class_name=typename(cls),
    )
    fields = list(filter(renderable, defields(cls)))
    res = jinja2_env.get_template("iter").render(
        func=FROM_ITER,
        serde_scope=getattr(cls, SERDE_SCOPE),
        fields=fields,
        cls_type_vars=get_type_var_names(cls),
        rvalue=renderer.render,
        arg=to_iter_arg,
    )

    if renderer.import_numpy:
        res = "import numpy\n" + res

    return res


def get_known_fields(f: DeField[Any], rename_all: Optional[str]) -> list[str]:
    names: list[str] = [f.conv_name(rename_all)]
    return names + f.alias


def render_from_dict(
    cls: type[Any],
    rename_all: Optional[str] = None,
    legacy_class_deserializer: Optional[DeserializeFunc] = None,
    type_check: TypeCheck = strict,
    class_deserializer: Optional[ClassDeserializer] = None,
    deny_unknown_fields: bool = False,
) -> str:
    renderer = Renderer(
        FROM_DICT,
        cls=cls,
        legacy_class_deserializer=legacy_class_deserializer,
        suppress_coerce=(not type_check.is_coerce()),
        class_deserializer=class_deserializer,
        class_name=typename(cls),
    )
    fields = list(filter(renderable, defields(cls)))
    known_fields = set(
        itertools.chain.from_iterable([get_known_fields(f, rename_all) for f in fields])
    )
    res = jinja2_env.get_template("dict").render(
        func=FROM_DICT,
        serde_scope=getattr(cls, SERDE_SCOPE),
        fields=fields,
        type_check=type_check,
        cls_type_vars=get_type_var_names(cls),
        rvalue=renderer.render,
        arg=functools.partial(to_arg, rename_all=rename_all),
        deny_unknown_fields=deny_unknown_fields,
        known_fields=known_fields,
    )

    if renderer.import_numpy:
        res = "import numpy\n" + res

    return res


def render_union_func(
    cls: type[Any], union_args: Sequence[type[Any]], tagging: Tagging = DefaultTagging
) -> str:
    union_name = f"Union[{', '.join([typename(a) for a in union_args])}]"

    renderer = Renderer(FROM_DICT, cls=cls, suppress_coerce=True)
    return jinja2_env.get_template("union").render(
        func=union_func_name(UNION_DE_PREFIX, union_args),
        serde_scope=getattr(cls, SERDE_SCOPE),
        union_args=union_args,
        union_name=union_name,
        tagging=tagging,
        is_taggable=Tagging.is_taggable,
        arg=lambda x: DeField(x, datavar="fake_dict", name="fake_key"),
        rvalue=renderer.render,
        is_primitive=is_primitive,
        is_none=is_none,
        typename=typename,
    )


def render_literal_func(
    cls: type[Any], literal_args: Sequence[Any], tagging: Tagging = DefaultTagging
) -> str:
    literal_name = f"Literal[{', '.join([repr(a) for a in literal_args])}]"
    return jinja2_env.get_template("literal").render(
        func=literal_func_name(literal_args),
        serde_scope=getattr(cls, SERDE_SCOPE),
        literal_args=literal_args,
        literal_name=literal_name,
        tagging=tagging,
        is_taggable=Tagging.is_taggable,
        repr=repr,
        type=type,
    )
