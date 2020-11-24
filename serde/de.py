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
import dataclasses
import functools
from dataclasses import dataclass, is_dataclass
from typing import Any, Callable, Dict, List, Optional, Type

import jinja2

from .compat import (has_default, has_default_factory, is_bare_dict, is_bare_list, is_bare_tuple, is_dict, is_enum,
                     is_list, is_opt, is_primitive, is_tuple, is_union, iter_types, type_args)
from .core import FROM_DICT, FROM_ITER, HIDDEN_NAME, SETTINGS, Field, Hidden, SerdeError, T, conv, fields, gen, logger
from .more_types import deserialize as custom

__all__: List = ['deserialize', 'is_deserializable', 'Deserializer', 'from_dict', 'from_tuple']

Custom = Optional[Callable[['DeField', Any], Any]]


def deserialize(_cls=None, rename_all: Optional[str] = None):
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

    def wrap(cls):
        g: Dict[str, Any] = {}

        # Create hidden object used by serde.
        if not hasattr(cls, HIDDEN_NAME):
            setattr(cls, HIDDEN_NAME, Hidden())

        # Create a scope storage used by serde.

        scope = getattr(cls, '__serde_scope__', None)
        if scope is None:
            scope = {}
            setattr(cls, '__serde_scope__', scope)

        # Set custom deserializer.
        g['__custom_deserializer__'] = custom

        # Collect types used in the gernerated code.
        for typ in iter_types(cls):
            if is_dataclass(typ) or is_enum(typ) or not is_primitive(typ):
                getattr(cls, '__serde_scope__')[typ.__name__] = typ

        # Collect default values and default factories used in the generated code.
        # To avoid name conflicts, name the variables like "__default_<NAME>__".
        for f in dataclasses.fields(cls):
            if has_default(f):
                g[f'__default_{f.name}__'] = f.default
            elif has_default_factory(f):
                g[f'__default_{f.name}__'] = f.default_factory

        logger.debug(f'{cls.__name__}: __serde_scope__ {scope}')

        cls = de_func(cls, FROM_ITER, render_from_iter(cls, custom), g)
        cls = de_func(cls, FROM_DICT, render_from_dict(cls, rename_all, custom), g)
        return cls

    if _cls is None:
        return wrap

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
    return hasattr(instance_or_class, FROM_ITER) or hasattr(instance_or_class, FROM_DICT)


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


def from_obj(c: Type[T], o: Any, de: Type[Deserializer] = None, strict=True, named=True, **opts):
    """
    Deserialize from an object into an instance of the type specified as arg `c`.
    `c` can be either primitive type, `List`, `Tuple`, `Dict` or `deserialize` class.

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
    >>> from_obj(Foo, obj)
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
    >>> from_obj(List[Foo], [{'i': 10}, {'i': 20}])
    [Foo(i=10), Foo(i=20)]
    >>>
    >>> from_obj(Dict[str, Foo], {'foo1': {'i': 10}, 'foo2': {'i': 20}})
    {'foo1': Foo(i=10), 'foo2': Foo(i=20)}
    """
    thisfunc = functools.partial(from_obj, named=named)
    if de:
        o = de.deserialize(o, **opts)
    if o is None:
        v = None
    if is_deserializable(c):
        if named:
            v = from_dict(c, o)
        else:
            v = from_tuple(c, o)
    elif is_opt(c):
        if o is None:
            v = None
        else:
            v = thisfunc(type_args(c)[0], o)
    elif is_union(c):
        v = None
        for typ in type_args(c):
            try:
                v = thisfunc(typ, o)
                break
            except (SerdeError, ValueError):
                pass
    elif is_list(c):
        v = [thisfunc(type_args(c)[0], e) for e in o]
    elif is_tuple(c):
        v = tuple(thisfunc(type_args(c)[i], e) for i, e in enumerate(o))
    elif is_dict(c):
        v = {thisfunc(type_args(c)[0], k): thisfunc(type_args(c)[1], v) for k, v in o.items()}
    else:
        v = o

    return v


def from_dict(cls, o):
    """
    Deserialize from dictionary.
    """
    if is_deserializable(cls):
        return cls.__serde_from_dict__(o)
    else:
        return from_obj(cls, o, named=True)


def from_tuple(cls, o):
    """
    Deserialize from tuple.
    """
    if is_deserializable(cls):
        return cls.__serde_from_iter__(o)
    else:
        return from_obj(cls, o, named=False)


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
        if is_list(self.type) or is_dict(self.type):
            return InnerField(typ, 'v', datavar='v')
        elif is_tuple(self.type):
            return InnerField(typ, f'{self.data}[{n}]', datavar=f'{self.data}[{n}]')
        else:
            return DeField(typ, self.name, datavar=self.datavar, index=self.index, iterbased=self.iterbased)

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
            return f'{self.datavar}["{conv(self, self.case)}"]'

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
    custom: Custom = None

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
        elif is_dict(arg.type):
            res = self.dict(arg)
        elif is_tuple(arg.type):
            res = self.tuple(arg)
        elif is_enum(arg.type):
            res = self.enum(arg)
        elif any(f(arg.type) for f in (is_primitive, is_union)):
            res = self.primitive(arg)
        else:
            return f'__custom_deserializer__({arg.type.__name__}, {arg.data})'

        if has_default(arg) or has_default_factory(arg):
            if arg.iterbased:
                exists = f'{arg.data} is not None'
            else:
                exists = f'{arg.datavar}.get("{arg.name}") is not None'
            if has_default(arg):
                return f'{res} if {exists} else __default_{arg.name}__'
            elif has_default_factory(arg):
                return f'{res} if {exists} else __default_{arg.name}__()'

        return res

    def dataclass(self, arg: DeField) -> str:
        return f'{arg.type.__name__}.{self.func}({arg.data})'

    def opt(self, arg: DeField) -> str:
        """
        Render rvalue for Optional.

        >>> from typing import List
        >>> Renderer('foo').render(DeField(Optional[int], 'o', datavar='data'))
        'data["o"] if data.get("o") is not None else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '[v for v in data["o"]] if data.get("o") is not None else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '[v for v in data["o"]] if data.get("o") is not None else None'

        >>> @deserialize
        ... @dataclass
        ... class Foo:
        ...     o: Optional[List[int]]
        >>> Renderer('foo').render(DeField(Optional[Foo], 'f', datavar='data'))
        'Foo.foo(data["f"]) if data.get("f") is not None else None'
        """
        value = arg[0]
        if has_default(arg):
            return self.render(value)
        else:
            if arg.iterbased:
                exists = f'{arg.data} is not None'
            else:
                exists = f'{arg.datavar}.get("{arg.name}") is not None'
            return f'{self.render(value)} if {exists} else None'

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

    def tuple(self, arg: DeField) -> str:
        """
        Render rvalue for tuple.

        >>> from typing import List, Tuple
        >>> @deserialize
        ... @dataclass
        ... class Foo: pass
        >>> Renderer('foo').render(DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data'))
        '(data["d"][0], data["d"][1], [v for v in data["d"][2]], Foo.foo(data["d"][3]))'

        >>> field = DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data', index=0, iterbased=True)
        >>> Renderer('foo').render(field)
        '(data[0][0], data[0][1], [v for v in data[0][2]], Foo.foo(data[0][3]))'
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
        '{Foo.foo(k): [Foo.foo(v) for v in v] for k, v in data["f"].items()}'
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
        if not arg.iterbased and has_default(arg):
            return f'{arg.datavar}.get("{arg.name}", __default_{arg.name}__)'
        else:
            return arg.data


def to_arg(f: DeField, index, rename_all: Optional[str] = None) -> DeField:
    f.index = index
    f.data = 'data'
    f.case = f.case or rename_all
    return f


def to_iter_arg(f: DeField, *args, **kwargs):
    f = to_arg(f, *args, **kwargs)
    f.iterbased = True
    return f


def render_from_iter(cls: Type, custom: Custom = None) -> str:
    template = """
def {{func}}(data):
  {# List up all classes used by this class. -#}
  {% for name in cls.__serde_scope__ -%}
  {{name}} = getattr(cls, '__serde_scope__')['{{name}}']
  {% endfor -%}

  if data is None:
    return None
  return cls(
  {% for f in cls|fields -%}
  {{f|arg(loop.index-1)|rvalue}},
  {% endfor -%}
  )
    """

    renderer = Renderer(FROM_ITER)
    env = jinja2.Environment(loader=jinja2.DictLoader({'iter': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'fields': defields})
    env.filters.update({'arg': to_iter_arg})
    return env.get_template('iter').render(func=FROM_ITER, cls=cls)


def render_from_dict(cls: Type, rename_all: Optional[str] = None, custom: Custom = None) -> str:
    template = """
def {{func}}(data):
  {# List up all classes used by this class. -#}
  {% for name in cls.__serde_scope__ -%}
  {{name}} = getattr(cls, '__serde_scope__')['{{name}}']
  {% endfor -%}

  if data is None:
    return None
  fs = fields(cls)
  return cls(
  {% for f in cls|fields -%}
  {{f|arg(loop.index-1)|rvalue}},
  {% endfor -%}
  )
    """

    renderer = Renderer(FROM_DICT, custom)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'fields': defields})
    env.filters.update({'arg': functools.partial(to_arg, rename_all=rename_all)})
    return env.get_template('dict').render(func=FROM_DICT, cls=cls)


def de_func(cls: Type[T], func: str, code: str, g: Dict) -> Type[T]:
    """
    Generate function to deserialize into an instance of `deserialize` class.
    """
    g['cls'] = cls
    import typing

    g['typing'] = typing
    g['NoneType'] = type(None)
    g['fields'] = dataclasses.fields

    # Generate deserialize function.
    code = gen(code, g, cls=cls)
    setattr(cls, func, staticmethod(g[func]))
    if SETTINGS['debug']:
        hidden = getattr(cls, HIDDEN_NAME)
        hidden.code[func] = code

    return cls
