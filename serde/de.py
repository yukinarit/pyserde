"""
Defines classess and functions for `deserialize` decorator.

`deserialize` is a decorator to make a `dataclasses.dataclass` class deserializable.
`is_deserializable` is used to test a class is with `deserialize`.
`Deserializer` is a deserializer base class used in `from_obj`,
`serde.json.from_json`. You can subclass it to make your own deserializer.
`from_obj` deserializes from an object into an instance of the class with
`deserialize`.

`args_from_seq` and `args_from_dict` are private functions but they are the core
parts of pyserde.
"""
import abc
import dataclasses # noqa
import enum
import stringcase
from typing import Any, Dict, Tuple, List, Type, Optional
from dataclasses import fields, is_dataclass

from .core import SerdeError, FROM_DICT, FROM_TUPLE, T, gen, iter_types, type_args
from .compat import is_opt, is_list, is_tuple, is_dict

__all__ = [
    'deserialize',
    'is_deserializable',
    'Deserializer',
    'from_obj',
    'args_from_seq',
    'args_from_dict',
]


def deserialize(_cls=None, rename_all: Optional[str] = None) -> Type:
    """
    `deserialize` decorator. A dataclass with this decorator can be deserialized
    into an object from various data format such as JSON and MsgPack.

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>> from serde.json import from_json
    >>>
    >>> # Mark the class deserializable.
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     i: int
    ...     s: str
    ...     f: float
    ...     b: bool
    >>>
    >>> from_json(Hoge, '{"i": 10, "s": "hoge", "f": 100.0, "b": true}')
    Hoge(i=10, s='hoge', f=100.0, b=True)

    Additionally, `deserialize` supports case conversion. Pass case name in
    `deserialize` decorator as shown below.

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize(rename_all = 'camelcase')
    ... @dataclass
    ... class Hoge:
    ...     int_field: int
    ...     str_field: str
    >>>
    >>> from_json(Hoge, '{"intField": 10, "strField": "hoge"}')
    Hoge(int_field=10, str_field='hoge')
    >>>
    """
    def wrap(cls) -> Type:
        cls = de_func(cls, FROM_TUPLE, args_from_seq(cls))
        cls = de_func(cls, FROM_DICT, args_from_dict(cls, case=rename_all))
        return cls

    if _cls is None:
        return wrap

    return wrap(_cls)


def is_deserializable(instance_or_class: Any) -> bool:
    """
    Test if arg can `deserialize`. Arg must be either an instance of class.

    >>> from dataclasses import dataclass
    >>> from serde import deserialize, is_deserializable
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     pass
    >>>
    >>> is_deserializable(Hoge)
    True
    >>>
    """
    return hasattr(instance_or_class, FROM_TUPLE) or hasattr(instance_or_class, FROM_DICT)


class Deserializer(metaclass=abc.ABCMeta):
    """
    `Deserializer` base class. Subclass this to custonize deserialize bahaviour.

    See `serde.json.JsonDeserializer` and `serde.msgpack.MsgPackDeserializer` for example usage.
    """
    @abc.abstractclassmethod
    def deserialize(self, data, **opts):
        """
        deserialize `data` into an object typically `dict`, `list` or `tuple`.

        For example, `serde.json.JsonDeserializer` takes json string and deserialize
        into an object. `serde.msgpack.MsgPackDeserializer` takes msgpack bytes and
        deserialize into an object.
        """


def from_obj(c: Type[T], o: Any, de: Type[Deserializer] = None, **opts):
    """
    Deserialize from an object into an instance of the type specified as arg `c`. `c` can be either primitive type, `List`, `Tuple`, `Dict` or `deserialize` class.

    ### Dataclass

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     i: int
    ...     f: float
    ...     s: str
    ...     b: bool
    >>>
    >>> obj = {'i': 10, 'f': 0.1, 's': 'hoge', 'b': False}
    >>> from_obj(Hoge, obj)
    Hoge(i=10, f=0.1, s='hoge', b=False)

    ### Containers

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     s: str
    ...     i: int
    >>>
    >>> from_obj(List[Hoge], [('hoge', 10), ('foo', 20)])
    [Hoge(s='hoge', i=10), Hoge(s='foo', i=20)]
    >>>
    >>> from_obj(Dict[str ,Hoge], {'hoge': ('hoge', 10), 'foo': ('foo', 20)})
    {'hoge': Hoge(s='hoge', i=10), 'foo': Hoge(s='foo', i=20)}
    >>>
    """
    if de:
        o = de().deserialize(o, **opts)
    if o is None:
        return None
    if is_deserializable(c):
        return from_dict_or_tuple(c, o)
    elif is_opt(c):
        return from_obj(type_args(c)[0], o)
    elif is_list(c):
        return [from_obj(type_args(c)[0], e) for e in o]
    elif is_tuple(c):
        return tuple(from_obj(type_args(c)[i], e) for i, e in enumerate(o))
    elif is_dict(c):
        return {from_obj(type_args(c)[0], k): from_obj(type_args(c)[1], v) for k, v in o.items()}
    else:
        return o


def from_dict_or_tuple(cls, o):
    """
    Deserialize into an instance of `deserialize` class from either `dict` or `tuple`.
    """
    if not is_deserializable(cls):
        raise SerdeError('`cls` must be deserializable.')

    if isinstance(o, (List, Tuple)):
        return cls.__serde_from_tuple__(o)
    elif isinstance(o, Dict):
        return cls.__serde_from_dict__(o)
    elif isinstance(o, cls) or o is None:
        return o
    else:
        raise SerdeError(f'Arg must be either List, Tuple, Dict or Type but {type(o)}.')


def to_case(s: str, case: Optional[str]) -> str:
    if case:
        f = getattr(stringcase, case, None)
        if not f:
            raise SerdeError((f"Unkown case type: {case}. Pass the name of case "
                              f"supported by 'stringcase' package."))
        return f(s)
    else:
        return s


def args_from_seq(cls) -> str:
    """
    Create string of ctor args for sequence type such as Tuple or List.
    The returned string will be used in `deserialize` decorator to
    generate the deserialize function.

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     s: str
    ...     i: int
    ...     f: float
    ...     b: bool
    >>>
    >>> args_from_seq(Hoge)
    's=data[0], i=data[1], f=data[2], b=data[3]'
    >>>
    """
    params = []
    for i, f in enumerate(fields(cls)):
        params.append(f'{f.name}=' + de_value(f.type, f'data[{i}]'))
    return ', '.join(params)


def args_from_dict(cls, case: str=None) -> str:
    """
    Similar to `args_from_seq` but from dict.

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     s: str
    ...     i: int
    ...     f: float
    ...     b: bool
    >>>
    >>> args_from_dict(Hoge)
    's=data["s"], i=data["i"], f=data["f"], b=data["b"]'

    `case` enables string case conversion e.g. snake_case to camelCase.
    `case` must be one of 'camelcase', 'capitalcase', 'constcase', 'lowercase',
    'pascalcase', 'snakecase', 'uppercase'.

    For more information on the case conversion, see python [stringcase](https://pypi.org/project/stringcase/) package.

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     str_field: str
    >>>
    >>> args_from_dict(Hoge)
    'str_field=data["str_field"]'
    >>> args_from_dict(Hoge, case='camelcase')
    'str_field=data["strField"]'
    >>> args_from_dict(Hoge, case='pascalcase')
    'str_field=data["StrField"]'
    >>>
    """
    params = []
    for f in fields(cls):
        params.append(f'{f.name}=' + de_value(f.type, f'data["{to_case(f.name, case)}"]'))
    return ', '.join(params)


def de_value(typ: Type, varname: str) -> str:
    """
    Create string of args to be used to `de_func`.
    """

    if is_deserializable(typ):
        nested = f'{typ.__name__}'
        s = f"from_dict_or_tuple({nested}, {varname})"
    elif isinstance(typ, str):
        # When `typ` is of string, type name is specified as forward declaration.
        s = f"from_dict_or_tuple({typ}, {varname})"
    elif is_opt(typ):
        element_typ = type_args(typ)[0]
        s = f"{de_value(element_typ, varname)}"
    elif is_list(typ):
        element_typ = type_args(typ)[0]
        s = f"[{de_value(element_typ, 'd')} for d in {varname}]"
    elif is_dict(typ):
        key_typ = type_args(typ)[0]
        value_typ = type_args(typ)[1]
        s = (f"{{ {de_value(key_typ, 'k')}: {de_value(value_typ, 'v')} "
             f"for k, v in {varname}.items() }}")
    elif is_tuple(typ):
        elements = [de_value(arg, varname + f'[{i}]') + ', ' for i, arg in enumerate(type_args(typ))]
        s = f"({''.join(elements)})"
    else:
        s = varname
    return s


def de_func(cls: Type[T], funcname: str, params: str) -> Type[T]:
    """
    Generate function to deserialize into an instance of `deserialize` class.
    """
    body = f'def {funcname}(data):\n return cls({params})'

    # Collect types to be used in the `exec` scope.
    globals: Dict[str, Any] = dict(cls=cls)
    for typ in iter_types(cls):
        if is_dataclass(typ):
            globals[typ.__name__] = typ
    globals['from_dict_or_tuple'] = from_dict_or_tuple

    # Generate deserialize function.
    gen(body, globals)
    setattr(cls, funcname, staticmethod(globals[funcname]))

    return cls
