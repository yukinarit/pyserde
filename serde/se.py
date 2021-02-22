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

from .compat import (is_bare_dict, is_bare_list, is_bare_tuple, is_dict, is_enum, is_list, is_opt, is_primitive,
                     is_tuple, is_union, iter_types, type_args, typename, is_none, is_set, is_bare_set)
from .core import (HIDDEN_NAME, SETTINGS, TO_DICT, TO_ITER, Field, Hidden, SerdeError, T, conv, fields, gen, logger,
                   UNION_SE_PREFIX, union_func_suffix, UNION_ARGS, is_instance)
from .more_types import serialize as custom

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
    _cls=None,
    rename_all: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
):
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

    @functools.wraps(_cls)
    def wrap(cls: Type[T]):
        if not hasattr(cls, HIDDEN_NAME):
            setattr(cls, HIDDEN_NAME, Hidden())

        # Create a scope storage used by serde.
        scope = getattr(cls, '__serde_scope__', None)
        if scope is None:
            scope = {}
            setattr(cls, '__serde_scope__', scope)

        # Collect types used in the gernerated code.
        for typ in iter_types(cls):
            if is_dataclass(typ) or is_enum(typ) or not is_primitive(typ):
                getattr(cls, '__serde_scope__')[typ.__name__] = typ

        g: Dict[str, Any] = {}
        for f in sefields(cls):
            if f.skip_if:
                g[f.skip_if.name] = f.skip_if
            if is_union(f.type):  # render all union functions
                union_args = type_args(f.type)
                union_func_name = f"{UNION_SE_PREFIX}{union_func_suffix(union_args)}"
                cls = se_func(cls, union_func_name, render_union_func(cls, union_args), g)
                scope[f"{union_func_name}{UNION_ARGS}"] = union_args

        logger.debug(f'{cls.__name__}: __serde_scope__ {scope}')

        g['is_dataclass'] = is_dataclass
        g['typename'] = typename  # used in union functions
        g['SerdeError'] = SerdeError  # used in union functions
        g['is_instance'] = is_instance  # used in union functions
        g['__custom_serializer__'] = custom
        g['__serde_enum_value__'] = enum_value

        to_tuple_code = render_to_tuple(cls, reuse_instances_default, convert_sets_default, custom)
        cls = se_func(cls, TO_ITER, to_tuple_code, g)
        to_dict_code = render_to_dict(cls, rename_all, reuse_instances_default, convert_sets_default, custom)
        cls = se_func(cls, TO_DICT, to_dict_code, g)
        return cls

    if _cls is None:
        return wrap

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
    return hasattr(instance_or_class, TO_ITER) or hasattr(instance_or_class, TO_DICT)


def to_obj(o, named: bool, reuse_instances: bool, convert_sets: bool):
    thisfunc = functools.partial(to_obj, named=named, reuse_instances=reuse_instances, convert_sets=convert_sets)
    if o is None:
        return None
    if is_serializable(o):
        if named:
            return getattr(o, TO_DICT)(reuse_instances=reuse_instances, convert_sets=convert_sets)
        else:
            return getattr(o, TO_ITER)(reuse_instances=reuse_instances, convert_sets=convert_sets)
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


def render_to_tuple(
    cls: Type, reuse_instances_default: bool = True, convert_sets_default: bool = False, custom: Custom = None
) -> str:
    template = """
def {{func}}(obj, reuse_instances = {{reuse_instances_default}}, convert_sets = {{convert_sets_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{reuse_instances_default}}
  if convert_sets is Ellipsis:
    convert_sets = {{convert_sets_default}}

  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  serde_scope = getattr(obj, '__serde_scope__')

  {# List up all classes used by this class. -#}
  {% for name in cls.__serde_scope__ -%}
  {{name}} = serde_scope['{{name}}']
  {% endfor -%}

  {% if cls|is_dataclass %}
  res = []
  {% for f in cls|fields -%}
  {% if not f.skip|default(False) -%}
  res.append({{f|arg|rvalue()}})
  {% endif -%}
  {% endfor -%}
  return tuple(res)
  {% endif %}
    """

    renderer = Renderer(TO_ITER, custom)
    env = jinja2.Environment(loader=jinja2.DictLoader({'iter': template}))
    env.filters.update({'fields': sefields})
    env.filters.update({'is_dataclass': is_dataclass})
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_arg})
    return env.get_template('iter').render(
        func=TO_ITER,
        cls=cls,
        reuse_instances_default=reuse_instances_default,
        convert_sets_default=convert_sets_default,
    )


def render_to_dict(
    cls: Type,
    case: Optional[str] = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    custom: Custom = None,
) -> str:
    template = """
def {{func}}(obj, reuse_instances = {{reuse_instances_default}}, convert_sets = {{convert_sets_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{reuse_instances_default}}
  if convert_sets is Ellipsis:
    convert_sets = {{convert_sets_default}}

  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  serde_scope = getattr(obj, '__serde_scope__')

  {# List up all classes used by this class. -#}
  {% for name in cls.__serde_scope__ -%}
  {{name}} = serde_scope['{{name}}']
  {% endfor -%}

  {% if cls|is_dataclass -%}
  res = {}
  {% for f in cls|fields -%}

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
  {% endif -%}
    """
    renderer = Renderer(TO_DICT, custom)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'fields': sefields})
    env.filters.update({'is_dataclass': is_dataclass})
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_arg})
    env.filters.update({'case': functools.partial(conv, case=case)})
    return env.get_template('dict').render(
        func=TO_DICT,
        cls=cls,
        reuse_instances_default=reuse_instances_default,
        convert_sets_default=convert_sets_default,
    )


def render_union_func(cls: Type, union_args: List[Type]) -> str:
    template = """
def {{func}}(serde_scope, obj, reuse_instances):
  {% for name in cls.__serde_scope__ %}
  {{name}} = serde_scope['{{name}}']
  {% endfor %}
  
  union_args = serde_scope['{{func}}{{UNION_ARGS}}']
  
  {% for t in union_args %}
  if is_instance(obj, union_args[{{loop.index0}}]):
    return {{t|arg|rvalue()}}
  {% endfor %}
  raise SerdeError("Can not serialize " + repr(obj) + " of type " + typename(type(obj)) + " for {{union_name}}")
    """
    # TODO handle containers in template
    union_func = f"{UNION_SE_PREFIX}{union_func_suffix(union_args)}"
    union_name = f"Union[{', '.join([typename(a) for a in union_args])}]"

    renderer = Renderer(TO_DICT, None) # FIXME we only need render function
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'arg': lambda x: SeField(x, "obj")})
    env.filters.update({'rvalue': renderer.render})
    return env.get_template('dict').render(func=union_func, union_args=union_args, cls=cls, union_name=union_name, UNION_ARGS=UNION_ARGS)

@dataclass
class Renderer:
    """
    Render rvalue for various types.
    """

    func: str
    custom: Custom = None

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
        'foo.__serde_to_iter__(reuse_instances=reuse_instances, convert_sets=convert_sets)'

        >>> Renderer(TO_ITER).render(SeField(List[Foo], 'foo'))
        '[v.__serde_to_iter__(reuse_instances=reuse_instances, convert_sets=convert_sets) for v in foo]'

        >>> Renderer(TO_ITER).render(SeField(Dict[str, Foo], 'foo'))
        '{k: v.__serde_to_iter__(reuse_instances=reuse_instances, convert_sets=convert_sets) for k, v in foo.items()}'

        >>> Renderer(TO_ITER).render(SeField(Dict[Foo, Foo], 'foo'))
        '{k.__serde_to_iter__(reuse_instances=reuse_instances, convert_sets=convert_sets): v.__serde_to_iter__(reuse_instances=reuse_instances, convert_sets=convert_sets) for k, v in foo.items()}'

        >>> Renderer(TO_ITER).render(SeField(Tuple[str, Foo, int], 'foo'))
        '(foo[0], foo[1].__serde_to_iter__(reuse_instances=reuse_instances, convert_sets=convert_sets), foo[2])'
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
            return f'__custom_serializer__({arg.varname})'

    def dataclass(self, arg: SeField) -> str:
        """
        Render rvalue for dataclass.
        """
        return f'{arg.varname}.{self.func}(reuse_instances=reuse_instances, convert_sets=convert_sets)'

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
        return f'__serde_enum_value__({arg.type.__name__}, {arg.varname})'

    def primitive(self, arg: SeField) -> str:
        """
        Render rvalue for primitives.
        """
        return f'{arg.varname}'

    def str(self, arg: SeField) -> str:
        return f"str({arg.varname})"

    def union_func(self, arg: SeField) -> str:
        return f"{UNION_SE_PREFIX}{union_func_suffix(type_args(arg.type))}(serde_scope, {arg.varname}, reuse_instances)"


def se_func(cls: Type[T], func: str, code: str, g: Dict) -> Type[T]:
    """
    Generate function to serialize into an object.
    """
    # Generate serialize function.
    code = gen(code, g, cls=cls)

    setattr(cls, func, g[func])
    if SETTINGS['debug']:
        hidden = getattr(cls, HIDDEN_NAME)
        hidden.code[func] = code

    return cls


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
