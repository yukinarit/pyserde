"""
Defines classess and functions for `deserialize` decorator.

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
from dataclasses import _MISSING_TYPE as DEFAULT_MISSING_TYPE
from dataclasses import dataclass
from dataclasses import fields as dataclass_fields
from dataclasses import is_dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

import jinja2

from .compat import assert_type, is_dict, is_list, is_opt, is_primitive, is_tuple, is_union, iter_types, type_args
from .core import FROM_DICT, FROM_ITER, HIDDEN_NAME, SETTINGS, Field, Hidden, SerdeError, T, conv, fields, gen
from .more_types import deserialize as custom

Custom = Optional[Callable[['DeField', Any], Any]]


def deserialize(_cls=None, rename_all: Optional[str] = None) -> Type:
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
    >>>
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
    >>>
    >>> from_json(RenameAll, '{"intField": 10, "strField": "foo"}')
    RenameAll(int_field=10, str_field='foo')
    >>>
    """

    def wrap(cls):
        g: Dict[str, Any] = globals().copy()
        if not hasattr(cls, HIDDEN_NAME):
            setattr(cls, HIDDEN_NAME, Hidden())
        g['__custom_deserializer__'] = custom
        cls = de_func(cls, FROM_ITER, render_from_iter(cls, custom), g)
        cls = de_func(cls, FROM_DICT, render_from_dict(cls, rename_all, custom), g)
        return cls

    if _cls is None:
        return wrap

    return wrap(_cls)


def is_deserializable(instance_or_class: Any) -> bool:
    """
    Test if arg can `deserialize`. Arg must be either an instance of class.

    >>> from serde import deserialize, is_deserializable
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Foo:
    ...     pass
    >>>
    >>> is_deserializable(Foo)
    True
    >>>
    """
    return hasattr(instance_or_class, FROM_ITER) or hasattr(instance_or_class, FROM_DICT)


class Deserializer(metaclass=abc.ABCMeta):
    """
    `Deserializer` base class. Subclass this to custonize deserialize bahaviour.

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


def from_obj(c: Type[T], o: Any, de: Type[Deserializer] = None, strict=True, **opts):
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
    >>>
    """
    if de:
        o = de.deserialize(o, **opts)
    if o is None:
        v = None
    if is_deserializable(c):
        v = from_dict_or_iter(c, o)
    elif is_opt(c):
        if o is None:
            v = None
        else:
            v = from_obj(type_args(c)[0], o)
    elif is_union(c):
        v = None
        for typ in type_args(c):
            try:
                v = from_obj(typ, o)
                break
            except (SerdeError, ValueError):
                pass
    elif is_list(c):
        assert_type(list, o, strict)
        v = [from_obj(type_args(c)[0], e) for e in o]
    elif is_tuple(c):
        assert_type(tuple, o, strict)
        v = tuple(from_obj(type_args(c)[i], e) for i, e in enumerate(o))
    elif is_dict(c):
        assert_type(dict, o, strict)
        v = {from_obj(type_args(c)[0], k): from_obj(type_args(c)[1], v) for k, v in o.items()}
    else:
        v = o

    return v


def from_dict_or_iter(cls, o):
    """
    Deserialize into an instance of `deserialize` class from either `dict` or `iterable`.
    """
    if not is_deserializable(cls):
        raise SerdeError('`cls` must be deserializable.')

    if isinstance(o, (List, Tuple)):
        return cls.__serde_from_iter__(o)
    elif isinstance(o, Dict):
        return cls.__serde_from_dict__(o)
    elif isinstance(o, cls) or o is None:
        return o
    else:
        raise SerdeError(f'Arg must be either List, Tuple, Dict or Type but {type(o)}.')


def from_dict(cls, o):
    return cls.__serde_from_dict__(o)


def from_tuple(cls, o):
    return cls.__serde_from_iter__(o)


@dataclass
class DeField(Field):
    datavar: Optional[str] = None  # name of variable to deserialize from.
    index: int = 0  # Field number inside dataclass.
    parent: Optional['DeField'] = None  # Parent of this field.
    iterbased: bool = False  # Iterater based deserializer or not.

    def __getitem__(self, n) -> 'DeField':
        typ = type_args(self.type)[n]
        if is_list(self.type) or is_dict(self.type):
            return ElementField(typ, 'v', datavar='v')
        elif is_tuple(self.type):
            return ElementField(typ, f'{self.data}[{n}]', datavar=f'{self.data}[{n}]')
        else:
            return DeField(typ, self.name, datavar=self.datavar, index=self.index, iterbased=self.iterbased)

    def get_kv(self) -> Tuple['ElementField', 'ElementField']:
        k = self[0]
        k.name = 'k'
        k.datavar = 'k'
        v = self[1]
        return (k, v)

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
class ElementField(DeField):
    """
    Field for element type such as List[T].
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
            return self.dataclass(arg)
        elif is_opt(arg.type):
            return self.opt(arg)
        elif is_list(arg.type):
            return self.list(arg)
        elif is_dict(arg.type):
            return self.dict(arg)
        elif is_tuple(arg.type):
            return self.tuple(arg)
        elif any(f(arg.type) for f in (is_primitive, is_union)):
            return self.primitive(arg)
        else:
            return f'__custom_deserializer__(fs[{arg.index}], {arg.data})'

    def dataclass(self, arg: DeField) -> str:
        return f'{arg.type.__name__}.{self.func}({arg.data})'

    def opt(self, arg: DeField) -> str:
        """
        Render rvalue for Optional.

        >>> Renderer('foo').render(DeField(Optional[int], 'o', datavar='data'))
        'data["o"] if "o" in data else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '[v for v in data["o"]] if "o" in data else None'

        >>> Renderer('foo').render(DeField(Optional[List[int]], 'o', datavar='data'))
        '[v for v in data["o"]] if "o" in data else None'

        >>> @deserialize
        ... @dataclass
        ... class Foo:
        ...     o: Optional[List[int]]
        >>> Renderer('foo').render(DeField(Optional[Foo], 'f', datavar='data'))
        'Foo.foo(data["f"]) if "f" in data else None'
        """
        value = arg[0]
        if arg.iterbased:
            exists = f'{value.data} is not None'
            return f'{self.render(value)} if {exists} else None'
        else:
            exists = f'"{value.name}" in {value.datavar}'
            return f'{self.render(value)} if {exists} else None'

    def list(self, arg: DeField) -> str:
        """
        Render rvalue for list.

        >>> Renderer('foo').render(DeField(List[int], 'l', datavar='data'))
        '[v for v in data["l"]]'

        >>> Renderer('foo').render(DeField(List[List[int]], 'l', datavar='data'))
        '[[v for v in v] for v in data["l"]]'
        """
        return f'[{self.render(arg[0])} for v in {arg.data}]'

    def tuple(self, arg: DeField) -> str:
        """
        Render rvalue for tuple.

        >>> @deserialize
        ... @dataclass
        ... class Foo: pass
        >>> Renderer('foo').render(DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data'))
        '(data["d"][0], data["d"][1], [v for v in data["d"][2]], Foo.foo(data["d"][3]))'

        >>> Renderer('foo').render(DeField(Tuple[str, int, List[int], Foo], 'd', datavar='data', index=0, iterbased=True))
        '(data[0][0], data[0][1], [v for v in data[0][2]], Foo.foo(data[0][3]))'
        """
        values = []
        for i, typ in enumerate(type_args(arg.type)):
            inner = arg[i]
            values.append(self.render(inner))
        return f'({", ".join(values)})'

    def dict(self, arg: DeField) -> str:
        """
        Render rvalue for dict.

        >>> Renderer('foo').render(DeField(Dict[str, int], 'd', datavar='data'))
        '{k: v for k, v in data["d"].items()}'

        >>> @deserialize
        ... @dataclass
        ... class Foo: pass
        >>> Renderer('foo').render(DeField(Dict[Foo, List[Foo]], 'f', datavar='data'))
        '{Foo.foo(k): [Foo.foo(v) for v in v] for k, v in data["f"].items()}'
        """
        k, v = arg.get_kv()
        return f'{{{self.render(k)}: {self.render(v)} for k, v in {arg.data}.items()}}'

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
        if not arg.iterbased and not isinstance(arg.default, DEFAULT_MISSING_TYPE):
            default = arg.default
            if isinstance(default, str):
                default = f'"{default}"'
            return f'{arg.datavar}.get("{arg.name}", {default})'
        else:
            return arg.data


def to_arg(f: DeField, index, rename_all: Optional[str] = None) -> DeField:
    f.index = index
    f.data = 'data'
    f.parent = DeField(type(None), 'data', datavar='data', case=f.case or rename_all)
    f.case = f.case or rename_all
    return f


def to_iter_arg(f: DeField, *args, **kwargs):
    f = to_arg(f, *args, **kwargs)
    f.iterbased = True
    return f


def render_from_iter(cls: Type, custom: Custom = None) -> str:
    template = """
def {{func}}(data):
  if data is None:
    return None
  return cls(
  {% for f in cls|fields %}
  {{f|arg(loop.index-1)|rvalue}},
  {% endfor %}
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
  if data is None:
    return None
  fs = fields(cls)
  return cls(
  {% for f in cls|fields %}
  {{f|arg(loop.index-1)|rvalue}},
  {% endfor %}
  )
    """

    renderer = Renderer(FROM_DICT, custom)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'fields': defields})
    env.filters.update({'arg': functools.partial(to_arg, rename_all=rename_all)})
    return env.get_template('dict').render(func=FROM_DICT, cls=cls)


def de_func(cls: Type[T], func: str, code: str, g: Dict = None, local: Dict = None) -> Type[T]:
    """
    Generate function to deserialize into an instance of `deserialize` class.
    """
    if not g:
        g = globals().copy()
    if not local:
        local = locals().copy()

    # Collect types to be used in the `exec` scope.
    for typ in iter_types(cls):
        if is_dataclass(typ):
            g[typ.__name__] = typ
    g['cls'] = cls
    import typing

    g['typing'] = typing
    g['NoneType'] = type(None)
    g['fields'] = dataclass_fields

    # Generate deserialize function.
    code = gen(code, g, cls=cls)
    setattr(cls, func, staticmethod(g[func]))
    if SETTINGS['debug']:
        hidden = getattr(cls, HIDDEN_NAME)
        hidden.code[func] = code

    return cls
