"""
Defines classes and functions for `deserialize` decorator.

`deserialize` is a decorator to make a `dataclasses.dataclass` class deserializable.
`is_deserializable` is used to test a class is with `deserialize`.
`Deserializer` is a deserializer base class used in `from_obj`,
`serde.json.from_json`. You can subclass it to make your own deserializer.
`from_obj` deserializes from an object into an instance of the class with
`deserialize`.

`args_from_iter` and `args_from_dict` are private functions but they are the core
parts of pyserde.
"""
import abc
import functools
import sys
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
    has_default,
    has_default_factory,
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
    FROM_DICT,
    FROM_ITER,
    SERDE_SCOPE,
    UNION_DE_PREFIX,
    Field,
    SerdeError,
    SerdeScope,
    add_func,
    fields,
    logger,
    raise_unsupported_type,
    union_func_name,
)
from .py36_datetime_compat import py36_date_fromisoformat, py36_datetime_fromisoformat

__all__: List = ['deserialize', 'is_deserializable', 'Deserializer', 'from_dict', 'from_tuple']

Custom = Optional[Callable[['DeField', Any], Any]]


def deserialize(
    _cls: Type[T] = None, rename_all: Optional[str] = None, reuse_instances_default: bool = True
) -> Type[T]:
    """
    `deserialize` decorator. A dataclass with this decorator can be deserialized
    into an object from various data format such as JSON and MsgPack.

    >>> from serde import deserialize
    >>> from serde.json import from_json
    >>>
    >>> # Mark the class deserializable.
    >>> @deserialize
    ... @dataclass
    ... class Foo:
    ...     i: int
    ...     s: str
    ...     f: float
    ...     b: bool
    >>> from_json(Foo, '{"i": 10, "s": "foo", "f": 100.0, "b": true}')
    Foo(i=10, s='foo', f=100.0, b=True)

    Additionally, `deserialize` supports case conversion. Pass case name in
    `deserialize` decorator as shown below.

    >>> from serde import deserialize
    >>>
    >>> @deserialize(rename_all = 'camelcase')
    ... @dataclass
    ... class RenameAll:
    ...     int_field: int
    ...     str_field: str
    >>> from_json(RenameAll, '{"intField": 10, "strField": "foo"}')
    RenameAll(int_field=10, str_field='foo')
    """

    def wrap(cls: Type):
        g: Dict[str, Any] = {}

        # Create a scope storage used by serde.
        # Each class should get own scope. Child classes can not share scope with parent class.
        # That's why we need the "scope.cls is not cls" check.
        scope: SerdeScope = getattr(cls, SERDE_SCOPE, None)
        if scope is None or scope.cls is not cls:
            scope = SerdeScope(cls, reuse_instances_default=reuse_instances_default)
            setattr(cls, SERDE_SCOPE, scope)

        # Set some globals for all generated functions
        g['cls'] = cls
        g['serde_scope'] = scope
        g['SerdeError'] = SerdeError
        g['raise_unsupported_type'] = raise_unsupported_type
        g['typename'] = typename  # used in union functions

        # Collect types used in the generated code.
        for typ in iter_types(cls):
            if is_dataclass(typ) or is_enum(typ) or not is_primitive(typ):
                scope.types[typ.__name__] = typ

            # python 3.6 has no fromisoformat functions for date & datetime, so we have to add our own.
            # See Renderer.render for usage
            if sys.version_info[:2] == (3, 6):
                if typ is date:
                    g['__py36_date_fromisoformat__'] = py36_date_fromisoformat
                elif typ is datetime:
                    g['__py36_datetime_fromisoformat__'] = py36_datetime_fromisoformat

        # render all union functions
        for union in iter_unions(cls):
            union_args = type_args(union)
            add_func(scope, union_func_name(UNION_DE_PREFIX, union_args), render_union_func(cls, union_args), g)

        # Collect default values and default factories used in the generated code.
        for f in defields(cls):
            if has_default(f):
                scope.defaults[f.name] = f.default
            elif has_default_factory(f):
                scope.defaults[f.name] = f.default_factory

        add_func(scope, FROM_ITER, render_from_iter(cls), g)
        add_func(scope, FROM_DICT, render_from_dict(cls, rename_all), g)

        logger.debug(f'{cls.__name__}: {SERDE_SCOPE} {scope}')

        return cls

    if _cls is None:
        return wrap  # type: ignore

    return wrap(_cls)


def is_deserializable(instance_or_class: Any) -> bool:
    """
    Test if arg can `deserialize`. Arg must be also an instance of class.

    >>> from serde import deserialize, is_deserializable
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Foo:
    ...     pass
    >>>
    >>> is_deserializable(Foo)
    True
    """
    return hasattr(instance_or_class, SERDE_SCOPE)


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


def from_obj(c: Type, o: Any, named: bool, reuse_instances: bool):
    """
    Deserialize from an object into an instance of the type specified as arg `c`.
    `c` can be either primitive type, `List`, `Tuple`, `Dict` or `deserialize` class.
    """
    thisfunc = functools.partial(from_obj, named=named, reuse_instances=reuse_instances)
    if o is None:
        return None
    if is_deserializable(c):
        serde_scope: SerdeScope = getattr(c, SERDE_SCOPE)
        if named:
            return serde_scope.funcs[FROM_DICT](o, reuse_instances=reuse_instances)
        else:
            return serde_scope.funcs[FROM_ITER](o, reuse_instances=reuse_instances)
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
    elif is_list(c) or is_set(c):
        return [thisfunc(type_args(c)[0], e) for e in o]
    elif is_tuple(c):
        return tuple(thisfunc(type_args(c)[i], e) for i, e in enumerate(o))
    elif is_dict(c):
        return {thisfunc(type_args(c)[0], k): thisfunc(type_args(c)[1], v) for k, v in o.items()}

    return o


def from_dict(cls, o, reuse_instances: bool = ...):
    """
    Deserialize from dictionary.

    ### Dataclass

    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Foo:
    ...     i: int
    ...     f: float
    ...     s: str
    ...     b: bool
    >>>
    >>> obj = {'i': 10, 'f': 0.1, 's': 'foo', 'b': False}
    >>> from_dict(Foo, obj)
    Foo(i=10, f=0.1, s='foo', b=False)

    ### Containers

    >>> from serde import deserialize
    >>> from typing import List
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Foo:
    ...     i: int
    >>>
    >>> from_dict(List[Foo], [{'i': 10}, {'i': 20}])
    [Foo(i=10), Foo(i=20)]
    >>>
    >>> from_dict(Dict[str, Foo], {'foo1': {'i': 10}, 'foo2': {'i': 20}})
    {'foo1': Foo(i=10), 'foo2': Foo(i=20)}
    """
    return from_obj(cls, o, named=True, reuse_instances=reuse_instances)


def from_tuple(cls, o, reuse_instances: bool = ...):
    """
    Deserialize from tuple.
    """
    return from_obj(cls, o, named=False, reuse_instances=reuse_instances)


@dataclass
class DeField(Field):
    """
    Feild class for deserialization.
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
        else:
            return f'{self.datavar}["{self.conv_name}"]'

    @data.setter
    def data(self, d):
        self.datavar = d


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
    Render rvalue for various types.
    """

    func: str

    def render(self, arg: DeField) -> str:
        """
        Render rvalue
        """
        if is_dataclass(arg.type):
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
            res = f"({self.c_tor_with_check(arg)}) if reuse_instances else {self.c_tor(arg)}"
        elif arg.type in [date, datetime]:
            from_iso = f"{arg.type.__name__}.fromisoformat({arg.data})"

            if sys.version_info[:2] == (3, 6):  # python 3.6 has no fromisoformat functions
                if arg.type is date:
                    from_iso = f"__py36_date_fromisoformat__({arg.data})"
                elif arg.type is datetime:
                    from_iso = f"__py36_datetime_fromisoformat__({arg.data})"

            res = f"({arg.data} if isinstance({arg.data}, {arg.type.__name__}) else {from_iso}) if reuse_instances else {from_iso}"
        elif is_none(arg.type):
            res = "None"
        else:
            return f"raise_unsupported_type({arg.data})"

        if has_default(arg) or has_default_factory(arg):
            if arg.iterbased:
                exists = f'{arg.data} is not None'
            else:
                exists = f'{arg.datavar}.get("{arg.conv_name}") is not None'
            if has_default(arg):
                res = f'({res}) if {exists} else serde_scope.defaults["{arg.name}"]'
            elif has_default_factory(arg):
                res = f'({res}) if {exists} else serde_scope.defaults["{arg.name}"]()'

        return res

    def dataclass(self, arg: DeField) -> str:
        return f"{arg.type.__name__}.{SERDE_SCOPE}.funcs['{self.func}']({arg.data}, reuse_instances=reuse_instances)"

    def opt(self, arg: DeField) -> str:
        """
        Render rvalue for Optional.

        >>> from typing import List
        >>> Renderer('foo').render(DeField(Optional[int], 'o', datavar='data'))
        '(data["o"]) if data.get("o") is not None else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '([v for v in data["o"]]) if data.get("o") is not None else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '([v for v in data["o"]]) if data.get("o") is not None else None'

        >>> @deserialize
        ... @dataclass
        ... class Foo:
        ...     o: Optional[List[int]]
        >>> Renderer('foo').render(DeField(Optional[Foo], 'f', datavar='data'))
        '(Foo.__serde__.funcs[\\'foo\\'](data["f"], reuse_instances=reuse_instances)) if data.get("f") is not None else None'
        """
        value = arg[0]
        if has_default(arg):
            return self.render(value)
        else:
            if arg.iterbased:
                exists = f'{arg.data} is not None'
            else:
                exists = f'{arg.datavar}.get("{arg.conv_name}") is not None'
            return f'({self.render(value)}) if {exists} else None'

    def list(self, arg: DeField) -> str:
        """
        Render rvalue for list.

        >>> from typing import List
        >>> Renderer('foo').render(DeField(List[int], 'l', datavar='data'))
        '[v for v in data["l"]]'

        >>> Renderer('foo').render(DeField(List[List[int]], 'l', datavar='data'))
        '[[v for v in v] for v in data["l"]]'
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
        'set(v for v in data["l"])'

        >>> Renderer('foo').render(DeField(Set[Set[int]], 'l', datavar='data'))
        'set(set(v for v in v) for v in data["l"])'
        """
        if is_bare_set(arg.type):
            return f'set({arg.data})'
        else:
            return f'set({self.render(arg[0])} for v in {arg.data})'

    def tuple(self, arg: DeField) -> str:
        """
        Render rvalue for tuple.

        >>> from typing import List, Tuple
        >>> @deserialize
        ... @dataclass
        ... class Foo: pass
        >>> Renderer('foo').render(DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data'))
        '(data["d"][0], data["d"][1], [v for v in data["d"][2]], Foo.__serde__.funcs[\\'foo\\'](data["d"][3], reuse_instances=reuse_instances))'

        >>> field = DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data', index=0, iterbased=True)
        >>> Renderer('foo').render(field)
        "(data[0][0], data[0][1], [v for v in data[0][2]], Foo.__serde__.funcs['foo'](data[0][3], reuse_instances=reuse_instances))"
        """
        if is_bare_tuple(arg.type):
            return f'tuple({arg.data})'
        else:
            values = []
            for i, typ in enumerate(type_args(arg.type)):
                inner = arg[i]
                values.append(self.render(inner))
            return f'({", ".join(values)})'

    def dict(self, arg: DeField) -> str:
        """
        Render rvalue for dict.

        >>> from typing import List
        >>> Renderer('foo').render(DeField(Dict[str, int], 'd', datavar='data'))
        '{k: v for k, v in data["d"].items()}'

        >>> @deserialize
        ... @dataclass
        ... class Foo: pass
        >>> Renderer('foo').render(DeField(Dict[Foo, List[Foo]], 'f', datavar='data'))
        '{Foo.__serde__.funcs[\\'foo\\'](k, reuse_instances=reuse_instances): [Foo.__serde__.funcs[\\'foo\\'](v, reuse_instances=reuse_instances) for v in v] for k, v in data["f"].items()}'
        """
        if is_bare_dict(arg.type):
            return arg.data
        else:
            k = arg.key_field()
            v = arg.value_field()
            return f'{{{self.render(k)}: {self.render(v)} for k, v in {arg.data}.items()}}'

    def enum(self, arg: DeField) -> str:
        return f'{arg.type.__name__}({self.primitive(arg)})'

    def primitive(self, arg: DeField) -> str:
        """
        Render rvalue for primitives.

        >>> Renderer('foo').render(DeField(int, 'i', datavar='data'))
        'data["i"]'

        >>> Renderer('foo').render(DeField(int, 'int_field', datavar='data', case='camelcase'))
        'data["intField"]'

        >>> Renderer('foo').render(DeField(int, 'i', datavar='data', index=1, iterbased=True))
        'data[1]'
        """
        return arg.data

    def c_tor(self, arg: DeField) -> str:
        return f"{arg.type.__name__}({arg.data})"

    def c_tor_with_check(self, arg: DeField, ctor: Optional[str] = None) -> str:
        if ctor is None:
            ctor = self.c_tor(arg)
        return f"{arg.data} if isinstance({arg.data}, {arg.type.__name__}) else {ctor}"

    def union_func(self, arg: DeField) -> str:
        func_name = union_func_name(UNION_DE_PREFIX, type_args(arg.type))
        return f"serde_scope.funcs['{func_name}']({arg.data}, reuse_instances)"


def to_arg(f: DeField, index, rename_all: Optional[str] = None) -> DeField:
    f.index = index
    f.data = 'data'
    f.case = f.case or rename_all
    return f


def to_iter_arg(f: DeField, *args, **kwargs) -> DeField:
    f = to_arg(f, *args, **kwargs)
    f.iterbased = True
    return f


def render_from_iter(cls: Type) -> str:
    template = """
def {{func}}(data, reuse_instances = {{serde_scope.reuse_instances_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}

  {# List up all classes used by this class. -#}
  {% for name in serde_scope.types.keys() -%}
  {{name}} = serde_scope.types['{{name}}']
  {% endfor -%}

  if data is None:
    return None

  return cls(
  {% for f in fields %}
  {{f|arg(loop.index-1)|rvalue}},
  {% endfor %}
  )
    """

    renderer = Renderer(FROM_ITER)
    env = jinja2.Environment(loader=jinja2.DictLoader({'iter': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_iter_arg})
    return env.get_template('iter').render(func=FROM_ITER, serde_scope=getattr(cls, SERDE_SCOPE), fields=defields(cls))


def render_from_dict(cls: Type, rename_all: Optional[str] = None) -> str:
    template = """
def {{func}}(data, reuse_instances = {{serde_scope.reuse_instances_default}}):
  if reuse_instances is Ellipsis:
    reuse_instances = {{serde_scope.reuse_instances_default}}

  {# List up all classes used by this class. #}
  {% for name in serde_scope.types.keys() %}
  {{name}} = serde_scope.types['{{name}}']
  {% endfor %}

  if data is None:
    return None

  return cls(
  {% for f in fields %}
  {{f|arg(loop.index-1)|rvalue}},
  {% endfor %}
  )
    """

    renderer = Renderer(FROM_DICT)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': functools.partial(to_arg, rename_all=rename_all)})
    return env.get_template('dict').render(func=FROM_DICT, serde_scope=getattr(cls, SERDE_SCOPE), fields=defields(cls))


def render_union_func(cls: Type, union_args: List[Type]) -> str:
    template = """
def {{func}}(data, reuse_instances):
  {% for name in serde_scope.types.keys() %}
  {{name}} = serde_scope.types['{{name}}']
  {% endfor %}

  # create fake dict so we can reuse the normal render function
  fake_dict = {"fake_key":data}

  error = "Exhausted all types"
  {% for t in union_args %}
  {% if t | is_primitive or t | is_none %}
  if isinstance(data, {{t.__name__}}):
    return {{t|arg|rvalue}}
  else:
    error = "input is not of type {{t.__name__}}"
  {% else %}
  try:
    return {{t|arg|rvalue}}
  except Exception as e:
    error = str(e)
  {% endif %}
  {% endfor %}
  raise SerdeError("Can not deserialize " + repr(data) + " of type " + typename(type(data)) + " into {{union_name}}. Reason: " + error)
    """
    union_name = f"Union[{', '.join([typename(a) for a in union_args])}]"

    renderer = Renderer(FROM_DICT)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update(
        {'arg': lambda x: DeField(x, datavar="fake_dict", name="fake_key")}
    )  # use custom to_arg for fake field
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'is_primitive': is_primitive})
    env.filters.update({'is_none': is_none})
    return env.get_template('dict').render(
        func=union_func_name(UNION_DE_PREFIX, union_args),
        serde_scope=getattr(cls, SERDE_SCOPE),
        union_args=union_args,
        union_name=union_name,
    )
