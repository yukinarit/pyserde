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
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import stringcase

from .compat import assert_type, is_dict, is_list, is_opt, is_tuple, is_union, typename, iter_types, type_args
from .core import (FROM_DICT, FROM_ITER, HIDDEN_NAME, SETTINGS, Hidden, SerdeError, T, gen, typecheck)

__all__ = ['deserialize', 'is_deserializable', 'Deserializer', 'from_obj', 'args_from_iter', 'args_from_dict']


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
        if not hasattr(cls, HIDDEN_NAME):
            setattr(cls, HIDDEN_NAME, Hidden())
        cls = de_func(cls, FROM_ITER, args_from_iter(cls))
        cls = de_func(cls, FROM_DICT, args_from_dict(cls, case=rename_all))
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
    ... class Hoge:
    ...     pass
    >>>
    >>> is_deserializable(Hoge)
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
    def deserialize(self, data, **opts):
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

    if strict:
        typecheck(c, v)

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


def to_case(s: str, case: Optional[str]) -> str:
    if case:
        f = getattr(stringcase, case, None)
        if not f:
            raise SerdeError(
                (f"Unkown case type: {case}. Pass the name of case " f"supported by 'stringcase' package.")
            )
        return f(s)
    else:
        return s


def args_from_iter(cls) -> str:
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
    >>> args_from_iter(Hoge)
    's=data[0], i=data[1], f=data[2], b=data[3]'
    >>>
    """
    params = []
    for i, f in enumerate(fields(cls)):
        arg = IterArg(f.type, f.name, 'data', index=i)
        params.append(f'{f.name}=' + de_value(arg))
    return ', '.join(params)


def args_from_dict(cls, case: str = None) -> str:
    """
    Similar to `args_from_iter` but from dict.

    >>> from dataclasses import dataclass
    >>> from serde import deserialize
    >>>
    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     s: str
    ...     i: List[int]
    ...     f: Optional[List[float]]
    ...     b: bool
    >>>
    >>> args_from_dict(Hoge)
    's=data["s"], i=[d for d in data["i"]], f=(data.get("f") and [d for d in data["f"]]), b=data["b"]'

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
        arg = DictArg(f.type, f.name, 'data', case=case)
        params.append(f'{f.name}=' + de_value(arg))
    return ', '.join(params)


@dataclass
class Arg:
    """
    Constructor argument for `deserialize` class.
    """

    type: Type  # Field type.
    field: str  # Field name.
    var: str  # Variable name.
    case: Optional[str] = None  # Case name.

    def __getitem__(self, n) -> 'Arg':
        typ = type_args(self.type)[n]
        if isinstance(self, IterArg):
            return IterArg(typ, self.field, self.var, case=self.case, index=self.index)
        else:
            return DictArg(typ, self.field, self.var, case=self.case)


@dataclass
class IterArg(Arg):
    """ Argument for Iterable like classes e.g. List """

    index: int = 0

    @property
    def varname(self) -> str:
        """
        Render variable name for Iterable like classes e.g. List.

        >>> IterArg(int, 'hoge', 'data', index=3).varname
        'data[3]'
        """
        return f'{self.var}[{self.index}]'


@dataclass
class DictArg(Arg):
    """ Argument for Dict like classes """

    @property
    def varname(self) -> str:
        """
        Render variable name for Dict like classes.

        >>> DictArg(int, 'hoge', 'data').varname
        'data["hoge"]'
        >>>
        >>> DictArg(int, 'hoge_foo', 'data', case='camelcase').varname
        'data["hogeFoo"]'
        >>>
        >>> DictArg(Optional[int], 'hoge', 'data').varname
        'data.get("hoge")'
        """
        if is_opt(self.type):
            return f'{self.var}.get("{to_case(self.field, self.case)}")'
        else:
            return f'{self.var}["{to_case(self.field, self.case)}"]'


def de_value(arg: Arg, varname: str = '') -> str:
    """
    Render string of args used in `de_func`.

    >>> @deserialize
    ... @dataclass
    ... class Hoge:
    ...     i: int
    >>>
    >>> de_value(DictArg(Hoge, 'hoge', 'data'))
    'from_obj(Hoge, data["hoge"])'
    >>>
    >>> de_value(DictArg(Optional[Hoge], 'hoge', 'data'))
    '(data.get("hoge") and from_obj(Hoge, data["hoge"]))'
    >>>
    >>> de_value(DictArg(List[int], 'hoge', 'data'))
    '[d for d in data["hoge"]]'
    >>>
    >>> de_value(DictArg(Optional[List[int]], 'hoge', 'data'))
    '(data.get("hoge") and [d for d in data["hoge"]])'
    >>>
    >>> de_value(DictArg(Tuple[int, str], 'hoge', 'data'))
    '(data["hoge"][0], data["hoge"][1], )'
    >>>
    >>> de_value(DictArg(Dict[str, int], 'hoge', 'data'))
    '{ k: v for k, v in data["hoge"].items() }'
    >>>
    >>> de_value(DictArg(int, 'hoge', 'data'))
    'data["hoge"]'
    >>>
    """
    typ = arg.type
    varname = varname or arg.varname

    if is_deserializable(typ):
        s = f"from_obj({typ.__name__}, {varname})"
    elif isinstance(typ, str):
        # When `typ` is of string, type name is specified as forward declaration.
        s = f"from_obj({typ}, {varname})"
    elif is_opt(typ):
        s = f"({varname} and {de_value(arg[0])})"
    elif is_union(typ):
        # TODO doesn't work with imported classes? (e.g. Union[str, xxxx.Package])
        # s = f"from_obj(Union[{','.join([t.__qualname__ for t in type_args(typ)])}], {varname})"
        s = f"from_obj({typename(typ)}, {varname})"
    elif is_list(typ):
        s = f"[{de_value(arg[0], 'd')} for d in {varname}]"
    elif is_tuple(typ):
        values = [de_value(arg[i], varname + f'[{i}]') + ', ' for i, _ in enumerate(type_args(typ))]
        s = f"({''.join(values)})"
    elif is_dict(typ):
        s = f"{{ {de_value(arg[0], 'k')}: {de_value(arg[1], 'v')} " f"for k, v in {varname}.items() }}"
    else:
        s = varname
    return s


def de_func(cls: Type[T], funcname: str, params: str) -> Type[T]:
    """
    Generate function to deserialize into an instance of `deserialize` class.
    """
    body = f'def {funcname}(data):\n' f'  return cls({params})'

    # Collect types to be used in the `exec` scope.
    g: Dict[str, Any] = globals().copy()
    for typ in iter_types(cls):
        if is_dataclass(typ):
            g[typ.__name__] = typ
    g['cls'] = cls
    g['from_obj'] = from_obj
    import typing

    g['typing'] = typing
    g['NoneType'] = type(None)

    # Generate deserialize function.
    code = gen(body, g, cls=cls)
    setattr(cls, funcname, staticmethod(g[funcname]))
    if SETTINGS['debug']:
        hidden = getattr(cls, HIDDEN_NAME)
        hidden.code[funcname] = code

    return cls
