"""
This module provides `serialize`, `is_serializable` `to_dict`, `to_tuple` and classes and functions
associated with serialization.
"""

import abc
import copy
import dataclasses
import functools
from dataclasses import dataclass, is_dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional, Type

import jinja2

from .compat import (
    SerdeError,
    SerdeSkip,
    is_bare_dict,
    is_bare_list,
    is_bare_opt,
    is_bare_set,
    is_bare_tuple,
    is_dict,
    is_enum,
    is_list,
    is_none,
    is_opt,
    is_primitive,
    is_set,
    is_tuple,
    is_union,
    iter_types,
    iter_unions,
    type_args,
    typename,
)
from .core import (
    SERDE_SCOPE,
    TO_DICT,
    TO_ITER,
    UNION_SE_PREFIX,
    DateTimeTypes,
    Field,
    SerdeScope,
    StrSerializableTypes,
    add_func,
    conv,
    fields,
    filter_scope,
    is_instance,
    logger,
    raise_unsupported_type,
    union_func_name,
)

__all__ = ["serialize", "is_serializable", "to_dict", "to_tuple"]

# Interface of Custom serialize function.
SerializeFunc = Callable[[Type, Any], Any]


def default_serializer(_cls: Type, obj):
    """
    Marker function to tell serde to use the default serializer. It's used when custom serializer is specified
    at the class but you want to override a field with the default serializer.
    """


def serde_custom_class_serializer(cls: Type, obj, custom: SerializeFunc, default: Callable):
    try:
        return custom(cls, obj)
    except SerdeSkip:
        return default()


class Serializer(metaclass=abc.ABCMeta):
    """
    `Serializer` base class. Subclass this to customize serialize behaviour.

    See `serde.json.JsonSerializer` and `serde.msgpack.MsgPackSerializer` for example usage.
    """

    @abc.abstractclassmethod
    def serialize(cls, obj, **opts):
        pass


def serialize(
    _cls=None,
    rename_all: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    serializer: Optional[SerializeFunc] = None,
    **kwargs,
):
    """
    A dataclass with this decorator is serializable into any of the data formats supported by pyserde.

    >>> from datetime import datetime
    >>> from serde import serialize
    >>> from serde.json import to_json
    >>>
    >>> @serialize
    ... class Foo:
    ...     i: int
    ...     s: str
    ...     f: float
    ...     b: bool
    >>>
    >>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
    '{"i": 10, "s": "foo", "f": 100.0, "b": true}'

    #### Class Attributes

    Class attributes can be specified as arguments in the `serialize` decorator in order to customize the serialization
    behaviour of the class entirely.

    * `rename_all` attribute converts field names into the specified string case.
    The following example converts snake-case field names into camel-case names.

    >>> @serialize(rename_all = 'camelcase')
    ... class Foo:
    ...     int_field: int
    ...     str_field: str
    >>>
    >>> to_json(Foo(int_field=10, str_field='foo'))
    '{"intField": 10, "strField": "foo"}'

    * `serializer` takes a custom class-level serialize function. The function applies to the all the fields
    in the class.

    >>> def serializer(cls, o):
    ...    if cls is datetime:
    ...        return o.strftime('%d/%m/%y')
    ...    else:
    ...        raise SerdeSkip()

    The first argument `cls` is a class of the field and the second argument `o` is a value of the field.
    `serializer` function will be called for every field. If you don't want to use the custom serializer
    for a certain field, raise `serde.SerdeSkip` exception, pyserde will use the default serializer for that field.

    >>> @serialize(serializer=serializer)
    ... class Foo:
    ...     i: int
    ...     dt: datetime

    This custom serializer serializes `datetime` object into the string in `MM/DD/YY` format.

    >>> to_json(Foo(10, datetime(2021, 1, 1, 0, 0, 0)))
    '{"i": 10, "dt": "01/01/21"}'
    """

    def wrap(cls: Type):
        # If no `dataclass` found in the class, dataclassify it automatically.
        if not is_dataclass(cls):
            dataclass(cls)

        g: Dict[str, Any] = {}

        # Create a scope storage used by serde.
        # Each class should get own scope. Child classes can not share scope with parent class.
        # That's why we need the "scope.cls is not cls" check.
        scope: SerdeScope = getattr(cls, SERDE_SCOPE, None)
        if scope is None or scope.cls is not cls:
            scope = SerdeScope(
                cls, reuse_instances_default=reuse_instances_default, convert_sets_default=convert_sets_default
            )
            setattr(cls, SERDE_SCOPE, scope)

        # Set some globals for all generated functions
        g['cls'] = cls
        g['copy'] = copy
        g['serde_scope'] = scope
        g['SerdeError'] = SerdeError
        g['raise_unsupported_type'] = raise_unsupported_type
        g['enum_value'] = enum_value
        g['is_dataclass'] = is_dataclass
        g['typename'] = typename  # used in union functions
        g['is_instance'] = is_instance  # used in union functions
        g['to_obj'] = to_obj
        if serialize:
            g['serde_custom_class_serializer'] = functools.partial(serde_custom_class_serializer, custom=serializer)

        # Collect types used in the generated code.
        for typ in iter_types(cls):
            if typ is cls or (is_primitive(typ) and not is_enum(typ)):
                continue
            g[typename(typ)] = typ

        # render all union functions
        for union in iter_unions(cls):
            union_args = type_args(union)
            union_key = union_func_name(UNION_SE_PREFIX, union_args)
            add_func(scope, union_key, render_union_func(cls, union_args), g)
            scope.union_se_args[union_key] = union_args

        for f in sefields(cls):
            if f.skip_if:
                g[f.skip_if.name] = f.skip_if
            if f.serializer:
                g[f.serializer.name] = f.serializer

        add_func(scope, TO_ITER, render_to_tuple(cls, serializer), g)
        add_func(scope, TO_DICT, render_to_dict(cls, rename_all, serializer), g)

        logger.debug(f'{cls.__name__}: {SERDE_SCOPE} {scope}')

        return cls

    if _cls is None:
        return wrap  # type: ignore

    return wrap(_cls)


def is_serializable(instance_or_class: Any) -> bool:
    """
    Test if an instance or class is serializable.

    >>> @serialize
    ... class Foo:
    ...     pass

    Testing `Foo` class object returns `True`.
    >>> is_serializable(Foo)
    True

    Testing `Foo` object laso returns `True`.
    >>> is_serializable(Foo())
    True
    """
    return hasattr(instance_or_class, SERDE_SCOPE)


def to_obj(o, named: bool, reuse_instances: bool, convert_sets: bool):
    thisfunc = functools.partial(to_obj, named=named, reuse_instances=reuse_instances, convert_sets=convert_sets)
    if o is None:
        return None
    if is_serializable(o):
        serde_scope: SerdeScope = getattr(o, SERDE_SCOPE)
        if named:
            return serde_scope.funcs[TO_DICT](o, reuse_instances=reuse_instances, convert_sets=convert_sets)
        else:
            return serde_scope.funcs[TO_ITER](o, reuse_instances=reuse_instances, convert_sets=convert_sets)
    elif is_dataclass(o):
        if named:
            return dataclasses.asdict(o)
        else:
            return dataclasses.astuple(o)
    elif isinstance(o, list):
        return [thisfunc(e) for e in o]
    elif isinstance(o, tuple):
        return tuple(thisfunc(e) for e in o)
    elif isinstance(o, set):
        return [thisfunc(e) for e in o]
    elif isinstance(o, dict):
        return {k: thisfunc(v) for k, v in o.items()}
    elif isinstance(o, StrSerializableTypes):
        return str(o)
    elif isinstance(o, DateTimeTypes):
        return o.isoformat()

    return o


def astuple(v):
    """
    Serialize object into tuple.
    """
    return to_tuple(v, reuse_instances=False, convert_sets=False)


def to_tuple(o, reuse_instances: bool = ..., convert_sets: bool = ...) -> Any:
    """
    Serialize object into tuple.

    >>> @serialize
    ... class Foo:
    ...     i: int
    ...     s: str = 'foo'
    ...     f: float = 100.0
    ...     b: bool = True
    >>>
    >>> to_tuple(Foo(i=10))
    (10, 'foo', 100.0, True)

    You can pass any type supported by pyserde. For example,

    >>> lst = [Foo(i=10), Foo(i=20)]
    >>> to_tuple(lst)
    [(10, 'foo', 100.0, True), (20, 'foo', 100.0, True)]
    """
    return to_obj(o, named=False, reuse_instances=reuse_instances, convert_sets=convert_sets)


def asdict(v):
    """
    Serialize object into dictionary.
    """
    return to_dict(v, reuse_instances=False, convert_sets=False)


def to_dict(o, reuse_instances: bool = ..., convert_sets: bool = ...) -> Any:
    """
    Serialize object into dictionary.

    >>> @serialize
    ... class Foo:
    ...     i: int
    ...     s: str = 'foo'
    ...     f: float = 100.0
    ...     b: bool = True
    >>>
    >>> to_dict(Foo(i=10))
    {'i': 10, 's': 'foo', 'f': 100.0, 'b': True}

    You can pass any type supported by pyserde. For example,

    >>> lst = [Foo(i=10), Foo(i=20)]
    >>> to_dict(lst)
    [{'i': 10, 's': 'foo', 'f': 100.0, 'b': True}, {'i': 20, 's': 'foo', 'f': 100.0, 'b': True}]
    """
    return to_obj(o, named=True, reuse_instances=reuse_instances, convert_sets=convert_sets)


@dataclass
class SeField(Field):
    """
    Field class for serialization.
    """

    parent: Optional['SeField'] = None

    @property
    def varname(self) -> str:
        """
        Get variable name in the generated code e.g. obj.a.b
        """
        var = self.parent.varname if self.parent else None
        if var:
            return f'{var}.{self.name}'
        else:
            if self.name is None:
                raise SerdeError('Field name is None.')
            return self.name

    def __getitem__(self, n) -> 'SeField':
        typ = type_args(self.type)[n]
        return SeField(typ, name=None)


def sefields(cls: Type) -> Iterator[SeField]:
    """
    Iterate fields for serialization.
    """
    for f in fields(SeField, cls):
        f.parent = SeField(None, 'obj')  # type: ignore
        assert isinstance(f, SeField)
        yield f


def render_to_tuple(cls: Type, custom: Optional[SerializeFunc] = None) -> str:
    template = """
def {{func}}(obj, reuse_instances = {{serde_scope.reuse_instances_default}},
             convert_sets = {{serde_scope.convert_sets_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}
  if convert_sets is Ellipsis:
    convert_sets = {{serde_scope.convert_sets_default}}

  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  return (
  {% for f in fields -%}
  {% if not f.skip|default(False) %}
  {{f|rvalue()}},
  {% endif -%}
  {% endfor -%}
  )
    """

    renderer = Renderer(TO_ITER, custom)
    env = jinja2.Environment(loader=jinja2.DictLoader({'iter': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'filter_scope': filter_scope})
    return env.get_template('iter').render(func=TO_ITER, serde_scope=getattr(cls, SERDE_SCOPE), fields=sefields(cls))


def render_to_dict(cls: Type, case: Optional[str] = None, custom: Optional[SerializeFunc] = None) -> str:
    template = """
def {{func}}(obj, reuse_instances = {{serde_scope.reuse_instances_default}},
             convert_sets = {{serde_scope.convert_sets_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}
  if convert_sets is Ellipsis:
    convert_sets = {{serde_scope.convert_sets_default}}

  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  res = {}
  {% for f in fields -%}
  {% if not f.skip -%}
    {% if f.skip_if -%}
  if not {{f.skip_if.name}}({{f|rvalue}}):
    {{f|lvalue}} = {{f|rvalue}}
    {% else -%}
  {{f|lvalue}} = {{f|rvalue}}
    {% endif -%}
  {% endif %}

  {% endfor -%}
  return res
    """
    renderer = Renderer(TO_DICT, custom)
    lrenderer = LRenderer(case)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'lvalue': lrenderer.render})
    env.filters.update({'case': functools.partial(conv, case=case)})
    env.filters.update({'filter_scope': filter_scope})
    return env.get_template('dict').render(func=TO_DICT, serde_scope=getattr(cls, SERDE_SCOPE), fields=sefields(cls))


def render_union_func(cls: Type, union_args: List[Type]) -> str:
    template = """
def {{func}}(obj, reuse_instances, convert_sets):
  union_args = serde_scope.union_se_args['{{func}}']

  {% for t in union_args %}
  if is_instance(obj, union_args[{{loop.index0}}]):
    return {{t|arg|rvalue()}}
  {% endfor %}
  raise SerdeError("Can not serialize " + repr(obj) + " of type " + typename(type(obj)) + " for {{union_name}}")
    """
    union_name = f"Union[{', '.join([typename(a) for a in union_args])}]"

    renderer = Renderer(TO_DICT)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'arg': lambda x: SeField(x, "obj")})
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'filter_scope': filter_scope})
    return env.get_template('dict').render(
        func=union_func_name(UNION_SE_PREFIX, union_args),
        serde_scope=getattr(cls, SERDE_SCOPE),
        union_args=union_args,
        union_name=union_name,
    )


@dataclass
class LRenderer:
    """
    Render lvalue for various types.
    """

    case: Optional[str]

    def render(self, arg: SeField) -> str:
        """
        Render lvalue
        """
        if is_dataclass(arg.type) and arg.flatten:
            return self.flatten(arg)
        else:
            return f'res["{arg.conv_name(self.case)}"]'

    def flatten(self, arg: SeField) -> str:
        """
        Render field with flatten attribute.
        """
        flattened = []
        for f in sefields(arg.type):
            flattened.append(self.render(f))
        return ", ".join(flattened)


@dataclass
class Renderer:
    """
    Render rvalue for code generation.
    """

    func: str
    custom: Optional[SerializeFunc] = None  # Custom class level serializer.

    def render(self, arg: SeField) -> str:
        """
        Render rvalue

        >>> from typing import Tuple
        >>> Renderer(TO_ITER).render(SeField(int, 'i'))
        'i'

        >>> Renderer(TO_ITER).render(SeField(List[int], 'l'))
        '[v for v in l]'

        >>> @serialize
        ... @dataclass(unsafe_hash=True)
        ... class Foo:
        ...    val: int
        >>> Renderer(TO_ITER).render(SeField(Foo, 'foo'))
        "foo.__serde__.funcs['to_iter'](foo, reuse_instances=reuse_instances, convert_sets=convert_sets)"

        >>> Renderer(TO_ITER).render(SeField(List[Foo], 'foo'))
        "[v.__serde__.funcs['to_iter'](v, reuse_instances=reuse_instances, convert_sets=convert_sets) for v in foo]"

        >>> Renderer(TO_ITER).render(SeField(Dict[str, Foo], 'foo'))
        "{k: v.__serde__.funcs['to_iter'](v, reuse_instances=reuse_instances, \
convert_sets=convert_sets) for k, v in foo.items()}"

        >>> Renderer(TO_ITER).render(SeField(Dict[Foo, Foo], 'foo'))
        "{k.__serde__.funcs['to_iter'](k, reuse_instances=reuse_instances, \
convert_sets=convert_sets): v.__serde__.funcs['to_iter'](v, reuse_instances=reuse_instances, \
convert_sets=convert_sets) for k, v in foo.items()}"

        >>> Renderer(TO_ITER).render(SeField(Tuple[str, Foo, int], 'foo'))
        "(foo[0], foo[1].__serde__.funcs['to_iter'](foo[1], reuse_instances=reuse_instances, \
convert_sets=convert_sets), foo[2],)"
        """
        if arg.serializer and arg.serializer.inner is not default_serializer:
            res = self.custom_field_serializer(arg)
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
        elif is_primitive(arg.type):
            res = self.primitive(arg)
        elif is_union(arg.type):
            res = self.union_func(arg)
        elif arg.type in StrSerializableTypes:
            res = f"{arg.varname} if reuse_instances else {self.string(arg)}"
        elif arg.type in DateTimeTypes:
            res = f"{arg.varname} if reuse_instances else {arg.varname}.isoformat()"
        elif is_none(arg.type):
            res = "None"
        elif arg.type is Any:
            res = f"to_obj({arg.varname}, True, False, False)"
        else:
            res = f"raise_unsupported_type({arg.varname})"

        # Custom field serializer overrides custom class serializer.
        if self.custom and not arg.serializer:
            return f'serde_custom_class_serializer({typename(arg.type)}, {arg.varname}, default=lambda: {res})'
        else:
            return res

    def custom_field_serializer(self, arg: SeField) -> str:
        """
        Render rvalue for the field with custom serializer.
        """
        assert arg.serializer
        return f"{arg.serializer.name}({arg.varname})"

    def dataclass(self, arg: SeField) -> str:
        """
        Render rvalue for dataclass.
        """
        if arg.flatten:
            flattened = []
            for f in sefields(arg.type):
                f.parent = arg  # type: ignore
                flattened.append(self.render(f))  # type: ignore
            return ", ".join(flattened)
        else:
            return (
                f"{arg.varname}.{SERDE_SCOPE}.funcs['{self.func}']({arg.varname},"
                " reuse_instances=reuse_instances, convert_sets=convert_sets)"
            )

    def opt(self, arg: SeField) -> str:
        """
        Render rvalue for optional.
        """
        if is_bare_opt(arg.type):
            return f'{arg.varname} if {arg.varname} is not None else None'
        else:
            inner = arg[0]
            inner.name = arg.varname
            return f'({self.render(inner)}) if {arg.varname} is not None else None'

    def list(self, arg: SeField) -> str:
        """
        Render rvalue for list.
        """
        if is_bare_list(arg.type):
            return arg.varname
        else:
            earg = arg[0]
            earg.name = 'v'
            return f'[{self.render(earg)} for v in {arg.varname}]'

    def set(self, arg: SeField) -> str:
        """
        Render rvalue for set.
        """
        if is_bare_set(arg.type):
            return f'list({arg.varname}) if convert_sets else {arg.varname}'
        else:
            earg = arg[0]
            earg.name = 'v'
            return (
                f'[{self.render(earg)} for v in {arg.varname}] '
                f'if convert_sets else set({self.render(earg)} for v in {arg.varname})'
            )

    def tuple(self, arg: SeField) -> str:
        """
        Render rvalue for tuple.
        """
        if is_bare_tuple(arg.type):
            return arg.varname
        else:
            rvalues = []
            for i, _ in enumerate(type_args(arg.type)):
                r = arg[i]
                r.name = f'{arg.varname}[{i}]'
                rvalues.append(self.render(r))
            return f"({', '.join(rvalues)},)"  # trailing , is required for single element tuples

    def dict(self, arg: SeField) -> str:
        """
        Render rvalue for dict.
        """
        if is_bare_dict(arg.type):
            return arg.varname
        else:
            karg = arg[0]
            karg.name = 'k'
            varg = arg[1]
            varg.name = 'v'
            return f'{{{self.render(karg)}: {self.render(varg)} for k, v in {arg.varname}.items()}}'

    def enum(self, arg: SeField) -> str:
        return f'enum_value({arg.type.__name__}, {arg.varname})'

    def primitive(self, arg: SeField) -> str:
        """
        Render rvalue for primitives.
        """
        return f'{arg.varname}'

    def string(self, arg: SeField) -> str:
        return f"str({arg.varname})"

    def union_func(self, arg: SeField) -> str:
        func_name = union_func_name(UNION_SE_PREFIX, type_args(arg.type))
        return f"serde_scope.funcs['{func_name}']({arg.varname}, reuse_instances, convert_sets)"


def enum_value(cls, e):
    """
    Helper function to get value from enum or enum compatible value.
    """
    if is_enum(e):
        v = e.value
        # Recursively get value of Nested enum.
        if is_enum(v):
            return enum_value(v.__class__, v)
        else:
            return v
    else:
        return cls(e).value
