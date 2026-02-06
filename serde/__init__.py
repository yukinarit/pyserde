from dataclasses import dataclass
from collections.abc import Callable
from typing import Any, Type, overload

from typing_extensions import dataclass_transform

from .compat import SerdeError, SerdeSkip, T
from .core import (
    ClassSerializer,
    ClassDeserializer,
    AdjacentTagging,
    coerce,
    DefaultTagging,
    ExternalTagging,
    InternalTagging,
    disabled,
    strict,
    Tagging,
    TypeCheck,
    Untagged,
    field,
    init,
    logger,
    should_impl_dataclass,
    add_serializer,
    add_deserializer,
)
from .de import (
    DeserializeFunc,
    default_deserializer,
    deserialize,
    from_dict,
    from_tuple,
    is_deserializable,
)
from .se import (
    SerializeFunc,
    asdict,
    astuple,
    default_serializer,
    is_serializable,
    serialize,
    to_dict,
    to_tuple,
)

__all__ = [
    "serde",
    "serialize",
    "deserialize",
    "is_serializable",
    "is_deserializable",
    "to_dict",
    "from_dict",
    "to_tuple",
    "from_tuple",
    "SerdeError",
    "SerdeSkip",
    "AdjacentTagging",
    "ExternalTagging",
    "InternalTagging",
    "Untagged",
    "disabled",
    "strict",
    "coerce",
    "field",
    "asdict",
    "astuple",
    "compat",
    "init",
    "logger",
    "inspect",
    "json",
    "msgpack",
    "numpy",
    "toml",
    "pickle",
    "yaml",
    "ClassSerializer",
    "ClassDeserializer",
    "add_serializer",
    "add_deserializer",
    "default_serializer",
    "default_deserializer",
]


@overload
def serde(
    _cls: Type[T],
    rename_all: str | None = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    skip_if_default: bool = False,
    skip_if_none: bool = False,
    transparent: bool = False,
    serializer: SerializeFunc | None = None,
    deserializer: DeserializeFunc | None = None,
    tagging: Tagging = DefaultTagging,
    type_check: TypeCheck = strict,
    serialize_class_var: bool = False,
    class_serializer: ClassSerializer | None = None,
    class_deserializer: ClassDeserializer | None = None,
    deny_unknown_fields: bool = False,
) -> Type[T]: ...


@overload
def serde(
    _cls: Any = None,
    rename_all: str | None = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    skip_if_default: bool = False,
    skip_if_none: bool = False,
    transparent: bool = False,
    serializer: SerializeFunc | None = None,
    deserializer: DeserializeFunc | None = None,
    tagging: Tagging = DefaultTagging,
    type_check: TypeCheck = strict,
    serialize_class_var: bool = False,
    class_serializer: ClassSerializer | None = None,
    class_deserializer: ClassDeserializer | None = None,
    deny_unknown_fields: bool = False,
) -> Callable[[type[T]], type[T]]: ...


@dataclass_transform(field_specifiers=(field,))
def serde(
    _cls: Any = None,
    rename_all: str | None = None,
    reuse_instances_default: bool = True,
    convert_sets_default: bool = False,
    skip_if_default: bool = False,
    skip_if_none: bool = False,
    transparent: bool = False,
    serializer: SerializeFunc | None = None,
    deserializer: DeserializeFunc | None = None,
    tagging: Tagging = DefaultTagging,
    type_check: TypeCheck = strict,
    serialize_class_var: bool = False,
    class_serializer: ClassSerializer | None = None,
    class_deserializer: ClassDeserializer | None = None,
    deny_unknown_fields: bool = False,
) -> Any:
    """
    serde decorator. Keyword arguments are passed in `serialize` and `deserialize`.
    """

    def wrap(cls: Any) -> Any:
        if should_impl_dataclass(cls):
            dataclass(cls)
        serialize(
            cls,
            rename_all=rename_all,
            reuse_instances_default=reuse_instances_default,
            convert_sets_default=convert_sets_default,
            skip_if_default=skip_if_default,
            skip_if_none=skip_if_none,
            transparent=transparent,
            serializer=serializer,
            deserializer=deserializer,
            tagging=tagging,
            type_check=type_check,
            serialize_class_var=serialize_class_var,
            class_serializer=class_serializer,
        )
        deserialize(
            cls,
            rename_all=rename_all,
            reuse_instances_default=reuse_instances_default,
            convert_sets_default=convert_sets_default,
            skip_if_default=skip_if_default,
            skip_if_none=skip_if_none,
            transparent=transparent,
            serializer=serializer,
            deserializer=deserializer,
            tagging=tagging,
            type_check=type_check,
            serialize_class_var=serialize_class_var,
            class_deserializer=class_deserializer,
            deny_unknown_fields=deny_unknown_fields,
        )
        return cls

    if _cls is None:
        return wrap

    return wrap(_cls)
