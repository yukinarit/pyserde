"""
Defines classes and functions for `serialize` decorator.

"""
import abc
import copy  # noqa
import dataclasses
import functools
from dataclasses import dataclass, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from ipaddress import IPv4Address, IPv4Interface, IPv4Network, IPv6Address, IPv6Interface, IPv6Network
from pathlib import Path, PosixPath, PurePath, PurePosixPath, PureWindowsPath, WindowsPath
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from uuid import UUID

import jinja2

from .compat import (
    T,
    is_bare_dict,
    is_bare_list,
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
    Field,
    SerdeError,
    SerdeScope,
    add_func,
    conv,
    fields,
    is_instance,
    logger,
    raise_unsupported_type,
    union_func_name,
)

__all__: List = ['serialize', 'is_serializable', 'Serializer', 'to_tuple', 'to_dict']

Custom = Optional[Callable[[Any], Any]]


class Serializer(metaclass=abc.ABCMeta):
    """
    `Serializer` base class. Subclass this to customize serialize behaviour.

    See `serde.json.JsonSerializer` and `serde.msgpack.MsgPackSerializer` for example usage.
    """

    @abc.abstractclassmethod
    def serialize(cls, obj, **opts):
        pass


def serialize(
    _cls: Type[T] = None,
    rename_all: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
) -> Type[T]:
    """
    `serialize` decorator. A dataclass with this decorator can be serialized
    into an object in various data format such as JSON and MsgPack.

    >>> from serde import serialize
    >>> from serde.json import to_json
    >>>
    >>> # Mark the class serializable.
    >>> @serialize
    ... @dataclass
    ... class Foo:
    ...     i: int
    ...     s: str
    ...     f: float
    ...     b: bool
    >>>
    >>> to_json(Foo(i=10, s='foo', f=100.0, b=True))
    '{"i": 10, "s": "foo", "f": 100.0, "b": true}'

    Additionally, `serialize` supports case conversion. Pass case name in
    `serialize` decorator as shown below.

    >>> @serialize(rename_all = 'camelcase')
    ... @dataclass
    ... class Foo:
    ...     int_field: int
    ...     str_field: str
    >>>
    >>> to_json(Foo(int_field=10, str_field='foo'))
    '{"intField": 10, "strField": "foo"}'
    """

    def wrap(cls: Type):
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
        g['serde_scope'] = scope
        g['SerdeError'] = SerdeError
        g['raise_unsupported_type'] = raise_unsupported_type
        g['enum_value'] = enum_value
        g['is_dataclass'] = is_dataclass
        g['typename'] = typename  # used in union functions
        g['is_instance'] = is_instance  # used in union functions

        # Collect types used in the generated code.
        for typ in iter_types(cls):
            if is_dataclass(typ) or is_enum(typ) or not is_primitive(typ):
                scope.types[typ.__name__] = typ

        # render all union functions
        for union in iter_unions(cls):
            union_args = type_args(union)
            union_key = union_func_name(UNION_SE_PREFIX, union_args)
            add_func(scope, union_key, render_union_func(cls, union_args), g)
            scope.union_se_args[union_key] = union_args

        for f in sefields(cls):
            if f.skip_if:
                g[f.skip_if.name] = f.skip_if

        add_func(scope, TO_ITER, render_to_tuple(cls), g)
        add_func(scope, TO_DICT, render_to_dict(cls, rename_all), g)

        logger.debug(f'{cls.__name__}: {SERDE_SCOPE} {scope}')

        return cls

    if _cls is None:
        return wrap  # type: ignore

    return wrap(_cls)


def is_serializable(instance_or_class: Any) -> bool:
    """
    Test if arg can `serialize`. Arg must be also an instance of class.

    >>> from dataclasses import dataclass
    >>> from serde import serialize, is_serializable
    >>>
    >>> @serialize
    ... @dataclass
    ... class Foo:
    ...     pass
    >>>
    >>> is_serializable(Foo)
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
        return set(thisfunc(e) for e in o)
    elif isinstance(o, dict):
        return {k: thisfunc(v) for k, v in o.items()}

    return o


def astuple(v):
    """
    Convert class with `serialize` to `tuple`.
    """
    return to_tuple(v, reuse_instances=False, convert_sets=False)


def to_tuple(o, reuse_instances: bool = ..., convert_sets: bool = ...) -> Any:
    """
    Convert object into tuple.

    >>> @serialize
    ... @dataclass
    ... class Foo:
    ...     i: int
    >>>
    >>> to_tuple(Foo(10))
    (10,)
    >>>
    >>> to_tuple([Foo(10), Foo(20)])
    [(10,), (20,)]
    >>>
    >>> to_tuple({'a': Foo(10), 'b': Foo(20)})
    {'a': (10,), 'b': (20,)}
    >>>
    >>> to_tuple((Foo(10), Foo(20)))
    ((10,), (20,))
    """
    return to_obj(o, named=False, reuse_instances=reuse_instances, convert_sets=convert_sets)


def asdict(v):
    """
    Convert class with `serialize` to `dict`.
    """
    return to_dict(v, reuse_instances=False, convert_sets=False)


def to_dict(o, reuse_instances: bool = ..., convert_sets: bool = ...) -> Any:
    """
    Convert object into dictionary.

    >>> @serialize
    ... @dataclass
    ... class Foo:
    ...     i: int
    >>>
    >>> to_dict(Foo(10))
    {'i': 10}
    >>>
    >>> to_dict([Foo(10), Foo(20)])
    [{'i': 10}, {'i': 20}]
    >>>
    >>> to_dict({'a': Foo(10), 'b': Foo(20)})
    {'a': {'i': 10}, 'b': {'i': 20}}
    >>>
    >>> to_dict((Foo(10), Foo(20)))
    ({'i': 10}, {'i': 20})
    """
    return to_obj(o, named=True, reuse_instances=reuse_instances, convert_sets=convert_sets)


@dataclass
class SeField(Field):
    parent: Optional['SeField'] = None

    @property
    def varname(self) -> str:
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


sefields = functools.partial(fields, SeField)


def to_arg(f: SeField) -> SeField:
    f.parent = SeField(None, 'obj')  # type: ignore
    return f


def render_to_tuple(cls: Type) -> str:
    template = """
def {{func}}(obj, reuse_instances = {{serde_scope.reuse_instances_default}}, convert_sets = {{serde_scope.convert_sets_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}
  if convert_sets is Ellipsis:
    convert_sets = {{serde_scope.convert_sets_default}}

  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  {# List up all classes used by this class. #}
  {% for name in serde_scope.types.keys() %}
  {{name}} = serde_scope.types['{{name}}']
  {% endfor %}

  res = []
  {% for f in fields -%}
  {% if not f.skip|default(False) %}
  res.append({{f|arg|rvalue()}})
  {% endif -%}
  {% endfor -%}
  return tuple(res)
    """

    renderer = Renderer(TO_ITER)
    env = jinja2.Environment(loader=jinja2.DictLoader({'iter': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_arg})
    return env.get_template('iter').render(func=TO_ITER, serde_scope=getattr(cls, SERDE_SCOPE), fields=sefields(cls))


def render_to_dict(cls: Type, case: Optional[str] = None) -> str:
    template = """
def {{func}}(obj, reuse_instances = {{serde_scope.reuse_instances_default}}, convert_sets = {{serde_scope.convert_sets_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}
  if convert_sets is Ellipsis:
    convert_sets = {{serde_scope.convert_sets_default}}

  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  {# List up all classes used by this class. #}
  {% for name in serde_scope.types.keys() -%}
  {{name}} = serde_scope.types['{{name}}']
  {% endfor -%}

  res = {}
  {% for f in fields -%}

  {% if not f.skip -%}
    {% if f.skip_if -%}
  if not {{f.skip_if.name}}({{f|arg|rvalue()}}):
    res["{{f|case}}"] = {{f|arg|rvalue()}}
    {% else -%}
  res["{{f|case}}"] = {{f|arg|rvalue()}}
    {% endif -%}
  {% endif %}

  {% endfor -%}
  return res
    """
    renderer = Renderer(TO_DICT)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_arg})
    env.filters.update({'case': functools.partial(conv, case=case)})
    return env.get_template('dict').render(func=TO_DICT, serde_scope=getattr(cls, SERDE_SCOPE), fields=sefields(cls))


def render_union_func(cls: Type, union_args: List[Type]) -> str:
    template = """
def {{func}}(obj, reuse_instances):
  {% for name in serde_scope.types.keys() %}
  {{name}} = serde_scope.types['{{name}}']
  {% endfor %}

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
    return env.get_template('dict').render(
        func=union_func_name(UNION_SE_PREFIX, union_args),
        serde_scope=getattr(cls, SERDE_SCOPE),
        union_args=union_args,
        union_name=union_name,
    )


@dataclass
class Renderer:
    """
    Render rvalue for various types.
    """

    func: str

    def render(self, arg: SeField) -> str:
        """
        Render rvalue

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
        "{k: v.__serde__.funcs['to_iter'](v, reuse_instances=reuse_instances, convert_sets=convert_sets) for k, v in foo.items()}"

        >>> Renderer(TO_ITER).render(SeField(Dict[Foo, Foo], 'foo'))
        "{k.__serde__.funcs['to_iter'](k, reuse_instances=reuse_instances, convert_sets=convert_sets): v.__serde__.funcs['to_iter'](v, reuse_instances=reuse_instances, convert_sets=convert_sets) for k, v in foo.items()}"

        >>> Renderer(TO_ITER).render(SeField(Tuple[str, Foo, int], 'foo'))
        "(foo[0], foo[1].__serde__.funcs['to_iter'](foo[1], reuse_instances=reuse_instances, convert_sets=convert_sets), foo[2])"
        """
        if is_dataclass(arg.type):
            return self.dataclass(arg)
        elif is_opt(arg.type):
            return self.opt(arg)
        elif is_list(arg.type):
            return self.list(arg)
        elif is_set(arg.type):
            return self.set(arg)
        elif is_dict(arg.type):
            return self.dict(arg)
        elif is_tuple(arg.type):
            return self.tuple(arg)
        elif is_enum(arg.type):
            return self.enum(arg)
        elif is_primitive(arg.type):
            return self.primitive(arg)
        elif is_union(arg.type):
            return self.union_func(arg)
        elif arg.type in [
            Decimal,
            Path,
            PosixPath,
            WindowsPath,
            PurePath,
            PurePosixPath,
            PureWindowsPath,
            UUID,
            IPv4Address,
            IPv6Address,
            IPv4Network,
            IPv6Network,
            IPv4Interface,
            IPv6Interface,
        ]:
            return f"{arg.varname} if reuse_instances else {self.str(arg)}"
        elif arg.type in [date, datetime]:
            return f"{arg.varname} if reuse_instances else {arg.varname}.isoformat()"
        elif is_none(arg.type):
            return "None"
        else:
            return f"raise_unsupported_type({arg.varname})"

    def dataclass(self, arg: SeField) -> str:
        """
        Render rvalue for dataclass.
        """
        return f"{arg.varname}.{SERDE_SCOPE}.funcs['{self.func}']({arg.varname}, reuse_instances=reuse_instances, convert_sets=convert_sets)"

    def opt(self, arg: SeField) -> str:
        """
        Render rvalue for optional.
        """
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
            return f'[{self.render(earg)} for v in {arg.varname}] if convert_sets else set({self.render(earg)} for v in {arg.varname})'

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
            return f"({', '.join(rvalues)})"

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

    def str(self, arg: SeField) -> str:
        return f"str({arg.varname})"

    def union_func(self, arg: SeField) -> str:
        func_name = union_func_name(UNION_SE_PREFIX, type_args(arg.type))
        return f"serde_scope.funcs['{func_name}']({arg.varname}, reuse_instances)"


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
