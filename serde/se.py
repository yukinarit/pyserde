"""
Defines classess and functions for `serialize` decorator.

"""
import abc
import copy  # noqa
import functools
from dataclasses import Field as DataclassField
from dataclasses import asdict as _asdict
from dataclasses import astuple as _astuple
from dataclasses import dataclass
from dataclasses import fields as dataclass_fields  # noqa
from dataclasses import is_dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

import jinja2
import stringcase

from .compat import is_dict, is_list, is_opt, is_primitive, is_tuple, is_union, type_args
from .core import HIDDEN_NAME, SE_NAME, SETTINGS, TO_DICT, TO_ITER, Field, Hidden, T, conv, fields, gen
from .more_types import serialize as custom

Custom = Optional[Callable[[Any], Any]]


class Serializer(metaclass=abc.ABCMeta):
    """
    `Serializer` base class. Subclass this to custonize serialize bahaviour.

    See `serde.json.JsonSerializer` and `serde.msgpack.MsgPackSerializer` for example usage.
    """

    @abc.abstractclassmethod
    def serialize(cls, obj):
        pass


def serialize(_cls=None, rename_all: Optional[str] = None) -> Type:
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
    >>>

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
    >>>
    """

    @functools.wraps(_cls)
    def wrap(cls: Type[T]) -> Type[T]:
        if not hasattr(cls, HIDDEN_NAME):
            setattr(cls, HIDDEN_NAME, Hidden())

        def serialize(self, ser, **opts) -> None:
            return ser.serialize(self, **opts)

        setattr(cls, SE_NAME, serialize)

        g: Dict[str, Any] = globals().copy()
        for f in sefields(cls):
            if f.skip_if:
                g[f.skip_if.mangled] = f.skip_if
        g['__custom_serializer__'] = custom
        cls = se_func(cls, TO_ITER, render_astuple(cls, custom), g)
        cls = se_func(cls, TO_DICT, render_asdict(cls, rename_all, custom), g)
        return cls

    if _cls is None:
        return wrap

    return wrap(_cls)


def is_serializable(instance_or_class: Any) -> bool:
    """
    Test if arg can `serialize`. Arg must be either an instance of class.

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
    >>>
    """
    return hasattr(instance_or_class, '__serde_serialize__')


def to_dict(o) -> Dict:
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
    if o is None:
        v = None
    if is_serializable(o):
        v = asdict(o)
    elif isinstance(o, list):
        v = [to_dict(e) for e in o]
    elif isinstance(o, tuple):
        v = tuple(to_dict(e) for e in o)
    elif isinstance(o, dict):
        v = {k: to_dict(v) for k, v in o.items()}
    else:
        v = o

    return v


def astuple(v):
    """
    Convert `serialize` class to `tuple`.
    """
    if is_serializable(v):
        return getattr(v, TO_ITER)()
    elif is_dataclass(v):
        return _astuple(v)
    elif isinstance(v, Dict):
        return tuple(astuple(e) for e in v.values())
    elif isinstance(v, (Tuple, List)):
        return tuple(astuple(e) for e in v)
    else:
        return v


def asdict(v):
    """
    Convert `serialize` class to `dict`.
    """
    if is_serializable(v):
        return getattr(v, TO_DICT)()
    elif is_dataclass(v):
        return _asdict(v)
    elif isinstance(v, Dict):
        return {asdict(k): asdict(v) for k, v in v.items()}
    elif isinstance(v, (Tuple, List)):
        return tuple(asdict(e) for e in v)
    else:
        return v


@dataclass
class SeField(Field):
    parent: Optional['Field'] = None

    @property
    def varname(self) -> str:
        var = self.parent.varname if self.parent else None
        if var:
            return f'{var}.{self.name}'
        else:
            return self.name

    def __getitem__(self, n) -> 'SeField':
        typ = type_args(self.type)[n]
        return SeField(typ, None)

    @staticmethod
    def mangle(field: DataclassField, name: str) -> str:
        return f'{field.name}_{name}'


sefields = functools.partial(fields, SeField)


def to_arg(f: SeField) -> SeField:
    f.parent = SeField(None, 'obj')
    return f


def render_astuple(cls: Type, custom: Custom = None) -> str:
    template = """
def {{func}}(obj):
  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  {% if cls|is_dataclass %}
  res = []
  {% for f in cls|fields -%}
  {% if not f.skip|default(False) %}
  res.append({{f|arg|rvalue()}})
  {% endif %}
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
    return env.get_template('iter').render(func=TO_ITER, cls=cls)


def render_asdict(cls: Type, case: Optional[str] = None, custom: Custom = None) -> str:
    template = """
def {{func}}(obj):
  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  {% if cls|is_dataclass %}
  res = {}
  {% for f in cls|fields -%}

  {% if not f.skip %}
    {% if f.skip_if %}
  if not {{f.skip_if.mangled}}({{f|arg|rvalue()}}):
    res["{{f|case}}"] = {{f|arg|rvalue()}}
    {% else %}
  res["{{f|case}}"] = {{f|arg|rvalue()}}
    {% endif %}
  {% endif %}

  {% endfor -%}
  return res
  {% endif %}
    """
    renderer = Renderer(TO_DICT, custom)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'fields': sefields})
    env.filters.update({'is_dataclass': is_dataclass})
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_arg})
    env.filters.update({'case': functools.partial(conv, case=case)})
    return env.get_template('dict').render(func=TO_DICT, cls=cls)


@dataclass
class Renderer:
    """
    Render rvalue for variouls types.
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
        'foo.__serde_to_iter__()'

        >>> Renderer(TO_ITER).render(SeField(List[Foo], 'foo'))
        '[v.__serde_to_iter__() for v in foo]'

        >>> Renderer(TO_ITER).render(SeField(Dict[str, Foo], 'foo'))
        '{k: v.__serde_to_iter__() for k, v in foo.items()}'

        >>> Renderer(TO_ITER).render(SeField(Dict[Foo, Foo], 'foo'))
        '{k.__serde_to_iter__(): v.__serde_to_iter__() for k, v in foo.items()}'

        >>> Renderer(TO_ITER).render(SeField(Tuple[str, Foo, int], 'foo'))
        '(foo[0], foo[1].__serde_to_iter__(), foo[2])'
        >>>
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
            return f'__custom_serializer__({arg.varname})'

    def dataclass(self, arg: SeField) -> str:
        """
        Render rvalue for dataclass.
        """
        return f'{arg.varname}.{self.func}()'

    def opt(self, arg: SeField) -> str:
        """
        Render rvalue for optional.
        """
        inner = arg[0]
        inner.name = arg.varname
        return f'{self.render(inner)} if {arg.varname} is not None else None'

    def list(self, arg: SeField) -> str:
        """
        Render rvalue for list.
        """
        earg = arg[0]
        earg.name = 'v'
        return f'[{self.render(earg)} for v in {arg.varname}]'

    def tuple(self, arg: SeField) -> str:
        """
        Render rvalue for tuple.
        """
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
        karg = arg[0]
        karg.name = 'k'
        varg = arg[1]
        varg.name = 'v'
        return f'{{{self.render(karg)}: {self.render(varg)} for k, v in {arg.varname}.items()}}'

    def primitive(self, arg: SeField) -> str:
        """
        Render rvalue for primitives.
        """
        return f'{arg.varname}'


def se_func(cls: Type[T], func: str, code: str, g: Dict = None, local: Dict = None) -> Type[T]:
    """
    Generate function to serialize into an object.
    """
    # Generate serialize function.
    if not g:
        g = globals().copy()
    if not local:
        local = locals().copy()
    code = gen(code, g, local, cls=cls)

    setattr(cls, func, local[func])
    if SETTINGS['debug']:
        hidden = getattr(cls, HIDDEN_NAME)
        hidden.code[func] = code

    return cls
