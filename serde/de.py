"""
This module provides `deserialize`, `is_deserializable` `from_dict`, `from_tuple` and classes and functions
associated with deserialization.
"""

import abc
import collections
import dataclasses
import functools
import typing
from dataclasses import dataclass, is_dataclass
from typing import Any, Callable, Dict, List, Optional, TypeVar

import jinja2
from typing_extensions import Type, dataclass_transform

from .compat import (
    Literal,
    SerdeError,
    SerdeSkip,
    UserError,
    find_generic_arg,
    get_args,
    get_generic_arg,
    get_origin,
    has_default,
    has_default_factory,
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
    is_set,
    is_str_serializable,
    is_tuple,
    is_union,
    is_variable_tuple,
    iter_literals,
    iter_types,
    iter_unions,
    type_args,
    typename,
)
from .core import (
    FROM_DICT,
    FROM_ITER,
    SERDE_SCOPE,
    TYPE_CHECK,
    UNION_DE_PREFIX,
    DefaultTagging,
    Field,
    NoCheck,
    SerdeScope,
    Tagging,
    TypeCheck,
    add_func,
    coerce,
    ensure,
    fields,
    is_instance,
    literal_func_name,
    logger,
    raise_unsupported_type,
    render_type_check,
    union_func_name,
)
from .numpy import (
    deserialize_numpy_array,
    deserialize_numpy_array_direct,
    deserialize_numpy_scalar,
    is_numpy_array,
    is_numpy_scalar,
)

__all__ = ['deserialize', 'is_deserializable', 'from_dict', 'from_tuple']

# Interface of Custom deserialize function.
DeserializeFunc = Callable[[Type, Any], Any]


def serde_custom_class_deserializer(cls: Type, datavar, value, custom: DeserializeFunc, default: Callable):
    """
    Handle custom deserialization. Use default deserialization logic if it receives `SerdeSkip` exception.

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


def default_deserializer(_cls: Type, obj):
    """
    Marker function to tell serde to use the default deserializer. It's used when custom deserializer is specified
    at the class but you want to override a field with the default deserializer.
    """


def _get_by_aliases(d: Dict[str, str], aliases: List[str]):
    if not aliases:
        raise KeyError("Tried all aliases, but key not found")
    if aliases[0] in d:
        return d[aliases[0]]
    else:
        return _get_by_aliases(d, aliases[1:])


def _make_deserialize(
    cls_name: str,
    fields,
    *args,
    rename_all: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    serializer: Optional[DeserializeFunc] = None,
    **kwargs,
):
    """
    Create a deserializable class programatically.
    """
    C = dataclasses.make_dataclass(cls_name, fields, *args, **kwargs)
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
    _cls=None,
    rename_all: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    deserializer: Optional[DeserializeFunc] = None,
    tagging: Tagging = DefaultTagging,
    type_check: TypeCheck = NoCheck,
    **kwargs,
):
    """
    A dataclass with this decorator is deserializable from any of the data formats supported by pyserde.

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

    #### Class Attributes

    Class attributes can be specified as arguments in the `deserialize` decorator in order to customize the
    deserialization behaviour of the class entirely.

    * `rename_all` attribute converts field names into the specified string case.
    The following example converts camel-case field names into snake-case names.

    >>> @deserialize(rename_all = 'camelcase')
    ... class Foo:
    ...     int_field: int
    ...     str_field: str
    >>>
    >>> from_json(Foo, '{"intField": 10, "strField": "foo"}')
    Foo(int_field=10, str_field='foo')

    * `deserializer` takes a custom class-level deserialize function. The function applies to the all the fields
    in the class.

    >>> from datetime import datetime
    >>> def deserializer(cls, o):
    ...     if cls is datetime:
    ...         return datetime.strptime(o, '%d/%m/%y')
    ...     else:
    ...         raise SerdeSkip()

    The first argument `cls` is a class of the field and the second argument `o` is value to deserialize from.
    `deserializer` function will be called for every field. If you don't want to use the custom deserializer
    for a certain field, raise `serde.SerdeSkip` exception, pyserde will use the default deserializer for that field.

    >>> @deserialize(deserializer=deserializer)
    ... class Foo:
    ...     i: int
    ...     dt: datetime

    This custom deserializer deserializes `datetime` the string in `MM/DD/YY` format into datetime object.

    >>> from_json(Foo, '{"i": 10, "dt": "01/01/21"}')
    Foo(i=10, dt=datetime.datetime(2021, 1, 1, 0, 0))
    """

    stack = []

    def wrap(cls: Type):
        if cls in stack:
            return
        stack.append(cls)

        tagging.check()

        # If no `dataclass` found in the class, dataclassify it automatically.
        if not is_dataclass(cls):
            dataclass(cls)

        g: Dict[str, Any] = {}

        # Create a scope storage used by serde.
        # Each class should get own scope. Child classes can not share scope with parent class.
        # That's why we need the "scope.cls is not cls" check.
        scope: Optional[SerdeScope] = getattr(cls, SERDE_SCOPE, None)
        if scope is None or scope.cls is not cls:
            scope = SerdeScope(cls, reuse_instances_default=reuse_instances_default)
            setattr(cls, SERDE_SCOPE, scope)

        # Set some globals for all generated functions
        g['cls'] = cls
        g['serde_scope'] = scope
        g['SerdeError'] = SerdeError
        g['UserError'] = UserError
        g['raise_unsupported_type'] = raise_unsupported_type
        g['typename'] = typename  # used in union functions
        g['ensure'] = ensure
        g['typing'] = typing
        g['collections'] = collections
        g['Literal'] = Literal
        g['from_obj'] = from_obj
        g['get_generic_arg'] = get_generic_arg
        g['is_instance'] = is_instance
        g['TypeCheck'] = TypeCheck
        g['NoCheck'] = NoCheck
        g['coerce'] = coerce
        g['_get_by_aliases'] = _get_by_aliases
        if deserialize:
            g['serde_custom_class_deserializer'] = functools.partial(
                serde_custom_class_deserializer, custom=deserializer
            )

        # Collect types used in the generated code.
        for typ in iter_types(cls):
            # When we encounter a dataclass not marked with deserialize, then also generate
            # deserialize functions for it.
            if is_dataclass_without_de(typ):
                # We call deserialize and not wrap to make sure that we will use the default serde
                # configuration for generating the deserialization function.
                deserialize(typ)
            if typ is cls or (is_primitive(typ) and not is_enum(typ)):
                continue
            if is_generic(typ):
                g[typename(typ)] = get_origin(typ)
            else:
                g[typename(typ)] = typ

        # render all union functions
        for union in iter_unions(cls):
            union_args = type_args(union)
            add_func(
                scope, union_func_name(UNION_DE_PREFIX, union_args), render_union_func(cls, union_args, tagging), g
            )

        # render literal functions
        for literal in iter_literals(cls):
            literal_args = type_args(literal)
            add_func(scope, literal_func_name(literal_args), render_literal_func(cls, literal_args), g)

        # Collect default values and default factories used in the generated code.
        for f in defields(cls):
            assert f.name
            if has_default(f):
                scope.defaults[f.name] = f.default
            elif has_default_factory(f):
                scope.defaults[f.name] = f.default_factory
            if f.deserializer:
                g[f.deserializer.name] = f.deserializer

        add_func(scope, FROM_ITER, render_from_iter(cls, deserializer, type_check), g)
        add_func(scope, FROM_DICT, render_from_dict(cls, rename_all, deserializer, type_check), g)
        add_func(scope, TYPE_CHECK, render_type_check(cls), g)

        logger.debug(f'{typename(cls)}: {SERDE_SCOPE} {scope}')

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


def is_dataclass_without_de(cls: Type[Any]) -> bool:
    if not dataclasses.is_dataclass(cls):
        return False
    if not hasattr(cls, SERDE_SCOPE):
        return True
    scope: Optional[SerdeScope] = getattr(cls, SERDE_SCOPE)
    return FROM_DICT not in scope.funcs


class Deserializer(metaclass=abc.ABCMeta):
    """
    `Deserializer` base class. Subclass this to customize deserialize behaviour.

    See `serde.json.JsonDeserializer` and `serde.msgpack.MsgPackDeserializer` for example usage.
    """

    @abc.abstractclassmethod
    def deserialize(cls, data, **opts):
        """
        deserialize `data` into an object typically `dict`, `list` or `tuple`.

        For example, `serde.json.JsonDeserializer` takes json string and deserialize
        into an object. `serde.msgpack.MsgPackDeserializer` takes msgpack bytes and
        deserialize into an object.
        """
        raise NotImplementedError


def from_obj(c: Type, o: Any, named: bool, reuse_instances: bool):
    """
    Deserialize from an object into an instance of the type specified as arg `c`.
    `c` can be either primitive type, `List`, `Tuple`, `Dict` or `deserialize` class.
    """

    def deserializable_to_obj(cls):
        serde_scope: SerdeScope = getattr(cls, SERDE_SCOPE)
        func_name = FROM_DICT if named else FROM_ITER
        res = serde_scope.funcs[func_name](cls, maybe_generic=maybe_generic, data=o, reuse_instances=reuse_instances)
        return res

    if is_generic(c):
        # Store subscripted generic type such as Foo[Bar] in "maybe_generic",
        # and store origin type such as Foo in "c". Since subscripted generics
        # are not a subclass of "type", use "c" for type inspection, and pass
        # "maybe_generic" in deserialize functions.
        maybe_generic = c
        c = get_origin(c)
    else:
        maybe_generic = c
    try:
        thisfunc = functools.partial(from_obj, named=named, reuse_instances=reuse_instances)
        if o is None:
            return None
        if is_dataclass_without_de(c):
            deserialize(c)
            return deserializable_to_obj(c)
        elif is_deserializable(c):
            return deserializable_to_obj(c)
        elif is_opt(c):
            if o is None:
                return None
            else:
                return thisfunc(type_args(c)[0], o)
        elif is_union(c):
            v = None
            for typ in type_args(c):
                try:
                    v = thisfunc(typ, o)
                    break
                except (SerdeError, ValueError):
                    pass
            return v
        elif is_list(c):
            if is_bare_list(c):
                return [e for e in o]
            else:
                res = [thisfunc(type_args(c)[0], e) for e in o]
                return res
        elif is_set(c):
            if is_bare_set(c):
                return set(e for e in o)
            elif is_frozen_set(c):
                res = frozenset(thisfunc(type_args(c)[0], e) for e in o)
                return res
            else:
                res = set(thisfunc(type_args(c)[0], e) for e in o)
                return res
        elif is_tuple(c):
            if is_bare_tuple(c) or is_variable_tuple(c):
                return tuple(e for e in o)
            else:
                res = tuple(thisfunc(type_args(c)[i], e) for i, e in enumerate(o))
                return res
        elif is_dict(c):
            if is_bare_dict(c):
                return {k: v for k, v in o.items()}
            elif is_default_dict(c):
                f = DeField(c, "")
                v = f.value_field()
                origin = get_origin(v.type)
                res = collections.defaultdict(
                    origin if origin else v.type,
                    {thisfunc(type_args(c)[0], k): thisfunc(type_args(c)[1], v) for k, v in o.items()},
                )
            else:
                res = {thisfunc(type_args(c)[0], k): thisfunc(type_args(c)[1], v) for k, v in o.items()}
            return res
        elif is_numpy_array(c):
            return deserialize_numpy_array_direct(c, o)
        elif is_datetime(c):
            return c.fromisoformat(o)
        elif is_any(c) or is_ellipsis(c):
            return o

        return c(o)

    except UserError as e:
        raise e.inner

    except Exception as e:
        raise SerdeError(e)


def from_dict(cls, o, reuse_instances: bool = ...):
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

    >>> lst = [{'i': 10, 's': 'foo', 'f': 100.0, 'b': True}, {'i': 20, 's': 'foo', 'f': 100.0, 'b': True}]
    >>> from_dict(List[Foo], lst)
    [Foo(i=10, s='foo', f=100.0, b=True), Foo(i=20, s='foo', f=100.0, b=True)]
    """
    return from_obj(cls, o, named=True, reuse_instances=reuse_instances)


def from_tuple(cls, o, reuse_instances: bool = ...):
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
    >>> from_tuple(List[Foo], lst)
    [Foo(i=10, s='foo', f=100.0, b=True), Foo(i=20, s='foo', f=100.0, b=True)]
    """
    return from_obj(cls, o, named=False, reuse_instances=reuse_instances)


@dataclass
class DeField(Field):
    """
    Field class for deserialization.
    """

    datavar: Optional[str] = None  # name of variable to deserialize from.
    index: int = 0  # Field index.
    iterbased: bool = False  # Iterater based deserializer or not.

    def __getitem__(self, n) -> 'DeField':
        """
        Access inner `Field` e.g. T of List[T].
        """
        typ = type_args(self.type)[n]
        opts = {
            'case': self.case,
            'rename': self.rename,
            'skip': self.skip,
            'skip_if': self.skip_if,
            'skip_if_false': self.skip_if_false,
            'flatten': self.flatten,
            'alias': self.alias,
            'parent': self.parent,
        }
        if is_list(self.type) or is_dict(self.type) or is_set(self.type):
            return InnerField(typ, 'v', datavar='v', **opts)
        elif is_tuple(self.type):
            return InnerField(typ, f'{self.data}[{n}]', datavar=f'{self.data}[{n}]', **opts)
        else:
            return DeField(typ, self.name, datavar=self.datavar, index=self.index, iterbased=self.iterbased, **opts)

    def key_field(self) -> 'DeField':
        """
        Get inner key field for Dict like class.
        """
        k = self[0]
        k.name = 'k'
        k.datavar = 'k'
        return k

    def value_field(self) -> 'DeField':
        """
        Get inner value field for Dict like class.
        """
        return self[1]

    @property
    def data(self) -> str:
        if self.iterbased:
            return f'{self.datavar}[{self.index}]'
        elif is_union(self.type) and type(None) in get_args(self.type):
            return f'{self.datavar}.get("{self.conv_name()}")'
        else:
            return f'{self.datavar}["{self.conv_name()}"]'

    @data.setter
    def data(self, d):
        self.datavar = d

    def data_or(self):
        if self.iterbased:
            return self.data
        else:
            return f'{self.datavar}.get("{self.conv_name()}")'


@dataclass
class InnerField(DeField):
    """
    Field for inner type e.g. T of List[T].
    """

    @property
    def data(self) -> str:
        return self.datavar or ''

    @data.setter
    def data(self, d):
        self.datavar = d


defields = functools.partial(fields, DeField)


@dataclass
class Renderer:
    """
    Render rvalue for code generation.
    """

    func: str
    cls: Optional[Type] = None
    custom: Optional[DeserializeFunc] = None  # Custom class level deserializer.
    import_numpy: bool = False
    suppress_coerce: bool = False

    def render(self, arg: DeField) -> str:
        """
        Render rvalue
        """
        if arg.deserializer and arg.deserializer.inner is not default_deserializer:
            res = self.custom_field_deserializer(arg)
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
        elif is_primitive(arg.type):
            res = self.primitive(arg)
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
        elif isinstance(arg.type, TypeVar):
            index = find_generic_arg(self.cls, arg.type)
            res = (
                f"from_obj(get_generic_arg(maybe_generic, {index}), "
                f" {arg.data}, named={not arg.iterbased}, reuse_instances=reuse_instances)"
            )
        elif is_generic(arg.type):
            arg.type = get_origin(arg.type)
            res = self.render(arg)
        elif is_literal(arg.type):
            res = self.literal(arg)
        else:
            return f"raise_unsupported_type({arg.data})"

        if arg.supports_default():
            res = self.default(arg, res)

        if self.custom and not arg.deserializer:
            # Rerender the code for default deserializer.
            default = Renderer(self.func, self.cls, None, suppress_coerce=self.suppress_coerce).render(arg)
            return self.custom_class_deserializer(arg, default)
        else:
            return res

    def custom_field_deserializer(self, arg: DeField) -> str:
        """
        Render rvalue for the field with custom deserializer.
        """
        assert arg.deserializer
        return f"{arg.deserializer.name}({arg.data})"

    def custom_class_deserializer(self, arg: DeField, code: str) -> str:
        """
        Render custom class deserializer.
        """
        # The function takes a closure in order to execute the default value lazily.
        return (
            f'serde_custom_class_deserializer({typename(arg.type)}, {arg.datavar}, {arg.data_or()}, '
            f'default=lambda: {code})'
        )

    def dataclass(self, arg: DeField) -> str:
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

        opts = "maybe_generic=maybe_generic, reuse_instances=reuse_instances"

        if arg.is_self_referencing():
            class_name = "cls"
        else:
            class_name = typename(arg.type)

        return f"{class_name}.{SERDE_SCOPE}.funcs['{self.func}'](data={var}, {opts})"

    def opt(self, arg: DeField) -> str:
        """
        Render rvalue for Optional.

        >>> from typing import List
        >>> Renderer('foo').render(DeField(Optional[int], 'o', datavar='data'))
        '(coerce(int, data["o"])) if data.get("o") is not None else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '([coerce(int, v) for v in data["o"]]) if data.get("o") is not None else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '([coerce(int, v) for v in data["o"]]) if data.get("o") is not None else None'

        >>> @deserialize
        ... class Foo:
        ...     o: Optional[List[int]]
        >>> Renderer('foo').render(DeField(Optional[Foo], 'f', datavar='data'))
        '(Foo.__serde__.funcs[\\'foo\\'](data=data["f"], maybe_generic=maybe_generic, \
reuse_instances=reuse_instances)) if data.get("f") is not None else None'
        """
        value = arg[0]
        if arg.iterbased:
            exists = f'{arg.data} is not None'
        else:
            exists = f'{arg.datavar}.get("{arg.conv_name()}") is not None'
        return f'({self.render(value)}) if {exists} else None'

    def list(self, arg: DeField) -> str:
        """
        Render rvalue for list.

        >>> from typing import List
        >>> Renderer('foo').render(DeField(List[int], 'l', datavar='data'))
        '[coerce(int, v) for v in data["l"]]'

        >>> Renderer('foo').render(DeField(List[List[int]], 'l', datavar='data'))
        '[[coerce(int, v) for v in v] for v in data["l"]]'
        """
        if is_bare_list(arg.type):
            return f'list({arg.data})'
        else:
            return f'[{self.render(arg[0])} for v in {arg.data}]'

    def set(self, arg: DeField) -> str:
        """
        Render rvalue for set.

        >>> from typing import Set
        >>> Renderer('foo').render(DeField(Set[int], 'l', datavar='data'))
        'set(coerce(int, v) for v in data["l"])'

        >>> Renderer('foo').render(DeField(Set[Set[int]], 'l', datavar='data'))
        'set(set(coerce(int, v) for v in v) for v in data["l"])'
        """
        if is_bare_set(arg.type):
            return f'set({arg.data})'
        elif is_frozen_set(arg.type):
            return f'frozenset({self.render(arg[0])} for v in {arg.data})'
        else:
            return f'set({self.render(arg[0])} for v in {arg.data})'

    def tuple(self, arg: DeField) -> str:
        """
        Render rvalue for tuple.

        >>> from typing import List, Tuple
        >>> @deserialize
        ... class Foo: pass
        >>> Renderer('foo').render(DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data'))
        '(coerce(str, data["d"][0]), coerce(int, data["d"][1]), \
[coerce(int, v) for v in data["d"][2]], \
Foo.__serde__.funcs[\\'foo\\'](data=data["d"][3], maybe_generic=maybe_generic, reuse_instances=reuse_instances),)'

        >>> field = DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data', index=0, iterbased=True)
        >>> Renderer('foo').render(field)
        "(coerce(str, data[0][0]), coerce(int, data[0][1]), \
[coerce(int, v) for v in data[0][2]], Foo.__serde__.funcs['foo'](data=data[0][3], \
maybe_generic=maybe_generic, reuse_instances=reuse_instances),)"
        """
        if is_bare_tuple(arg.type) or is_variable_tuple(arg.type):
            return f'tuple({arg.data})'
        else:
            values = []
            for i, typ in enumerate(type_args(arg.type)):
                inner = arg[i]
                values.append(self.render(inner))
            return f'({", ".join(values)},)'  # trailing , is required for single element tuples

    def dict(self, arg: DeField) -> str:
        """
        Render rvalue for dict.

        >>> from typing import List
        >>> Renderer('foo').render(DeField(Dict[str, int], 'd', datavar='data'))
        '{coerce(str, k): coerce(int, v) for k, v in data["d"].items()}'

        >>> @deserialize
        ... class Foo: pass
        >>> Renderer('foo').render(DeField(Dict[Foo, List[Foo]], 'f', datavar='data'))
        '{Foo.__serde__.funcs[\\'foo\\'](data=k, maybe_generic=maybe_generic, reuse_instances=reuse_instances): \
[Foo.__serde__.funcs[\\'foo\\'](data=v, maybe_generic=maybe_generic, reuse_instances=reuse_instances) for v in v] \
for k, v in data["f"].items()}'
        """
        if is_bare_dict(arg.type):
            return arg.data
        elif is_default_dict(arg.type):
            k = arg.key_field()
            v = arg.value_field()
            origin = get_origin(v.type)
            if origin:
                # When the callable type is of generic type e.g List.
                # Get origin type "list" from "List[X]".
                callable = origin.__name__
            else:
                # When the callable type is non generic type e.g int, Foo.
                callable = v.type.__name__
            return f'collections.defaultdict({callable}, \
                    {{{self.render(k)}: {self.render(v)} for k, v in {arg.data}.items()}})'
        else:
            k = arg.key_field()
            v = arg.value_field()
            return f'{{{self.render(k)}: {self.render(v)} for k, v in {arg.data}.items()}}'

    def enum(self, arg: DeField) -> str:
        return f'{typename(arg.type)}({self.primitive(arg)})'

    def primitive(self, arg: DeField, suppress_coerce: bool = False) -> str:
        """
        Render rvalue for primitives.

        >>> Renderer('foo').render(DeField(int, 'i', datavar='data'))
        'coerce(int, data["i"])'

        >>> Renderer('foo').render(DeField(int, 'int_field', datavar='data', case='camelcase'))
        'coerce(int, data["intField"])'

        >>> Renderer('foo').render(DeField(int, 'i', datavar='data', index=1, iterbased=True))
        'coerce(int, data[1])'
        """
        typ = typename(arg.type)
        dat = arg.data
        if arg.alias:
            aliases = map(lambda s: f'"{s}"', [arg.name, *arg.alias])
            dat = f"_get_by_aliases(data, [{','.join(aliases)}])"
        if self.suppress_coerce:
            return dat
        else:
            return f'coerce({typ}, {dat})'

    def c_tor(self, arg: DeField) -> str:
        return f"{typename(arg.type)}({arg.data})"

    def c_tor_with_check(self, arg: DeField, ctor: Optional[str] = None) -> str:
        if ctor is None:
            ctor = self.c_tor(arg)
        return f"{arg.data} if isinstance({arg.data}, {typename(arg.type)}) else {ctor}"

    def union_func(self, arg: DeField) -> str:
        func_name = union_func_name(UNION_DE_PREFIX, type_args(arg.type))
        return f"serde_scope.funcs['{func_name}'](cls=cls, data={arg.data}, reuse_instances=reuse_instances)"

    def literal(self, arg: DeField) -> str:
        func_name = literal_func_name(type_args(arg.type))
        return f"serde_scope.funcs['{func_name}'](cls=cls, data={arg.data}, reuse_instances=reuse_instances)"

    def default(self, arg: DeField, code: str) -> str:
        exists = f'"{arg.conv_name()}" in {arg.datavar}'
        if has_default(arg):
            return f'({code}) if {exists} else serde_scope.defaults["{arg.name}"]'
        elif has_default_factory(arg):
            return f'({code}) if {exists} else serde_scope.defaults["{arg.name}"]()'
        else:
            return code


def to_arg(f: DeField, index, rename_all: Optional[str] = None) -> DeField:
    f.index = index
    f.data = 'data'
    f.case = f.case or rename_all
    return f


def to_iter_arg(f: DeField, *args, **kwargs) -> DeField:
    f = to_arg(f, *args, **kwargs)
    f.iterbased = True
    return f


def render_from_iter(cls: Type, custom: Optional[DeserializeFunc] = None, type_check: TypeCheck = NoCheck) -> str:
    template = """
def {{func}}(cls=cls, maybe_generic=None, data=None, reuse_instances = {{serde_scope.reuse_instances_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}

  if data is None:
    return None

  {% for f in fields %}
  __{{f.name}} = {{f|arg(loop.index-1)|rvalue}}
  {% endfor %}

  try:
    return cls(
      {% for f in fields %}
      __{{f.name}},
      {% endfor %}
    )
  except Exception as e:
    raise UserError(e)
    """

    renderer = Renderer(FROM_ITER, cls=cls, custom=custom, suppress_coerce=(not type_check.is_coerce()))
    env = jinja2.Environment(loader=jinja2.DictLoader({'iter': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_iter_arg})
    res = env.get_template('iter').render(func=FROM_ITER, serde_scope=getattr(cls, SERDE_SCOPE), fields=defields(cls))

    if renderer.import_numpy:
        res = "import numpy\n" + res

    return res


def render_from_dict(
    cls: Type,
    rename_all: Optional[str] = None,
    custom: Optional[DeserializeFunc] = None,
    type_check: TypeCheck = NoCheck,
) -> str:
    template = """
def {{func}}(cls=cls, maybe_generic=None, data=None,
             reuse_instances = {{serde_scope.reuse_instances_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}

  if data is None:
    return None

  {% for f in fields %}
  __{{f.name}} = {{f|arg(loop.index-1)|rvalue}}
  {% endfor %}

  try:
    rv = cls(
    {% for f in fields %}
    __{{f.name}},
    {% endfor %}
    )
  except Exception as e:
    raise UserError(e)

  {% if type_check.is_strict() %}
  rv.__serde__.funcs['typecheck'](rv)
  {% endif %}

  return rv
    """

    renderer = Renderer(FROM_DICT, cls=cls, custom=custom, suppress_coerce=(not type_check.is_coerce()))
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': functools.partial(to_arg, rename_all=rename_all)})
    res = env.get_template('dict').render(
        func=FROM_DICT, serde_scope=getattr(cls, SERDE_SCOPE), fields=defields(cls), type_check=type_check
    )

    if renderer.import_numpy:
        res = "import numpy\n" + res

    return res


def render_union_func(cls: Type, union_args: List[Type], tagging: Tagging = DefaultTagging) -> str:
    template = """
def {{func}}(cls=cls, maybe_generic=None, data=None, reuse_instances = {{serde_scope.reuse_instances_default}}):
  errors = []
  {% for t in union_args %}
  try:
    # create fake dict so we can reuse the normal render function
    {% if tagging.is_external() and is_taggable(t)  %}
    ensure("{{t|typename}}" in data , "'{{t|typename}}' key is not present")
    fake_dict = {"fake_key": data["{{t|typename}}"]}

    {% elif tagging.is_internal() and is_taggable(t) %}
    ensure("{{tagging.tag}}" in data , "'{{tagging.tag}}' key is not present")
    ensure("{{t|typename}}" == data["{{tagging.tag}}"], "tag '{{t|typename}}' isn't found")
    fake_dict = {"fake_key": data}

    {% elif tagging.is_adjacent() and is_taggable(t) %}
    ensure("{{tagging.tag}}" in data , "'{{tagging.tag}}' key is not present")
    ensure("{{tagging.content}}" in data , "'{{tagging.content}}' key is not present")
    ensure("{{t|typename}}" == data["{{tagging.tag}}"], "tag '{{t|typename}}' isn't found")
    fake_dict = {"fake_key": data["{{tagging.content}}"]}

    {% else %}
    fake_dict = {"fake_key": data}
    {% endif %}

    {% if t|is_primitive or t|is_none %}
    if not isinstance(fake_dict["fake_key"], {{t|typename}}):
        raise Exception("Not a type of {{t|typename}}")
    {% endif %}
    return {{t|arg|rvalue}}
  except Exception as e:
    errors.append(f' Failed to deserialize into {{t|typename}}: {e}')
  {% endfor %}
  raise SerdeError("Can not deserialize " + repr(data) + " of type " + \
          typename(type(data)) + " into {{union_name}}.\\nReasons:\\n" + "\\n".join(errors))
    """
    union_name = f"Union[{', '.join([typename(a) for a in union_args])}]"

    renderer = Renderer(FROM_DICT, cls=cls, suppress_coerce=True)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update(
        {'arg': lambda x: DeField(x, datavar="fake_dict", name="fake_key")}
    )  # use custom to_arg for fake field
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'is_primitive': is_primitive})
    env.filters.update({'is_none': is_none})
    env.filters.update({'typename': typename})
    return env.get_template('dict').render(
        func=union_func_name(UNION_DE_PREFIX, union_args),
        serde_scope=getattr(cls, SERDE_SCOPE),
        union_args=union_args,
        union_name=union_name,
        tagging=tagging,
        is_taggable=Tagging.is_taggable,
    )


def render_literal_func(cls: Type, literal_args: List[Any], tagging: Tagging = DefaultTagging) -> str:
    template = """
def {{func}}(cls=cls, maybe_generic=None, data=None, reuse_instances = {{serde_scope.reuse_instances_default}}):
  if data in ({%- for v in literal_args -%}{{v|repr}},{%- endfor -%}):
    return data
  raise SerdeError("Can not deserialize " + repr(data) + " as {{literal_name}}.")
    """
    literal_name = f"Literal[{', '.join([repr(a) for a in literal_args])}]"

    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'repr': repr})
    env.filters.update({'type': type})
    return env.get_template('dict').render(
        func=literal_func_name(literal_args),
        serde_scope=getattr(cls, SERDE_SCOPE),
        literal_args=literal_args,
        literal_name=literal_name,
        tagging=tagging,
        is_taggable=Tagging.is_taggable,
    )
