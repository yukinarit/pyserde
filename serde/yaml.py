"""
Serialize and Deserialize in YAML format. This module depends on
[pyyaml](https://pypi.org/project/PyYAML/) package.
"""

from typing import Any, overload

import yaml

from .compat import SerdeError, T
from .de import Deserializer, from_dict
from .se import Serializer, to_dict

__all__ = ["from_yaml", "to_yaml", "deserialize_yaml_numbers"]


class YamlSerializer(Serializer[str]):
    @classmethod
    def serialize(cls, obj: Any, **opts: Any) -> str:
        return yaml.safe_dump(obj, **opts)  # type: ignore


class YamlDeserializer(Deserializer[str]):
    @classmethod
    def deserialize(cls, data: str, **opts: Any) -> Any:
        return yaml.safe_load(data, **opts)


def deserialize_yaml_numbers(value: Any) -> float:
    """
    Convert YAML numbers to float, accepting ints/floats and numeric strings (e.g. scientific
    notation). Rejects booleans and non-numeric inputs.
    """
    if isinstance(value, bool):
        raise SerdeError(f"Expected YAML number but got boolean {value!r}")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError as e:
            raise SerdeError(f"Could not convert YAML number string {value!r} to float") from e
    raise SerdeError(f"Expected YAML number but got {type(value).__name__}")


def to_yaml(
    obj: Any,
    cls: Any | None = None,
    se: type[Serializer[str]] = YamlSerializer,
    reuse_instances: bool = False,
    convert_sets: bool = True,
    skip_none: bool = False,
    **opts: Any,
) -> str:
    """
    Serialize the object into YAML.

    You can pass any serializable `obj`. If you supply keyword arguments other than `se`,
    they will be passed in `yaml.safe_dump` function.

    * `skip_none`: When set to True, any field in the class with a None value is excluded from the
    serialized output. Defaults to False.

    If you want to use the other yaml package, you can subclass `YamlSerializer` and implement
    your own logic.
    """
    return se.serialize(
        to_dict(
            obj,
            c=cls,
            reuse_instances=reuse_instances,
            convert_sets=convert_sets,
            skip_none=skip_none,
        ),
        **opts,
    )


@overload
def from_yaml(
    c: type[T],
    s: str,
    de: type[Deserializer[str]] = YamlDeserializer,
    coerce_numbers: bool = True,
    **opts: Any,
) -> T: ...


# For Union, Optional etc.
@overload
def from_yaml(
    c: Any,
    s: str,
    de: type[Deserializer[str]] = YamlDeserializer,
    coerce_numbers: bool = True,
    **opts: Any,
) -> Any: ...


def from_yaml(
    c: Any,
    s: str,
    de: type[Deserializer[str]] = YamlDeserializer,
    coerce_numbers: bool = True,
    **opts: Any,
) -> Any:
    """
    `c` is a class object and `s` is YAML string. If you supply keyword arguments other than `de`,
    they will be passed in `yaml.safe_load` function.

    * `coerce_numbers`: When True (default), numeric YAML scalars or numeric strings (e.g.
      "1e-3") are coerced to floats when the target type is float. Booleans are rejected.

    If you want to use the other yaml package, you can subclass `YamlDeserializer` and implement
    your own logic.
    """
    deserialize_numbers = deserialize_yaml_numbers if coerce_numbers else None
    return from_dict(
        c,
        de.deserialize(s, **opts),
        reuse_instances=False,
        deserialize_numbers=deserialize_numbers,
    )
