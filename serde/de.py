from typing import Type, Any, Dict
from dataclasses import fields, Field, is_dataclass

from .core import T, DE_NAME, gen


def gen_de_params(idx: int, f: Field) -> str:
    """
    Generate parameters for deserialize function.
    """
    # If a member is also pyserde class, invoke the deserialize
    # function on its own.
    if is_deserializable(f.type):
        nested = f'{f.type.__name__}'
        return f"{f.name}={nested}.{DE_NAME}(tpl[{idx}])"
    else:
        return f"{f.name}=tpl[{idx}]"


def gen_de(cls: Type[T]) -> Type[T]:
    """
    Generate deserialize function by exec.
    """
    params = ', '.join([gen_de_params(i, f)
                        for i, f in enumerate(fields(cls))])
    body = (f'def {DE_NAME}(tpl):\n'
            f' return cls({params})')

    globals: Dict[str, Any] = dict(cls=cls)

    # Collect fields to used in exec scope.
    for f in fields(cls):
        if is_dataclass(f.type):
            globals[f.type.__name__] = f.type

    gen(body, globals, echo=True)
    if DE_NAME in globals:
        pass
    setattr(cls, DE_NAME, staticmethod(globals[DE_NAME]))

    return cls


def is_deserializable(instance_or_class: Any) -> bool:
    """
    Test if `instance_or_class` is deserializable.
    """
    return hasattr(instance_or_class, DE_NAME)


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
        return gen_de(cls)

    if _cls is None:
        wrap

    return wrap(_cls)
