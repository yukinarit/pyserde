"""
Defines classess and functions for `serialize` decorator.

"""
import abc
import copy
import functools
from dataclasses import Field as DataclassField
from dataclasses import asdict as _asdict
from dataclasses import astuple as _astuple
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Type

import jinja2
import stringcase

from .compat import is_dict, is_list, is_tuple, type_args
from .core import HIDDEN_NAME, SE_NAME, SETTINGS, TO_DICT, TO_ITER, Hidden, T, gen
from .de import Arg


class Serializer(metaclass=abc.ABCMeta):
    """
    `Serializer` base class. Subclass this to custonize serialize bahaviour.

    See `serde.json.JsonSerializer` and `serde.msgpack.MsgPackSerializer` for example usage.
    """

    @abc.abstractclassmethod
    def serialize(self, obj):
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
    ... class Hoge:
    ...     i: int
    ...     s: str
    ...     f: float
    ...     b: bool
    >>>
    >>> to_json(Hoge(i=10, s='hoge', f=100.0, b=True))
    '{"i": 10, "s": "hoge", "f": 100.0, "b": true}'
    >>>

    Additionally, `serialize` supports case conversion. Pass case name in
    `serialize` decorator as shown below.

    >>> @serialize(rename_all = 'camelcase')
    ... @dataclass
    ... class Hoge:
    ...     int_field: int
    ...     str_field: str
    >>>
    >>> to_json(Hoge(int_field=10, str_field='hoge'))
    '{"intField": 10, "strField": "hoge"}'
    >>>
    """

    @functools.wraps(_cls)
    def wrap(cls: Type[T]) -> Type[T]:
        if not hasattr(cls, HIDDEN_NAME):
            setattr(cls, HIDDEN_NAME, Hidden())

        def serialize(self, ser, **opts) -> None:
            return ser().serialize(self, **opts)

        setattr(cls, SE_NAME, serialize)
        cls = se_func(cls, TO_ITER, render_astuple(cls))
        cls = se_func(cls, TO_DICT, render_asdict(cls, rename_all))
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
    ... class Hoge:
    ...     pass
    >>>
    >>> is_serializable(Hoge)
    True
    >>>
    """
    return hasattr(instance_or_class, '__serde_serialize__')


def to_dict(o) -> Dict:
    """
    Convert object into dictionary.

    >>> @serialize
    ... @dataclass
    ... class Hoge:
    ...     i: int
    >>>
    >>> to_dict(Hoge(10))
    {'i': 10}
    >>>
    >>> to_dict([Hoge(10), Hoge(20)])
    [{'i': 10}, {'i': 20}]
    >>>
    >>> to_dict({'a': Hoge(10), 'b': Hoge(20)})
    {'a': {'i': 10}, 'b': {'i': 20}}
    >>>
    >>> to_dict((Hoge(10), Hoge(20)))
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
    else:
        return _asdict(v)


@dataclass
class Field:
    """
    Field in pyserde class.
    """

    type: Type
    name: str
    parent: Optional['Field'] = None
    case: Optional[str] = None

    @staticmethod
    def from_dataclass(f: DataclassField) -> '':
        return Field(f.type, f.name)

    @property
    def varname(self) -> str:
        var = self.parent.varname if self.parent else None
        if var:
            return f'{var}.{self.name}'
        else:
            return self.name

    def __getitem__(self, n) -> 'Field':
        typ = type_args(self.type)[n]
        return Field(typ, None)


def to_arg(f: DataclassField, case: Optional[str] = None) -> Field:
    ident = Field.from_dataclass(f)
    ident.parent = Field(None, 'obj')
    ident.case = case
    return ident


def render_astuple(cls: Type) -> str:
    template = '''
def {{funcname}}(obj):
  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  {% if cls|is_dataclass %}
  res = []
  {% for f in cls|fields -%}
  res.append({{f|arg|rvalue()}})
  {% endfor -%}
  return tuple(res)
  {% endif %}
    '''

    renderer = Renderer(TO_ITER)
    env = jinja2.Environment(loader=jinja2.DictLoader({'iter': template}))
    env.filters.update({'fields': fields})
    env.filters.update({'is_dataclass': is_dataclass})
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_arg})
    return env.get_template('iter').render(funcname=TO_ITER, cls=cls)


def render_asdict(cls: Type, case: Optional[str] = None) -> str:
    template = '''
def {{funcname}}(obj):
  if not is_dataclass(obj):
    return copy.deepcopy(obj)

  {% if cls|is_dataclass %}
  res = {}
  {% for f in cls|fields -%}
  res["{{f.name|case}}"] = {{f|arg|rvalue()}}
  {% endfor -%}
  return res
  {% endif %}
    '''

    renderer = Renderer(TO_DICT)
    env = jinja2.Environment(loader=jinja2.DictLoader({'dict': template}))
    env.filters.update({'fields': fields})
    env.filters.update({'is_dataclass': is_dataclass})
    env.filters.update({'rvalue': renderer.render})
    env.filters.update({'arg': to_arg})
    env.filters.update({'case': getattr(stringcase, case or '', lambda s: s)})
    return env.get_template('dict').render(funcname=TO_DICT, cls=cls)


@dataclass
class Renderer:
    """
    Render rvalue for variouls types.
    """

    func: str

    def render(self, arg: Field) -> str:
        """
        Render rvalue

        >>> Renderer(TO_ITER).render(Field(int, 'i'))
        'i'

        >>> Renderer(TO_ITER).render(Field(List[int], 'l'))
        '[v for v in l]'

        >>> @serialize
        ... @dataclass(unsafe_hash=True)
        ... class Hoge:
        ...    val: int
        >>> Renderer(TO_ITER).render(Field(Hoge, 'hoge'))
        'hoge.__serde_to_iter__()'

        >>> Renderer(TO_ITER).render(Field(List[Hoge], 'hoge'))
        '[v.__serde_to_iter__() for v in hoge]'

        >>> Renderer(TO_ITER).render(Field(Dict[str, Hoge], 'hoge'))
        '{k: v.__serde_to_iter__() for k, v in hoge.items()}'

        >>> Renderer(TO_ITER).render(Field(Dict[Hoge, Hoge], 'hoge'))
        '{k.__serde_to_iter__(): v.__serde_to_iter__() for k, v in hoge.items()}'

        >>> Renderer(TO_ITER).render(Field(Tuple[str, Hoge, int], 'hoge'))
        '(hoge[0], hoge[1].__serde_to_iter__(), hoge[2])'
        >>>
        """
        if is_dataclass(arg.type):
            return self.dataclass(arg)
        elif is_list(arg.type):
            return self.list(arg)
        elif is_dict(arg.type):
            return self.dict(arg)
        elif is_tuple(arg.type):
            return self.tuple(arg)
        else:
            return self.primitive(arg)

    def dataclass(self, arg: Field) -> str:
        return f'{arg.varname}.{self.func}()'

    def list(self, arg: Field) -> str:
        earg = arg[0]
        earg.name = 'v'
        return f'[{self.render(earg)} for v in {arg.varname}]'

    def tuple(self, arg: Field) -> str:
        rvalues = []
        for i, _ in enumerate(type_args(arg.type)):
            r = arg[i]
            r.name = f'{arg.varname}[{i}]'
            rvalues.append(self.render(r))
        return f"({', '.join(rvalues)})"

    def dict(self, arg: Field) -> str:
        karg = arg[0]
        karg.name = 'k'
        varg = arg[1]
        varg.name = 'v'
        return f'{{{self.render(karg)}: {self.render(varg)} for k, v in {arg.varname}.items()}}'

    def primitive(self, arg: Field) -> str:
        return f'{arg.varname}'


def se_func(cls: Type[T], func: str, code: str) -> Type[T]:
    """
    Generate function to serialize into an object.
    """
    g: Dict[str, Any] = globals().copy()

    # Generate serialize function.
    code = gen(code, g, cls=cls)

    setattr(cls, func, g[func])
    if SETTINGS['debug']:
        hidden = getattr(cls, HIDDEN_NAME)
        hidden.code[func] = code

    return cls
