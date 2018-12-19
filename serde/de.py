from typing import Type, Any, Dict
from dataclasses import fields, is_dataclass

from .core import T, FROM_TUPLE, FROM_DICT, gen


def param_from_tuple(cls) -> str:
    """
    Generate parameters for deserialize function.
    """
    # If a member is also pyserde class, invoke the deserialize
    # function on its own.
    params = []
    for i, f in enumerate(fields(cls)):
        if is_deserializable(f.type):
            nested = f'{f.type.__name__}'
            params.append(f"{f.name}={nested}.{FROM_TUPLE}(data[{i}])")
        else:
            params.append(f"{f.name}=data[{i}]")
    return ', '.join(params)


def param_from_dict(cls) -> str:
    # If a member is also pyserde class, invoke the deserialize
    # function on its own.
    params = []
    for f in fields(cls):
        if is_deserializable(f.type):
            nested = f'{f.type.__name__}'
            params.append(f"{f.name}={nested}.{FROM_DICT}(data['{f.name}'])")
        else:
            params.append(f"{f.name}=data['{f.name}']")
    return ', '.join(params)


def gen_from_any(cls: Type[T], name, params) -> Type[T]:
    """
    Generate function to deserialize from tuple.
    """
    body = (f'def {name}(data):\n'
            f' return cls({params})')

    globals: Dict[str, Any] = dict(cls=cls)

    # Collect fields to used in exec scope.
    for f in fields(cls):
        if is_dataclass(f.type):
            globals[f.type.__name__] = f.type

    gen(body, globals, echo=False)
    if name in globals:
        pass
    setattr(cls, name, staticmethod(globals[name]))

    return cls


def is_deserializable(instance_or_class: Any) -> bool:
    """
    Test if `instance_or_class` is deserializable.
    """
    return hasattr(instance_or_class, FROM_TUPLE)


class Deserializer:
    """
    Deserializer base class.
    """
    def deserialize(self, obj: Any) -> Dict[str, Any]:
        pass


def deserialize(_cls=None, rename_all: bool=False) -> Type:
    """
    `deserialize` decorator. A dataclass with this decorator can be
    deserialized into an object from various data interchange format
    such as JSON and MsgPack.
    """
    def wrap(cls) -> Type:
        cls = gen_from_any(cls, FROM_TUPLE, param_from_tuple(cls))
        cls = gen_from_any(cls, FROM_DICT, param_from_dict(cls))
        return cls

    if _cls is None:
        wrap

    return wrap(_cls)
